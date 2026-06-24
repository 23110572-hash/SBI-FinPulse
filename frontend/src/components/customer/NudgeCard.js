"use client";
import { motion } from "framer-motion";
import { Target, TrendingUp } from "lucide-react";
import { FRAME_LABELS, CHANNEL_LABELS } from "@/lib/constants";

export default function NudgeCard({ nudge }) {
  const product = nudge.product_recommended || {};
  return (
    <motion.div whileHover={{ y: -2 }} className="card"
      style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
        <div style={{ width: 42, height: 42, borderRadius: 12, background: "var(--sbi-blue-surface)",
          display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <Target size={20} color="var(--sbi-blue-primary)" />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700 }}>{product.name || "Recommendation"}</div>
          <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>
            {product.category && <span>{product.category.replace(/_/g, " ")}</span>}
            {product.expected_returns && <span> · {product.expected_returns}</span>}
          </div>
        </div>
        {nudge.expected_conversion && (
          <span className="badge badge-success">
            <TrendingUp size={12} /> {nudge.expected_conversion}
          </span>
        )}
      </div>

      <p style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", lineHeight: 1.55 }}>
        {nudge.message_draft}
      </p>

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {nudge.psychological_frame && (
          <span className="badge badge-gold">{FRAME_LABELS[nudge.psychological_frame] || nudge.psychological_frame}</span>
        )}
        {nudge.channel && (
          <span className="badge badge-blue">{CHANNEL_LABELS[nudge.channel] || nudge.channel}</span>
        )}
      </div>
    </motion.div>
  );
}
