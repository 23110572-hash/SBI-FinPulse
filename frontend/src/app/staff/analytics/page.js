"use client";
import { useEffect, useState } from "react";
import Card from "@/components/common/Card";
import { BarChartCard, PieChartCard } from "@/components/staff/EngagementChart";
import { titleCase } from "@/lib/utils";
import { api } from "@/lib/api";

export default function AnalyticsPage() {
  const [data, setData] = useState(null);

  useEffect(() => { api.dashboardAnalytics().then(setData).catch(() => {}); }, []);

  const byCategory = (data?.nudges_by_category || []).map((d) => ({ name: titleCase(d.name), value: d.value }));
  const byFrame = (data?.nudges_by_frame || []).map((d) => ({ name: titleCase(d.name), value: d.value }));
  const lifeEvents = data?.life_events || [];
  const scoreDist = (data?.score_distribution || []).map((d) => ({ name: d.range, value: d.count }));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div>
        <h1 style={{ fontSize: "var(--text-3xl)" }}>Analytics</h1>
        <p className="text-secondary" style={{ fontSize: "var(--text-sm)" }}>
          Engagement metrics across the agentic pipeline.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: 20 }}>
        <ChartCard title="Health Score Distribution" subtitle="Customers by score band">
          <BarChartCard data={scoreDist} color="#1A237E" />
        </ChartCard>

        <ChartCard title="Nudges by Product Category" subtitle="What the strategist recommends">
          <BarChartCard data={byCategory} color="#3F51B5" />
        </ChartCard>

        <ChartCard title="Top Life Events Detected" subtitle="Across analyzed customers">
          {lifeEvents.length ? <PieChartCard data={lifeEvents} /> :
            <Empty />}
        </ChartCard>

        <ChartCard title="Psychological Frames" subtitle="Behavioural strategies used">
          {byFrame.length ? <BarChartCard data={byFrame} color="#C49B2A" /> : <Empty />}
        </ChartCard>
      </div>
    </div>
  );
}

function ChartCard({ title, subtitle, children }) {
  return (
    <Card>
      <h3 style={{ fontSize: "var(--text-lg)" }}>{title}</h3>
      <p style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", marginBottom: 12 }}>{subtitle}</p>
      {children}
    </Card>
  );
}
function Empty() {
  return <div style={{ height: 200, display: "flex", alignItems: "center", justifyContent: "center",
    color: "var(--text-tertiary)", fontSize: "var(--text-sm)" }}>Run analyses to populate this chart.</div>;
}
