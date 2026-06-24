"use client";
import { motion } from "framer-motion";
import { PartyPopper } from "lucide-react";
import { titleCase } from "@/lib/utils";

export default function LifeEventBanner({ event }) {
  if (!event) return null;
  return (
    <motion.div
      initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }}
      style={{
        background: "linear-gradient(135deg, #7B1FA2, #9C27B0)", color: "#fff",
        borderRadius: "var(--radius-lg)", padding: "14px 16px", display: "flex",
        alignItems: "center", gap: 12, boxShadow: "var(--shadow-md)",
      }}>
      <div style={{ width: 40, height: 40, borderRadius: 12, background: "rgba(255,255,255,0.2)",
        display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <PartyPopper size={20} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700, fontSize: "var(--text-sm)" }}>
          Life event detected: {titleCase(event.event)}
        </div>
        <div style={{ fontSize: "var(--text-xs)", color: "rgba(255,255,255,0.85)" }}>
          {event.details}
        </div>
      </div>
      {event.confidence != null && (
        <span className="badge" style={{ background: "rgba(255,255,255,0.22)", color: "#fff" }}>
          {Math.round(event.confidence * 100)}%
        </span>
      )}
    </motion.div>
  );
}
