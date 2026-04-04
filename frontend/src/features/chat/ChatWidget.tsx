import { useState, useRef, useEffect, forwardRef, useImperativeHandle } from "react";
import { X, Send, Stethoscope } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const quickReplies = [
  "Имам болка в гърдите",
  "Запази час при невролог",
  "Кой лекар работи с НЗОК?",
  "Работно време", 
  "Цени",
];

const initialMessages: Message[] = [
  {
    role: "assistant",
    content:
      "Здравей! Аз съм виртуалният асистент на Медицински център 'Здраве плюс'. Мога да ти помогна да откриеш правилния специалист за теб, спрямо твоите нужди, и да запазим час за консултация. Как мога да ти помогна днес?",
  },
];

const mockConversation: Message[] = [
  { role: "user", content: "Имам главоболие" },
  {
    role: "assistant",
    content:
      'Препоръчвам ти да си запазиш час при някой от невролозите при нас. Имаме д-р Елена Николова and д-р Стефан Димитров. При кого от тях би искал да проверил за свободни часове',
  },
];

export interface ChatWidgetHandle {
  open: () => void;
}

const ChatWidget = forwardRef<ChatWidgetHandle>((_props, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    ...initialMessages,
    ...mockConversation,
  ]);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useImperativeHandle(ref, () => ({ open: () => setIsOpen(true) }));

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isOpen]);

  const sendMessage = () => {
    const text = input.trim();
    if (!text) return;
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Thank you for your message. A specialist will review "${text}" and get back to you shortly. In the meantime, you can call us at 02 800 12 34.`,
        },
      ]);
    }, 800);
  };

  const handleQuickReply = (text: string) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Thank you for asking about "${text}". Let me help you with that. Please call us at 02 800 12 34 or I can book an appointment for you.`,
        },
      ]);
    }, 800);
  };

  return (
    <>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-primary flex items-center justify-center text-primary-foreground shadow-xl hover:scale-105 transition-transform"
        >
          <span className="absolute inset-0 rounded-full bg-online animate-pulse-ring" />
          <Stethoscope size={24} />
        </button>
      )}

      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-[380px] max-w-[calc(100vw-2rem)] h-[520px] max-h-[calc(100vh-3rem)] bg-card rounded-2xl shadow-2xl border border-border flex flex-col animate-slide-up overflow-hidden">
          <div className="flex items-center gap-3 px-4 py-3 border-b border-border bg-primary/5">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-display font-bold text-lg">
              З
            </div>
            <div className="flex-1">
              <p className="font-semibold text-sm">Zdrave Plus Assistant</p>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-online" />
                <span className="text-xs text-muted-foreground">Online</span>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-muted-foreground hover:text-foreground transition-colors">
              <X size={20} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-chat-bubble`}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-chat-user text-chat-user-foreground rounded-br-md"
                      : "bg-chat-assistant text-chat-assistant-foreground rounded-bl-md"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {messages.length <= 1 + mockConversation.length && (
              <div className="flex flex-wrap gap-2 pt-1">
                {quickReplies.map((qr) => (
                  <button
                    key={qr}
                    onClick={() => handleQuickReply(qr)}
                    className="px-3 py-1.5 rounded-full border border-primary/30 text-xs font-medium text-primary hover:bg-primary/10 transition-colors"
                  >
                    {qr}
                  </button>
                ))}
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="border-t border-border p-3 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Describe your symptoms or ask a question..."
              className="flex-1 bg-secondary rounded-lg px-3 py-2 text-sm outline-none placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/30"
            />
            <Button size="icon" onClick={sendMessage} disabled={!input.trim()}>
              <Send size={16} />
            </Button>
          </div>
        </div>
      )}
    </>
  );
});

ChatWidget.displayName = "ChatWidget";

export default ChatWidget;
