"use client";
import { motion } from "framer-motion";
import {
  ArrowRight, Sparkles, PartyPopper, Lightbulb, TrendingDown, Target,
} from "lucide-react";

// Pre-imported icon map — avoids `import *` which forces the entire library into the bundle.
const ICONS = { PartyPopper, Lightbulb, TrendingDown, Target, Sparkles };

const TYPE_STYLES = {
  life_event: { accent: "#7B1FA2", bg: "#F3E5F5", emoji: "🎉" },
  alert: { accent: "var(--color-warning)", bg: "var(--color-warning-light)", emoji: "📉" },
  opportunity: { accent: "var(--color-success)", bg: "var(--color-success-light)", emoji: "💡" },
  product_suggestion: { accent: "var(--sbi-blue-light)", bg: "var(--sbi-blue-surface)", emoji: "🎯" },
};

export default function InsightCard({ insight, compact = false, onAction }) {
  const style = TYPE_STYLES[insight.type] || TYPE_STYLES.product_suggestion;
  const Icon = ICONS[insight.icon] || Sparkles;

  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="card"
      style={{
        borderLeft: `4px solid ${style.accent}`, padding: 16,
        minWidth: compact ? 240 : "auto", flexShrink: 0,
        display: "flex", flexDirection: "column", gap: 8,
      }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ width: 36, height: 36, borderRadius: 10, background: style.bg,
          display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <Icon size={18} color={style.accent} />
        </div>
        <div style={{ fontWeight: 700, fontSize: "var(--text-sm)", color: "var(--text-primary)" }}>
          {insight.title}
        </div>
      </div>
      <p style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)",
        display: "-webkit-box", WebkitLineClamp: compact ? 2 : 4, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
        {insight.description}
      </p>
      <button onClick={onAction}
        style={{ display: "flex", alignItems: "center", gap: 4, color: style.accent,
          fontWeight: 600, fontSize: "var(--text-sm)", marginTop: "auto" }}>
        {insight.action || "View"} <ArrowRight size={15} />
      </button>
    </motion.div>
  );
}
