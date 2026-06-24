"use client";
import { useCallback, useState } from "react";
import Card from "@/components/common/Card";
import StatsGrid from "@/components/staff/StatsGrid";
import ActivityTable from "@/components/staff/ActivityTable";
import EngagementFeed from "@/components/staff/EngagementFeed";
import { LineTrend } from "@/components/staff/EngagementChart";
import { usePolling } from "@/hooks/usePolling";
import { api } from "@/lib/api";

export default function StaffDashboard() {
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  const refresh = useCallback(async () => {
    const [s, a, an] = await Promise.allSettled([
      api.dashboardStats(),
      api.dashboardActivity(),
      api.dashboardAnalytics(),
    ]);
    if (s.status === "fulfilled") setStats(s.value);
    if (a.status === "fulfilled") setActivity(a.value.activity || []);
    if (an.status === "fulfilled") setAnalytics(an.value);
  }, []);

  usePolling(refresh, 30000);

  const scoreData = (analytics?.score_distribution || []).map((s) => ({ name: s.range, value: s.count }));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div>
        <h1 style={{ fontSize: "var(--text-3xl)" }}>Dashboard</h1>
        <p className="text-secondary" style={{ fontSize: "var(--text-sm)" }}>
          Live overview of agentic engagement across your customer base.
        </p>
      </div>

      <StatsGrid stats={stats} />

      <div className="staff-split">
        <EngagementFeed />
        <ActivityTable activity={activity} />
      </div>

      <div className="staff-split">
        <Card>
          <h3 style={{ fontSize: "var(--text-lg)", marginBottom: 8 }}>Health Score Distribution</h3>
          <p style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", marginBottom: 8 }}>
            Across analyzed customers
          </p>
          <LineTrend data={scoreData} color="#3F51B5" height={220} />
        </Card>
      </div>
    </div>
  );
}
