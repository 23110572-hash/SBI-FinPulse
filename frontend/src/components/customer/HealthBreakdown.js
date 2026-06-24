"use client";
import { motion } from "framer-motion";
import {
  PiggyBank, Umbrella, ShieldCheck, TrendingUp, Scale, Circle,
} from "lucide-react";
import { WELLNESS_CATEGORIES } from "@/lib/constants";
import { scoreColor } from "@/lib/utils";
import Card from "@/components/common/Card";

const ICONS = { PiggyBank, Umbrella, ShieldCheck, TrendingUp, Scale };

export default function HealthBreakdown({ breakdown = {} }) {
  return (
    <Card>
      <h3 style={{ fontSize: "var(--text-lg)", marginBottom: 16 }}>Score Breakdown</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
        {WELLNESS_CATEGORIES.map((cat, i) => {
          const item = breakdown[cat.key];
          if (!item) return null;
          const Icon = ICONS[cat.icon] || Circle;
          const color = scoreColor(item.score);
          return (
            <div key={cat.key}>
              <div className="flex items-center justify-between" style={{ marginBottom: 6 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Icon size={16} color={color} />
                  <span style={{ fontSize: "var(--text-sm)", fontWeight: 600 }}>{cat.label}</span>
                </div>
                <span style={{ fontSize: "var(--text-sm)", fontWeight: 700, color }}>{item.score}</span>
              </div>
              <div className="progress-track">
                <motion.div className="progress-fill"
                  style={{ background: color }}
                  initial={{ width: 0 }} animate={{ width: `${item.score}%` }}
                  transition={{ duration: 0.6, delay: 0.04 * i, ease: "easeOut" }} />
              </div>
              {item.detail && (
                <p style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", marginTop: 5 }}>
                  {item.detail}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}
