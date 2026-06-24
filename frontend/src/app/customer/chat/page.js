"use client";
import { useEffect, useRef } from "react";
import { useCustomerId } from "@/hooks/useCustomer";
import { useChat } from "@/hooks/useChat";
import ChatInterface from "@/components/customer/ChatInterface";

export default function ChatPage() {
  const [customerId] = useCustomerId();
  const chat = useChat(customerId);
  const prefilled = useRef(false);

  // pick up a prefill from quick actions
  useEffect(() => {
    if (prefilled.current || chat.loadingHistory) return;
    const q = typeof window !== "undefined" && sessionStorage.getItem("finpulse_prefill");
    if (q) {
      sessionStorage.removeItem("finpulse_prefill");
      prefilled.current = true;
      chat.send(q);
    }
  }, [chat.loadingHistory]);

  return (
    <div className="chat-page">
      <div style={{ background: "var(--gradient-header)", color: "#fff", padding: "16px 20px",
        display: "flex", alignItems: "center", gap: 12 }}>
        <div>
          <div style={{ fontWeight: 700 }}>FinPulse AI</div>
          <div style={{ fontSize: "var(--text-xs)", display: "flex", alignItems: "center", gap: 6,
            color: "rgba(255,255,255,0.8)" }}>
            <span className="status-dot dot-green" /> Online
          </div>
        </div>
      </div>

      <ChatInterface
        messages={chat.messages} typing={chat.typing} onSend={chat.send}
        language={chat.language} setLanguage={chat.setLanguage} loadingHistory={chat.loadingHistory} />
    </div>
  );
}
