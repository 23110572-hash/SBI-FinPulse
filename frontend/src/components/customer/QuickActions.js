"use client";
import { useRouter } from "next/navigation";
import { TrendingUp, Shield, PiggyBank, MessageCircle } from "lucide-react";

const ACTIONS = [
  { label: "Start SIP", icon: TrendingUp, color: "#2E7D32", bg: "#E8F5E9", q: "Help me start a SIP" },
  { label: "Get Insurance", icon: Shield, color: "#0277BD", bg: "#E1F5FE", q: "I want term insurance" },
  { label: "Open FD", icon: PiggyBank, color: "#C49B2A", bg: "#F5E6B8", q: "What are the best FD rates?" },
  { label: "Ask AI", icon: MessageCircle, color: "#1A237E", bg: "#E8EAF6", q: null },
];

export default function QuickActions() {
  const router = useRouter();
  const go = (q) => {
    if (q) sessionStorage.setItem("finpulse_prefill", q);
    router.push("/customer/chat");
  };
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
      {ACTIONS.map((a) => {
        const Icon = a.icon;
        return (
          <button key={a.label} onClick={() => go(a.q)}
            style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
            <div style={{ width: 52, height: 52, borderRadius: 16, background: a.bg,
              display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Icon size={22} color={a.color} />
            </div>
            <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text-secondary)", textAlign: "center" }}>
              {a.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}
