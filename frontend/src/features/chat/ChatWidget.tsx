import {
  useState, useRef, useEffect, forwardRef, useImperativeHandle,
} from "react";

import { X, Send, Stethoscope, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Message } from "@/types/api-responses";
import { sendChatMessage } from "@/services/api";

const quickReplies = [
  "Имам болка в гърдите",
  "Запази час при невролог",
  "Кой лекар работи с НЗОК?",
  "Работно време",
  "Цени",
];

const INITIAL_MESSAGES: Message[] = [
  {
    role: "assistant",
    content:
      "Здравей! Аз съм виртуалният асистент на Медицински център „Здраве Плюс\". " +
      "Мога да ти помогна да намериш правилния специалист и да запазим час. " +
      "Как мога да ти помогна днес?",
  },
];

export interface ChatWidgetHandle {
  open: () => void;
}

const ChatWidget = forwardRef<ChatWidgetHandle>((_props, ref) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [history, setHistory] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useImperativeHandle(ref, () => ({ open: () => setIsOpen(true) }));

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isOpen]);

  const sendMessage = async (text: string = input.trim()) => {
    if (!text || loading) return;
    setInput("");

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await sendChatMessage(text, history);
      const assistantMsg: Message = { role: "assistant", content: res.reply };
      setMessages((prev) => [...prev, assistantMsg]);
      // Keep full OpenAI-format history for the agent
      setHistory(res.history);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Извинявам се, има технически проблем. Моля, опитайте отново или се обадете на 02 800 12 34.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const showQuickReplies = messages.length === 1; // only initial message visible

  return (
    <>
      {/* Floating trigger button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-primary flex items-center justify-center text-primary-foreground shadow-xl hover:scale-105 transition-transform"
          aria-label="Open chat"
        >
          <span className="absolute inset-0 rounded-full bg-online animate-pulse-ring" />
          <Stethoscope size={24} />
        </button>
      )}

      {/* Chat panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-[380px] max-w-[calc(100vw-2rem)] h-[520px] max-h-[calc(100vh-3rem)] bg-card rounded-2xl shadow-2xl border border-border flex flex-col animate-slide-up overflow-hidden">

          {/* Header */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-border bg-primary/5">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-display font-bold text-lg">
              З
            </div>
            <div className="flex-1">
              <p className="font-semibold text-sm">Здраве Плюс Асистент</p>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-xs text-muted-foreground">Онлайн</span>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Close chat"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-br-md"
                      : "bg-secondary text-secondary-foreground rounded-bl-md"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-secondary rounded-2xl rounded-bl-md px-4 py-3 flex items-center gap-1.5">
                  <Loader2 size={14} className="animate-spin text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Пиша…</span>
                </div>
              </div>
            )}

            {/* Quick replies - shown only before user's first message */}
            {showQuickReplies && !loading && (
              <div className="flex flex-wrap gap-2 pt-1">
                {quickReplies.map((qr) => (
                  <button
                    key={qr}
                    onClick={() => sendMessage(qr)}
                    className="px-3 py-1.5 rounded-full border border-primary/30 text-xs font-medium text-primary hover:bg-primary/10 transition-colors"
                  >
                    {qr}
                  </button>
                ))}
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-border p-3 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
              placeholder="Опишете симптомите или задайте въпрос…"
              disabled={loading}
              className="flex-1 bg-secondary rounded-lg px-3 py-2 text-sm outline-none placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/30 disabled:opacity-50"
            />
            <Button
              size="icon"
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
            </Button>
          </div>
        </div>
      )}
    </>
  );
});

ChatWidget.displayName = "ChatWidget";

export default ChatWidget;