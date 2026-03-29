import json
import pickle
import re
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    from src.rag.retriever import MedicalRetriever
    from src.tools.tools import TOOL_SCHEMAS, TOOL_DISPATCH, _doctors
except ImportError:
    from rag.retriever import MedicalRetriever
    from tools.tools import TOOL_SCHEMAS, TOOL_DISPATCH, _doctors

INDEX_DIR = Path(__file__).resolve().parents[1] / "data" / "processed" / "faiss_index"
TEXTS_MAP: dict = {}


_SENTINEL_RE = re.compile(r"<!--doc:(?P<id>dr_\d{3})-->")

_SKIP_RAG_RE = re.compile(
    r"\b0[0-9]{9}\b"
    r"|\bтелефон\b|\bтел\.?\b"
    r"|\bказвам се\b|\bимена(та)? (са|ми)\b"
    r"|\bустройва ме\b|\bпотвърж?д\w*\b|\bда, запиши\b"
    r"|\bпри него\b|\bпри нея\b|\bтози лекар\b|\bтази лекарка\b"
    r"|\bсвободни? часове?\b|\bза кога\b|\bкога има\b"
    r"|\bв (сряда|понеделник|вторник|четвъртък|петък|събота)\b"
    r"|\b\d{1,2}\.\d{1,2}\.\d{4}\b|\b\d{4}-\d{2}-\d{2}\b"
    r"|\b\d{1,2}:\d{2}\b"
    r"|\b(запиши|запишете|запиш) ме\b|\bхайде\b|\bизбирам\b|\bнека да е\b"
    r"|\bdr_\d{3}\b",
    re.IGNORECASE,
)

_CONFIRM_RE = re.compile(
    r"успешно записан|референтен номер|MC-[A-Z0-9]{4,8}",
    re.IGNORECASE,
)

_SYSTEM_PROMPT = """\
Ти си AI асистент ЕДИНСТВЕНО на Медицински Център "Здраве Плюс", София.
Днешната дата е {today}.{doctor_note}
 
ОБХВАТ — отговаряш САМО на въпроси свързани с:
- симптоми и насочване към специалист
- лекари, специалности и цени в центъра
- свободни часове и записване на час
- работно време, адрес, контакти на центъра
- НЗОК покритие
 
При всякакви ДРУГИ теми (политика, технологии, история, готвене и т.н.) отговаряй точно:
"Аз съм асистент на Медицински Център Здраве Плюс и мога да помогна само с медицински въпроси и записване на часове. За друго, моля обърнете се към подходящ източник."
 
ПРАВИЛА ЗА ИНСТРУМЕНТИ:
1. Задължителен ред: search_doctors → check_availability → book_appointment
2. ВИНАГИ извиквай search_doctors първо за да получиш верния doctor_id — никога не предполагай или измисляй doctor_id.
3. Използвай САМО doctor_id от резултата на search_doctors — полето "id" в обекта на лекаря.
4. Никога не извиквай check_availability без doctor_id взет от search_doctors в СЪЩИЯ разговор.
5. Показвай САМО часове върнати от check_availability като available=true.
6. Преди book_appointment вземи три имена и телефон от пациента.
7. Никога не потвърждавай записване без реален успешен резултат от book_appointment.
8. При нова специалност → задължително извикай search_doctors отново.
 
ВАЛУТА: Всички цени са в евро (€). Винаги показвай цените с "евро" или "€" - никога "лева" или "лв".
 
ОБЩИ ПРАВИЛА:
- Отговаряй само на български, топло и разбиращо
- Не поставяй диагнози — само насочвай към специалист
- При спешни симптоми (гръдна болка, загуба на съзнание, инсулт, парализа) → 112
 
Адрес: бул. Васил Левски 47, София | Тел: 02 800 12 34
Работно време: Пон–Пет 08:00–19:00, Събота 09:00–14:00\
"""

_DOCTOR_NOTE = (
    "\n\nАКТИВЕН ЛЕКАР: {name} ({specialty}, doctor_id={doc_id})."
    " Ползвай САМО този doctor_id за check_availability и book_appointment."
    " За друга специалност → search_doctors първо."
)


