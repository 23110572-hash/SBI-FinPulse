"use client";
import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import ChatMessage, { TypingIndicator } from "./ChatMessage";

const SUGGESTIONS = ["Tell me about SIP", "How much term insurance do I need?", "Best FD rates?", "Help me save tax"];

export default function ChatInterface({ messages, typing, onSend, language, setLanguage, loadingHistory }) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, typing]);

  const submit = (e) => {
    e?.preventDefault();
    if (!input.trim()) return;
    onSend(input);
    setInput("");
  };

  const lastAi = [...messages].reverse().find((m) => m.role === "assistant");
  const quickReplies = lastAi?.quick_replies || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", flex: 1 }}>
      <div ref={scrollRef} style={{ flex: 1, overflowY: "auto", padding: "16px",
        display: "flex", flexDirection: "column", gap: 14 }}>
        {!loadingHistory && messages.length === 0 && (
          <div style={{ textAlign: "center", margin: "auto", color: "var(--text-tertiary)", padding: 24,
            maxWidth: 320 }}>
            <p style={{ fontSize: "var(--text-base)", fontWeight: 600, color: "var(--text-secondary)",
              marginBottom: 6 }}>FinPulse AI</p>
            <p style={{ fontSize: "var(--text-sm)" }}>
              Ask me anything about SBI products, your finances or how to reach your goals.
            </p>
          </div>
        )}
        {messages.map((m, i) => <ChatMessage key={i} message={m} />)}
        {typing && <TypingIndicator />}
      </div>

      {(quickReplies.length > 0 || messages.length === 0) && (
        <div style={{ display: "flex", gap: 8, padding: "0 16px 10px", flexWrap: "wrap" }}>
          {(quickReplies.length ? quickReplies : SUGGESTIONS).map((q) => (
            <button key={q} onClick={() => onSend(q)} className="badge badge-blue"
              style={{ cursor: "pointer", padding: "7px 12px", border: "1px solid var(--sbi-blue-surface)" }}>
              {q}
            </button>
          ))}
        </div>
      )}

      <form onSubmit={submit} style={{ display: "flex", gap: 8, padding: "12px 16px",
        borderTop: "1px solid var(--neutral-200)", background: "#fff", alignItems: "center" }}>
        <button type="button" onClick={() => setLanguage(language === "en" ? "hi" : "en")}
          className="badge badge-neutral" style={{ cursor: "pointer", fontWeight: 700, padding: "8px 10px" }}>
          {language === "en" ? "EN" : "हिं"}
        </button>
        <input
          value={input} onChange={(e) => setInput(e.target.value)}
          placeholder="Message FinPulse AI..."
          style={{ flex: 1, padding: "11px 16px", borderRadius: "var(--radius-full)",
            border: "1px solid var(--neutral-300)", fontSize: "var(--text-sm)", outline: "none" }} />
        <button type="submit" className="btn btn-primary" style={{ padding: 11, borderRadius: "50%" }}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
