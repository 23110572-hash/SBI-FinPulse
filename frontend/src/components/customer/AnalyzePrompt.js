"use client";
import { motion } from "framer-motion";
import {
  Sparkles, Loader2, UserSearch, HeartPulse, Lightbulb,
  ShieldCheck, MessageSquareText, Circle,
} from "lucide-react";
import { AGENT_ICONS } from "@/lib/constants";

// Pre-imported icon map — avoids `import *` which pulls in the entire library.
const ICONS = {
  UserSearch, HeartPulse, Lightbulb, ShieldCheck, MessageSquareText,
};

// Shown when no analysis exists yet. Runs the live crew stream.
export default function AnalyzePrompt({ steps, stepPlan, running, error, onStart }) {
  const started = running || Object.keys(steps).length > 0;

  return (
    <div className="card" style={{ textAlign: "center", padding: 28 }}>
      {!started && (
        <>
          <div style={{ width: 64, height: 64, borderRadius: "50%", background: "var(--sbi-blue-surface)",
            display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
            <Sparkles size={28} color="var(--sbi-blue-primary)" />
          </div>
          <h3 style={{ marginBottom: 8 }}>Let our AI agents analyse your finances</h3>
          <p style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", marginBottom: 20 }}>
            Five specialised agents will study your transactions, score your financial health and craft
            personalised recommendations.
          </p>
          <button className="btn btn-primary btn-block" onClick={onStart}>
            <Sparkles size={16} /> Run my analysis
          </button>
        </>
      )}

      {started && (
        <div style={{ textAlign: "left" }}>
          <h3 style={{ marginBottom: 16, textAlign: "center" }}>
            {running ? "Agents are working..." : "Analysis complete!"}
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {stepPlan.map((s) => {
              const state = steps[s.step];
              const status = state?.status || "pending";
              const Icon = ICONS[AGENT_ICONS[s.step]] || Circle;
              const done = status === "complete";
              const active = status === "running";
              return (
                <motion.div key={s.step} initial={{ opacity: 0.5 }} animate={{ opacity: 1 }}
                  style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 12px",
                    borderRadius: 12, background: active ? "var(--sbi-blue-subtle)" : "transparent" }}>
                  <div style={{ width: 34, height: 34, borderRadius: 10,
                    background: done ? "var(--color-success-light)" : "var(--neutral-100)",
                    display: "flex", alignItems: "center", justifyContent: "center" }}>
                    {active ? <Loader2 size={16} className="spin" color="var(--sbi-blue-light)" />
                      : <Icon size={16} color={done ? "var(--color-success)" : "var(--neutral-400)"} />}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: "var(--text-sm)", fontWeight: 600 }}>{s.agent}</div>
                  </div>
                  <span className={`status-dot ${done ? "dot-green" : active ? "dot-blue" : "dot-grey"}`} />
                </motion.div>
              );
            })}
          </div>
          {error && <p style={{ color: "var(--color-danger)", fontSize: "var(--text-sm)", marginTop: 12 }}>{error}</p>}
        </div>
      )}
    </div>
  );
}
