"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useCustomerId } from "@/hooks/useCustomer";
import { useAnalysis } from "@/hooks/useAnalysis";
import InsightCard from "@/components/customer/InsightCard";
import { SkeletonCard } from "@/components/common/Skeleton";

const FILTERS = [
  { key: "all", label: "All" },
  { key: "life_event", label: "Life Events" },
  { key: "alert", label: "Alerts" },
  { key: "opportunity", label: "Opportunities" },
  { key: "product_suggestion", label: "For You" },
];

export default function InsightsPage() {
  const router = useRouter();
  const [customerId] = useCustomerId();
  const { analysis, loading } = useAnalysis(customerId);
  const [filter, setFilter] = useState("all");

  const insights = buildInsights(analysis);
  const filtered = filter === "all" ? insights : insights.filter((i) => i.type === filter);

  return (
    <div>
      <div className="gradient-header">
        <h2 style={{ fontSize: "var(--text-2xl)" }}>Your Insights</h2>
        <p style={{ color: "rgba(255,255,255,0.78)", fontSize: "var(--text-sm)" }}>
          AI-detected events, alerts and opportunities
        </p>
      </div>

      <div style={{ display: "flex", gap: 8, overflowX: "auto", padding: "16px 16px 4px" }}>
        {FILTERS.map((f) => (
          <button key={f.key} onClick={() => setFilter(f.key)}
            className={`badge ${filter === f.key ? "badge-blue" : "badge-neutral"}`}
            style={{ cursor: "pointer", padding: "8px 14px", whiteSpace: "nowrap",
              border: filter === f.key ? "1px solid var(--sbi-blue-light)" : "1px solid transparent" }}>
            {f.label}
          </button>
        ))}
      </div>

      <div className="page-pad" style={{ display: "flex", flexDirection: "column", gap: 12, paddingTop: 8 }}>
        {loading && <><SkeletonCard /><SkeletonCard /></>}
        {!loading && filtered.length === 0 && (
          <div style={{ textAlign: "center", padding: 40, color: "var(--text-tertiary)" }}>
            <div style={{ fontSize: 36 }}>🌱</div>
            <p style={{ fontSize: "var(--text-sm)", marginTop: 8 }}>
              No insights here yet. Run your analysis from the Home tab.
            </p>
          </div>
        )}
        {filtered.map((ins, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.18, ease: "easeOut" }}>
            <InsightCard insight={ins} onAction={() => router.push("/customer/chat")} />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function buildInsights(analysis) {
  if (!analysis) return [];
  const out = [];
  (analysis.profile?.life_events_detected || []).forEach((ev) =>
    out.push({ type: "life_event", icon: "PartyPopper", title: tc(ev.event), description: ev.details, action: "Explore options" }));
  (analysis.wellness?.critical_gaps || []).forEach((g) =>
    out.push({ type: "alert", icon: "TrendingDown", title: tc(g.gap), description: g.impact, action: "Fix this" }));
  (analysis.wellness?.quick_wins || []).forEach((w) =>
    out.push({ type: "opportunity", icon: "Lightbulb", title: w.action, description: w.impact, action: "Act now" }));
  (analysis.nudge_plan?.nudges || []).forEach((n) =>
    out.push({ type: "product_suggestion", icon: "Target", title: n.product_recommended?.name || n.product_recommended?.product_name, description: n.message_draft, action: "Learn more" }));
  return out;
}
function tc(s) { return (s || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()); }
