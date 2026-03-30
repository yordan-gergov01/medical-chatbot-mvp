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

ASSISTANT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712109.png"


def respond(user_message: str, history: list):
    """Generator — директно обновява chatbot-а на всеки yield."""
    if not user_message.strip():
        yield "", history
        return

    history = history + [{"role": "user", "content": user_message}]

    thinking = history + [{"role": "assistant", "content": "⏳ Мисля…"}]
    yield "", thinking

    openai_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history
    ]

    reply, _ = agent.chat(user_message, openai_history)

    final = history + [{"role": "assistant", "content": reply}]
    yield "", final


def clear_chat():
    return []


def build_ui() -> gr.Blocks:
    with gr.Blocks(title='Медицински център "Здраве Плюс" - AI Асистент') as demo:

        gr.HTML("""
            <div style="text-align:center; padding: 16px 0 8px 0;">
                <h1 style="font-size:1.6rem; font-weight:600; margin:0;">
                    🏥 Медицински център "Здраве Плюс" - AI Асистент
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
                    avatar_images=(None, ASSISTANT_AVATAR),
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

        submit_btn.click(
            fn=respond,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot],
            show_progress="hidden",
        )

        msg_input.submit(
            fn=respond,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot],
            show_progress="hidden",
        )

        clear_btn.click(fn=clear_chat, outputs=[chatbot])

    return demo


def main():
    theme = gr.themes.Soft(font=["Inter", "system-ui", "sans-serif"])
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        theme=theme,
    )


if __name__ == "__main__":
    main()