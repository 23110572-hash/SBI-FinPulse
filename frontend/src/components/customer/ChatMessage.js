"use client";
import { motion } from "framer-motion";
import { FileText } from "lucide-react";

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}
      style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start" }}>
      <div style={{ maxWidth: "82%" }}>
        <div style={{
          background: isUser ? "var(--bg-chat-user)" : "var(--bg-chat-ai)",
          color: isUser ? "#fff" : "var(--text-primary)",
          padding: "10px 14px",
          borderRadius: isUser ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
          fontSize: "var(--text-sm)", lineHeight: 1.5, whiteSpace: "pre-wrap",
          boxShadow: "var(--shadow-sm)",
        }}>
          {message.content}
        </div>
        {message.sources && message.sources.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 6 }}>
            {message.sources.slice(0, 3).map((s, i) => (
              <span key={i} className="badge badge-blue" style={{ fontSize: 10 }}>
                <FileText size={11} /> {s.title}
              </span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

export function TypingIndicator() {
  return (
    <div style={{ display: "flex", justifyContent: "flex-start" }}>
      <div style={{ background: "var(--bg-chat-ai)", padding: "12px 16px", borderRadius: "16px 16px 16px 4px",
        display: "flex", gap: 5 }}>
        {[0, 1, 2].map((i) => (
          <motion.span key={i}
            style={{ width: 7, height: 7, borderRadius: "50%", background: "var(--sbi-blue-light)" }}
            animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 0.9, repeat: Infinity, delay: i * 0.15 }} />
        ))}
      </div>
    </div>
  );
}
