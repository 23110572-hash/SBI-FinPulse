"use client";
import { useCallback, useState } from "react";
import { Radar, Zap, Clock, RefreshCw } from "lucide-react";
import Card from "@/components/common/Card";
import { usePolling } from "@/hooks/usePolling";
import { api } from "@/lib/api";
import { titleCase } from "@/lib/utils";

const SOURCE_ICON = { scheduler: Clock, webhook: Zap, manual: Radar };

const STATUS_VARIANT = {
  processed: "badge-success",
  processing: "badge-blue",
  detected: "badge-gold",
  skipped: "badge-neutral",
};

/**
 * Live feed of proactive triggers detected by the engagement engine
 * (scheduled scans + real-time webhooks). Demonstrates that FinPulse
 * reaches out on its own, not just on a staff click.
 */
export default function EngagementFeed() {
  const [events, setEvents] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [lastScan, setLastScan] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const d = (await api.allEngagementEvents(30)) || [];
      // only re-render when the data actually changed
      setEvents((prev) => {
        const sameLen = prev.length === d.length;
        const sameTop = sameLen && prev[0]?.id === d[0]?.id &&
          prev[0]?.status === d[0]?.status;
        return sameTop ? prev : d;
      });
    } catch (_) {}
  }, []);

  usePolling(refresh, 30000);

  const runScan = async () => {
    setScanning(true);
    try {
      const summary = await api.runScan();
      setLastScan(summary);
      await refresh();
    } catch (_) {
    } finally {
      setScanning(false);
    }
  };

  return (
    <Card>
      <div className="flex items-center justify-between" style={{ marginBottom: 6 }}>
        <div>
          <h3 style={{ fontSize: "var(--text-lg)", display: "flex", alignItems: "center", gap: 8 }}>
            <Radar size={18} /> Proactive Engagement
          </h3>
          <p style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>
            Signals detected from behaviour, patterns &amp; life events
          </p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={runScan} disabled={scanning}>
          <RefreshCw size={14} className={scanning ? "spin" : ""} />
          {scanning ? "Scanning…" : "Run scan"}
        </button>
      </div>

      {lastScan && (
        <div style={{ fontSize: 11, color: "var(--text-tertiary)", marginBottom: 10 }}>
          Last scan: {lastScan.scanned} scanned · {lastScan.triggered} triggered ·{" "}
          {lastScan.skipped} skipped (no consent / fresh)
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 360, overflowY: "auto" }}>
        {events.length === 0 && (
          <div style={{ fontSize: "var(--text-sm)", color: "var(--text-tertiary)", padding: "16px 0" }}>
            No proactive events yet. Run a scan, or push a transaction to{" "}
            <code>/api/engagement/webhook/transaction</code>.
          </div>
        )}
        {events.map((e) => {
          const Icon = SOURCE_ICON[e.source] || Radar;
          return (
            <div key={e.id} style={{
              display: "flex", alignItems: "center", gap: 12, padding: "10px 12px",
              background: "var(--sbi-blue-subtle)", borderRadius: 10,
            }}>
              <Icon size={16} style={{ color: "var(--sbi-blue, #1A237E)", flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 600, fontSize: "var(--text-sm)" }}>
                  {titleCase((e.signal || "").replace(/_/g, " "))}
                </div>
                <div style={{ fontSize: 11, color: "var(--text-tertiary)" }}>
                  {e.customer_id} · {e.source}
                  {e.confidence ? ` · ${Math.round(e.confidence * 100)}%` : ""}
                </div>
              </div>
              <span className={`badge ${STATUS_VARIANT[e.status] || "badge-neutral"}`}>
                {titleCase(e.status)}
              </span>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
