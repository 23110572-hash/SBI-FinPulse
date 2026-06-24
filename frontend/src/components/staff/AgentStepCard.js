"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronDown, Loader2, UserSearch, HeartPulse, Lightbulb,
  ShieldCheck, MessageSquareText, Circle,
} from "lucide-react";
import { AGENT_ICONS } from "@/lib/constants";

const ICONS = {
  UserSearch, HeartPulse, Lightbulb, ShieldCheck, MessageSquareText,
};

export default function AgentStepCard({ step, meta, status = "pending", log, isLast }) {
  const [open, setOpen] = useState(false);
  const Icon = ICONS[AGENT_ICONS[step]] || Circle;
  const done = status === "complete";
  const active = status === "running";

  const ringColor = done ? "var(--color-success)" : active ? "var(--sbi-blue-light)" : "var(--neutral-300)";

  return (
    <div style={{ display: "flex", gap: 16 }}>
      {/* timeline rail */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ width: 44, height: 44, borderRadius: "50%", flexShrink: 0,
          background: done ? "var(--color-success-light)" : active ? "var(--sbi-blue-surface)" : "var(--neutral-100)",
          border: `2px solid ${ringColor}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
          {active ? <Loader2 size={18} className="spin" color="var(--sbi-blue-light)" />
            : <Icon size={18} color={done ? "var(--color-success)" : "var(--neutral-400)"} />}
        </div>
        {!isLast && (
          <div style={{ width: 2, flex: 1, minHeight: 24, marginTop: 4,
            background: done ? "var(--color-success)" : "var(--neutral-200)",
            transition: "background var(--transition-slow)" }} />
        )}
      </div>

      {/* content */}
      <div style={{ flex: 1, paddingBottom: 20 }}>
        <div className="card" style={{ padding: 0, overflow: "hidden",
          borderColor: active ? "var(--sbi-blue-light)" : undefined }}>
          <button onClick={() => log && setOpen(!open)}
            style={{ width: "100%", display: "flex", alignItems: "center", gap: 12, padding: "14px 16px",
              textAlign: "left", cursor: log ? "pointer" : "default" }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: "var(--text-sm)" }}>{meta?.agent || step}</div>
            </div>
            <span className={`status-dot ${done ? "dot-green" : active ? "dot-blue" : "dot-grey"}`} />
            {log && <ChevronDown size={16} style={{ transform: open ? "rotate(180deg)" : "none",
              transition: "transform var(--transition-base)", color: "var(--text-tertiary)" }} />}
          </button>

          <AnimatePresence>
            {open && log && (
              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }} style={{ overflow: "hidden" }}>
                <div style={{ borderTop: "1px solid var(--neutral-100)", padding: 16 }}>
                  {log.summary && (
                    <p style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", marginBottom: 12,
                      fontStyle: "italic" }}>
                      {log.summary}
                    </p>
                  )}
                  <pre style={{ background: "var(--sbi-blue-subtle)", borderRadius: 10, padding: 12,
                    fontSize: 11.5, fontFamily: "var(--font-mono)", overflow: "auto", maxHeight: 320,
                    color: "var(--text-primary)", margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                    {JSON.stringify(log.output, null, 2)}
                  </pre>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
