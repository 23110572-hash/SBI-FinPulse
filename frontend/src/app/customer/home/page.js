"use client";
import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, RefreshCw } from "lucide-react";
import { useCustomerId, useCustomer } from "@/hooks/useCustomer";
import { useAnalysis, useAnalysisStream } from "@/hooks/useAnalysis";
import CustomerHeader from "@/components/customer/CustomerHeader";
import HealthScoreCard from "@/components/customer/HealthScoreCard";
import HealthBreakdown from "@/components/customer/HealthBreakdown";
import QuickActions from "@/components/customer/QuickActions";
import LifeEventBanner from "@/components/customer/LifeEventBanner";
import InsightCard from "@/components/customer/InsightCard";
import AnalyzePrompt from "@/components/customer/AnalyzePrompt";
import { PageSkeleton } from "@/components/common/Skeleton";

export default function CustomerHome() {
  const router = useRouter();
  const [customerId, setCustomerId] = useCustomerId();
  const { customer } = useCustomer(customerId);
  const { analysis, loading, reload } = useAnalysis(customerId);
  const stream = useAnalysisStream(customerId);

  // when a live stream completes, refresh the stored analysis
  useEffect(() => {
    if (stream.result) reload();
  }, [stream.result, reload]);

  // Auto-start analysis on first visit (or after a customer switch) so the
  // user never has to click "Run my analysis". One run per customer per mount.
  const autoStarted = useRef(null);
  useEffect(() => {
    if (!customerId) return;
    if (loading) return;                          // wait for cache check
    if (analysis?.wellness) return;               // already have results
    if (stream.running || stream.result) return;  // run in flight or finished
    if (autoStarted.current === customerId) return;
    autoStarted.current = customerId;
    stream.start();
  }, [customerId, loading, analysis, stream.running, stream.result, stream.start]);

  const wellness = analysis?.wellness;
  const profile = analysis?.profile;
  const lifeEvent = profile?.life_events_detected?.[0];
  const insights = buildInsights(analysis);

  // A run is in flight (initial OR a manual re-analyze) — show live progress.
  const analysing = stream.running || (Object.keys(stream.steps).length > 0 && !stream.result);

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100%" }}>
      <CustomerHeader name={customer?.name} subtitle="Hello," customerId={customerId} onSwitch={setCustomerId} />

      <div className="page-pad" style={{ marginTop: -32, display: "flex", flexDirection: "column", gap: 18 }}>
        {loading && !wellness && !analysing && <PageSkeleton />}

        {/* live agent stream — shown on first analysis AND on re-analyze */}
        {(analysing || (!loading && !wellness)) && (
          <AnalyzePrompt {...stream} onStart={stream.start} />
        )}

        {wellness && !analysing && (
          <>
            <div className="flex items-center justify-between">
              <h3 style={{ fontSize: "var(--text-lg)" }}>Your financial health</h3>
              <button className="btn-ghost btn-sm" onClick={() => stream.start()}
                disabled={stream.running}
                style={{ display: "flex", alignItems: "center", gap: 6, fontWeight: 600 }}>
                <RefreshCw size={14} /> Re-analyze
              </button>
            </div>

            <HealthScoreCard
              score={wellness.overall_score} grade={wellness.grade}
              peerComparison={wellness.peer_comparison} />

            {lifeEvent && <LifeEventBanner event={lifeEvent} />}

            <QuickActions />

            <HealthBreakdown breakdown={wellness.breakdown} />

            <div>
              <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
                <h3 style={{ fontSize: "var(--text-lg)", display: "flex", alignItems: "center", gap: 6 }}>
                  <Sparkles size={18} color="var(--sbi-gold)" /> AI Insights
                </h3>
                <button className="btn-ghost" style={{ fontSize: "var(--text-sm)", fontWeight: 600 }}
                  onClick={() => router.push("/customer/insights")}>See all</button>
              </div>
              <div style={{ display: "flex", gap: 12, overflowX: "auto", paddingBottom: 8, margin: "0 -4px",
                paddingLeft: 4, paddingRight: 4 }}>
                {insights.slice(0, 4).map((ins, i) => (
                  <InsightCard key={i} insight={ins} compact onAction={() => router.push("/customer/insights")} />
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function buildInsights(analysis) {
  if (!analysis) return [];
  const out = [];
  (analysis.profile?.life_events_detected || []).forEach((ev) =>
    out.push({ type: "life_event", icon: "PartyPopper", title: titleCase(ev.event), description: ev.details, action: "Explore" }));
  (analysis.wellness?.quick_wins || []).forEach((w) =>
    out.push({ type: "opportunity", icon: "Lightbulb", title: w.action, description: w.impact, action: "Act now" }));
  (analysis.nudge_plan?.nudges || []).forEach((n) =>
    out.push({ type: "product_suggestion", icon: "Target", title: n.product_recommended?.name || n.product_recommended?.product_name, description: n.message_draft, action: "Learn more" }));
  return out;
}

function titleCase(s) { return (s || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()); }