def _content_as_str(content) -> str:
    """Normalize OpenAI message content — can be str, list of parts, or None."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content)


def _active_doctor_from_history(history: list[dict]) -> tuple[str, dict] | tuple[None, None]:
    """
    Returns (doctor_id, doctor) for the most recent doctor confirmed by a tool result.
    Priority: top-level "doctor_id" in tool messages (check_availability /
    book_appointment) — iterates chronologically so the latest always wins.
    Fallback: sentinel tag we embed in assistant messages.
    """
    last_id: str | None = None
    for msg in history:
        if msg.get("role") != "tool":
            continue
        try:
            if doc_id := json.loads(_content_as_str(msg.get("content"))).get("doctor_id"):
                if doc_id in _doctors:
                    last_id = doc_id
        except (json.JSONDecodeError, TypeError):
            pass

    if last_id:
        return last_id, _doctors[last_id]

    for msg in reversed(history):
        if msg.get("role") != "assistant":
            continue
        if m := _SENTINEL_RE.search(_content_as_str(msg.get("content"))):
            if (doc_id := m.group("id")) in _doctors:
                return doc_id, _doctors[doc_id]

    return None, None


def _doctor_from_turn(tool_msgs: list[dict]) -> str | None:
    """Most recent doctor_id confirmed in the current turn's tool results."""
    last_id: str | None = None
    for msg in tool_msgs:
        try:
            if doc_id := json.loads(_content_as_str(msg.get("content"))).get("doctor_id"):
                if doc_id in _doctors:
                    last_id = doc_id
        except (json.JSONDecodeError, TypeError):
            pass
    return last_id


def _booked_this_turn(tool_msgs: list[dict]) -> bool:
    """True only when a successful book_appointment result exists in this turn."""
    return any(
        '"success": true' in _content_as_str(m.get("content"))
        and '"reference"' in _content_as_str(m.get("content"))
        for m in tool_msgs
    )


class MedicalAgent:
    def __init__(self, index_dir: Path = INDEX_DIR):
        self.client = OpenAI()
        self.retriever = MedicalRetriever(index_dir=index_dir)
        texts_path = index_dir / "texts.pkl"
        if texts_path.exists():
            global TEXTS_MAP
            with open(texts_path, "rb") as f:
                TEXTS_MAP = pickle.load(f)

    def _system_prompt(self, history: list[dict]) -> str:
        doc_id, doctor = _active_doctor_from_history(history)
        doctor_note = (
            _DOCTOR_NOTE.format(
                name=doctor["name"], specialty=doctor["specialty"], doc_id=doc_id,
            )
            if doctor else ""
        )
        return _SYSTEM_PROMPT.format(
            today=datetime.today().strftime("%d.%m.%Y (%A)"),
            doctor_note=doctor_note,
        )

    def _rag_context(self, message: str) -> str:
        if _SKIP_RAG_RE.search(message) or not TEXTS_MAP:
            return ""
        try:
            results = self.retriever.search(message, top_k=4, rewrite=True, rerank=True)
            parts = [TEXTS_MAP[r["id"]] for r in results if r["id"] in TEXTS_MAP]
            return "\n\n---\n\n".join(parts)
        except Exception as e:
            print(f"[RAG] error — {e}")
            return ""

    def _run_tool(self, name: str, args: dict) -> str:
        fn = TOOL_DISPATCH.get(name)
        if not fn:
            return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            return json.dumps(fn(**args), ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def chat(self, user_message: str, history: list[dict]) -> tuple[str, list[dict]]:
        rag = self._rag_context(user_message)
        user_content = (
            f"[Информация от базата]\n{rag}\n\n[Въпрос]\n{user_message}" if rag
            else user_message
        )

        messages = [
            {"role": "system", "content": self._system_prompt(history)},
            *history,
            {"role": "user", "content": user_content},
        ]
        turn_tools: list[dict] = []

        for _ in range(8):
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.3,
                max_tokens=800,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
            )
            msg = response.choices[0].message
            messages.append(msg)

            if response.choices[0].finish_reason == "stop" or not msg.tool_calls:
                reply = msg.content or ""

                # Hallucination guard
                if _CONFIRM_RE.search(reply) and not _booked_this_turn(turn_tools):
                    print("[guard] Hallucinated booking — intercepted")
                    reply = (
                        "Съжалявам, възникна техническа грешка при записването. "
                        "Моля, потвърдете отново желания час и аз ще го запиша веднага."
                    )

                # Embed sentinel for next turn
                active_id = _doctor_from_turn(turn_tools) or (
                    _active_doctor_from_history(history)[0] if not turn_tools else None
                )
                if active_id:
                    reply += f"<!--doc:{active_id}-->"

                updated = [
                    *history,
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": reply},
                ]
                return reply, updated

            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = self._run_tool(tc.function.name, args)
                print(f"[tool] {tc.function.name}({args})")
                tool_msg = {"role": "tool", "tool_call_id": tc.id, "content": result}
                messages.append(tool_msg)
                turn_tools.append(tool_msg)

        reply = "Извинявам се, не успях да обработя заявката. Обадете се на 02 800 12 34."
        return reply, [
            *history,
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": reply},
        ]


if __name__ == "__main__":
    agent, history = MedicalAgent(), []
    print("Медицински Център Здраве Плюс — AI Асистент\n")
    while True:
        user_input = input("Пациент: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        reply, history = agent.chat(user_input, history)
        print(f"Асистент: {_SENTINEL_RE.sub('', reply)}\n")