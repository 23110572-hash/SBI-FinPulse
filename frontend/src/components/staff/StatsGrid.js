"use client";
import { motion } from "framer-motion";
import { Users, Bell, TrendingUp, PartyPopper } from "lucide-react";
import AnimatedCounter from "@/components/common/AnimatedCounter";

export default function StatsGrid({ stats }) {
  const cards = [
    { label: "Customers Analyzed", value: stats?.customers_analyzed ?? 0, icon: Users,
      color: "#1A237E", bg: "#E8EAF6", suffix: "" },
    { label: "Nudges Generated", value: stats?.nudges_generated ?? 0, icon: Bell,
      color: "#C49B2A", bg: "#F5E6B8", suffix: "" },
    { label: "Response Rate", value: stats?.response_rate ?? 0, icon: TrendingUp,
      color: "#2E7D32", bg: "#E8F5E9", suffix: "%" },
    { label: "Life Events Detected", value: stats?.life_events_detected ?? 0, icon: PartyPopper,
      color: "#7B1FA2", bg: "#F3E5F5", suffix: "" },
  ];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <motion.div key={c.label} className="card card-hover"
            initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
            style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ width: 50, height: 50, borderRadius: 14, background: c.bg,
              display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <Icon size={24} color={c.color} />
            </div>
            <div>
              <div style={{ fontFamily: "var(--font-heading)", fontSize: "var(--text-3xl)", fontWeight: 800,
                color: "var(--text-primary)", lineHeight: 1 }}>
                <AnimatedCounter value={c.value} decimals={c.suffix === "%" ? 1 : 0} suffix={c.suffix} />
              </div>
              <div style={{ fontSize: "var(--text-sm)", color: "var(--text-tertiary)", marginTop: 4 }}>{c.label}</div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
