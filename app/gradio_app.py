import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import gradio as gr
from src.agent import MedicalAgent

print("Loading agent...")
agent = MedicalAgent()
print("Agent ready.\n")

EXAMPLES = [
    "Имам болки в гърдите и задух от два дни. При кой лекар да се запиша?",
    "Коляното ме боли след тренировка. Има ли ортопед с опит в спортни травми?",
    "Искам да запиша час при невролог за следващата седмица.",
    "Кои лекари приемат по НЗОК?",
    "До колко часа работи центърът в събота?",
]


def respond(user_message: str, chat_history: list) -> tuple:
    if not user_message.strip():
        return "", chat_history

    openai_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in chat_history
    ]

    reply, _ = agent.chat(user_message, openai_history)

    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": reply})
    return "", chat_history


def clear_chat() -> tuple:
    return [], []


with gr.Blocks(title="Медицински Център Здраве Плюс - AI Асистент") as demo:

    gr.HTML("""
        <div style="text-align:center; padding: 16px 0 8px 0;">
            <h1 style="font-size:1.6rem; font-weight:600; margin:0;">
                🏥 Медицински Център Здраве Плюс
            </h1>
            <p style="color:#64748b; margin:4px 0 0 0; font-size:0.95rem;">
                AI асистент за записване на часове · София, бул. Васил Левски 47 · 02 800 12 34
            </p>
        </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                height=480,
                show_label=False,
                avatar_images=(
                    None,
                    "https://cdn-icons-png.flaticon.com/512/2965/2965278.png"
                ),
            )

            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Опишете симптомите си или задайте въпрос...",
                    show_label=False,
                    scale=5,
                    container=False,
                )
                submit_btn = gr.Button("Изпрати", variant="primary", scale=1, min_width=90)

            clear_btn = gr.Button("🗑 Нов разговор", variant="secondary", size="sm")

        with gr.Column(scale=1):
            gr.Markdown("### 💡 Примерни въпроси")
            for example in EXAMPLES:
                ex_btn = gr.Button(example, variant="secondary", size="sm")
                ex_btn.click(fn=lambda e=example: e, outputs=msg_input)

            gr.Markdown("""
### ℹ️ Информация
**Работно време**
Пон – Пет: 08:00 – 19:00
Събота: 09:00 – 14:00

**Спешни случаи**
При спешни симптоми — обадете се на **112**

**Записване по телефон**
02 800 12 34
            """)

    state = gr.State([])

    submit_btn.click(
        fn=respond,
        inputs=[msg_input, state],
        outputs=[msg_input, state],
    ).then(fn=lambda h: h, inputs=state, outputs=chatbot)

    msg_input.submit(
        fn=respond,
        inputs=[msg_input, state],
        outputs=[msg_input, state],
    ).then(fn=lambda h: h, inputs=state, outputs=chatbot)

    clear_btn.click(fn=clear_chat, outputs=[state, chatbot])


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
    )