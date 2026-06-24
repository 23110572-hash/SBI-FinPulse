"use client";
import { useMemo, useState, useCallback } from "react";
import {
  Mail, ShieldCheck, ShieldAlert, ShieldX, Clock, AlertTriangle,
  Check, X, Scale, CreditCard, PiggyBank,
} from "lucide-react";
import Card from "@/components/common/Card";
import Skeleton from "@/components/common/Skeleton";
import { usePolling } from "@/hooks/usePolling";
import { api } from "@/lib/api";

// Risk-tiered nudge console:
//   - Review Queue  : Tier 2 (credit) and Tier 3 (MF/insurance) approved nudges
//                     awaiting staff sign-off. RBI/IRDAI/SEBI mandate this.
//   - Engagement Log: immutable audit of every nudge across all tiers,
//                     including auto-sent Tier 1, blocked, failed, queued.

const STATUS_FILTERS = [
  { key: "all", label: "All" },
  { key: "sent", label: "Sent" },
  { key: "queued", label: "Queued" },
  { key: "blocked", label: "Blocked" },
  { key: "failed", label: "Failed" },
];

function bucket(n) {
  if (n.delivery_status === "sent") return "sent";
  if (n.delivery_status === "failed" || n.delivery_status === "not_configured") return "failed";
  if (n.delivery_status === "blocked_no_consent" || n.delivery_status === "blocked_compliance")
    return "blocked";
  if (n.compliance_status === "rejected") return "blocked";
  return "queued";
}

function fmtTime(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}

const TIER_META = {
  1: { name: "Tier 1 · Low risk", short: "T1", color: "var(--color-success)",
       bg: "var(--color-success-light)", icon: PiggyBank },
  2: { name: "Tier 2 · Medium risk", short: "T2", color: "var(--color-warning)",
       bg: "var(--color-warning-light)", icon: CreditCard },
  3: { name: "Tier 3 · High risk", short: "T3", color: "var(--color-danger)",
       bg: "var(--color-danger-light)", icon: Scale },
};

export default function NudgesPage() {
  const [nudges, setNudges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("review");
  const [filter, setFilter] = useState("all");
  const [notice, setNotice] = useState(null);

  const refresh = useCallback(() =>
    api.listNudges()
      .then((d) => setNudges(d || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  , []);

  // pauses while the tab is hidden, never overlaps with itself, runs once on mount
  usePolling(refresh, 30000);

  const flash = (type, text) => {
    setNotice({ type, text });
    setTimeout(() => setNotice(null), 5500);
  };

  const onApprove = async (id) => {
    try { await api.approveNudge(id); flash("success", "Approved. Sending…"); }
    catch (e) { flash("danger", e.message || "Approve failed"); return; }
    try {
      const res = await api.sendNudge(id);
      if (res?.delivered) flash("success", `Delivered via ${res.channel || "email"}.`);
      else flash("warning", res?.error || `Not delivered (${res?.status}).`);
    } catch (e) { flash("danger", e.message || "Send failed"); }
    refresh();
  };
  const onReject = async (id) => {
    try { await api.rejectNudge(id); flash("success", "Rejected."); refresh(); }
    catch (e) { flash("danger", e.message || "Reject failed"); }
  };

  const reviewQueue = useMemo(() => nudges.filter((n) => n.requires_review), [nudges]);

  const counts = useMemo(() => {
    const c = { all: nudges.length, sent: 0, queued: 0, blocked: 0, failed: 0 };
    nudges.forEach((n) => { c[bucket(n)] += 1; });
    return c;
  }, [nudges]);

  const tierCounts = useMemo(() => {
    const c = { 1: 0, 2: 0, 3: 0 };
    nudges.forEach((n) => { if (n.tier in c) c[n.tier] += 1; });
    return c;
  }, [nudges]);

  const filteredLog = useMemo(
    () => filter === "all" ? nudges : nudges.filter((n) => bucket(n) === filter),
    [nudges, filter]
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div>
        <h1 style={{ fontSize: "var(--text-3xl)" }}>Nudges</h1>
        <p className="text-secondary" style={{ fontSize: "var(--text-sm)" }}>
          Risk-tiered approval. Tier 1 (savings/FD/digital) auto-sends. Tier 2 (credit) and
          Tier 3 (mutual fund / insurance) require staff sign-off — RBI DNCR.04, IRDAI and
          SEBI Investment Advisor Regulations.
        </p>
      </div>

      <TierBar tierCounts={tierCounts} />

      <div style={{ display: "flex", gap: 6, borderBottom: "1px solid var(--neutral-200)" }}>
        <TabButton active={tab === "review"} onClick={() => setTab("review")}
          label={`Review Queue${reviewQueue.length ? ` (${reviewQueue.length})` : ""}`} />
        <TabButton active={tab === "log"} onClick={() => setTab("log")}
          label="Engagement Log" />
      </div>

      {notice && (
        <div role="status"
          className={`badge badge-${notice.type === "success" ? "success" :
            notice.type === "danger" ? "danger" : "gold"}`}
          style={{
            position: "fixed", bottom: 24, left: "50%", transform: "translateX(-50%)",
            zIndex: 80, padding: "12px 18px", fontSize: "var(--text-sm)",
            boxShadow: "var(--shadow-lg)", maxWidth: "calc(100vw - 32px)",
          }}>
          {notice.text}
        </div>
      )}

      {loading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[...Array(3)].map((_, i) => <Skeleton key={i} height={120} radius={14} />)}
        </div>
      )}

      {!loading && tab === "review" && (
        <ReviewQueueView items={reviewQueue} onApprove={onApprove} onReject={onReject} />
      )}

      {!loading && tab === "log" && (
        <LogView items={filteredLog} counts={counts} filter={filter} setFilter={setFilter} />
      )}
    </div>
  );
}

function TabButton({ active, onClick, label }) {
  return (
    <button onClick={onClick}
      style={{
        padding: "10px 18px", fontSize: "var(--text-sm)", fontWeight: 600,
        color: active ? "var(--sbi-blue-primary)" : "var(--text-secondary)",
        borderBottom: active ? "2px solid var(--sbi-blue-primary)" : "2px solid transparent",
        marginBottom: -1, transition: "color var(--transition-fast)",
      }}>
      {label}
    </button>
  );
}

function TierBar({ tierCounts }) {
  const total = (tierCounts[1] + tierCounts[2] + tierCounts[3]) || 1;
  const pct = (k) => Math.round((tierCounts[k] / total) * 100);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
      {[1, 2, 3].map((tier) => {
        const m = TIER_META[tier];
        const Icon = m.icon;
        return (
          <Card key={tier} style={{ padding: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <div style={{ width: 28, height: 28, borderRadius: 8, background: m.bg,
                display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icon size={15} color={m.color} />
              </div>
              <div style={{ fontSize: "var(--text-xs)", fontWeight: 600,
                color: "var(--text-secondary)" }}>{m.name}</div>
            </div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
              <span style={{ fontSize: "var(--text-2xl)", fontWeight: 700 }}>
                {tierCounts[tier] || 0}
              </span>
              <span style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>
                {pct(tier)}%
              </span>
            </div>
          </Card>
        );
      })}
    </div>
  );
}

// ─── REVIEW QUEUE ───────────────────────────────────────────────────────────
function ReviewQueueView({ items, onApprove, onReject }) {
  if (items.length === 0) {
    return (
      <Card style={{ textAlign: "center", padding: 40, color: "var(--text-tertiary)" }}>
        <ShieldCheck size={32} color="var(--color-success)" style={{ marginBottom: 8 }} />
        <div style={{ fontSize: "var(--text-base)", fontWeight: 600,
          color: "var(--text-primary)", marginBottom: 4 }}>
          Nothing waiting on you.
        </div>
        <div style={{ fontSize: "var(--text-sm)" }}>
          Tier 2 and Tier 3 nudges that need your sign-off will appear here.
        </div>
      </Card>
    );
  }
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(420px, 1fr))",
      gap: 16 }}>
      {items.map((n) => <ReviewCard key={n.id} n={n} onApprove={onApprove} onReject={onReject} />)}
    </div>
  );
}

function ReviewCard({ n, onApprove, onReject }) {
  const m = TIER_META[n.tier] || TIER_META[2];
  const Icon = m.icon;
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12,
      borderLeft: `4px solid ${m.color}` }}>
      <div className="flex items-center justify-between">
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 30, height: 30, borderRadius: 8, background: m.bg,
            display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Icon size={16} color={m.color} />
          </div>
          <div style={{ fontWeight: 700, fontSize: "var(--text-sm)" }}>{m.name}</div>
        </div>
        <ComplianceBadge n={n} />
      </div>

      <div>
        <div style={{ fontWeight: 700, fontSize: "var(--text-base)" }}>
          {n.product_name || "—"}
        </div>
        <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", marginTop: 2 }}>
          {n.customer_name || n.customer_id} · gap: {n.target_gap || "—"}
        </div>
      </div>

      <p style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", lineHeight: 1.55,
        background: "var(--sbi-blue-subtle)", padding: 10, borderRadius: 10, margin: 0 }}>
        {n.message_draft || ""}
      </p>

      <div style={{ display: "flex", gap: 8, alignItems: "flex-start",
        background: "var(--neutral-50)", padding: 10, borderRadius: 8 }}>
        <Scale size={14} color="var(--text-tertiary)" style={{ marginTop: 2, flexShrink: 0 }} />
        <div style={{ fontSize: 11.5, color: "var(--text-secondary)", lineHeight: 1.5 }}>
          {n.tier_reason}
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: "auto" }}>
        <button className="btn btn-success btn-sm" style={{ flex: 1 }}
          onClick={() => onApprove(n.id)}>
          <Check size={14} /> Approve &amp; send
        </button>
        <button className="btn btn-danger btn-sm" onClick={() => onReject(n.id)}>
          <X size={14} /> Reject
        </button>
      </div>
    </div>
  );
}

// ─── ENGAGEMENT LOG ─────────────────────────────────────────────────────────
function LogView({ items, counts, filter, setFilter }) {
  return (
    <>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {STATUS_FILTERS.map((f) => (
          <button key={f.key} onClick={() => setFilter(f.key)}
            className={`badge ${filter === f.key ? "badge-blue" : "badge-neutral"}`}
            style={{
              cursor: "pointer", padding: "8px 16px",
              border: filter === f.key ? "1px solid var(--sbi-blue-light)" : "1px solid transparent",
            }}>
            {f.label} ({counts[f.key]})
          </button>
        ))}
      </div>

      {items.length === 0 ? (
        <Card style={{ textAlign: "center", padding: 40, color: "var(--text-tertiary)" }}>
          No entries in this view yet.
        </Card>
      ) : (
        <Card style={{ padding: 0, overflow: "hidden" }}>
          <div style={{ display: "grid",
            gridTemplateColumns: "0.6fr 1.4fr 1fr 1fr 1fr 0.8fr", gap: 0,
            fontSize: "var(--text-xs)", fontWeight: 700,
            textTransform: "uppercase", color: "var(--text-tertiary)",
            padding: "12px 16px", borderBottom: "1px solid var(--neutral-200)",
            background: "var(--neutral-50)" }}>
            <span>Tier</span>
            <span>Nudge</span>
            <span>Customer</span>
            <span>Compliance</span>
            <span>Delivery</span>
            <span>When</span>
          </div>
          {items.map((n) => <LogRow key={n.id} n={n} />)}
        </Card>
      )}
    </>
  );
}

function LogRow({ n }) {
  const m = TIER_META[n.tier] || TIER_META[2];
  return (
    <div style={{
      display: "grid", gridTemplateColumns: "0.6fr 1.4fr 1fr 1fr 1fr 0.8fr",
      gap: 0, alignItems: "center", padding: "14px 16px",
      borderBottom: "1px solid var(--neutral-100)", fontSize: "var(--text-sm)",
    }}>
      <span title={m.name} className="badge"
        style={{ background: m.bg, color: m.color, width: "fit-content" }}>
        {m.short}
      </span>
      <div style={{ paddingRight: 16 }}>
        <div style={{ fontWeight: 700 }}>{n.product_name || "—"}</div>
        <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)",
          display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical",
          overflow: "hidden", marginTop: 2 }}>
          {n.message_draft || ""}
        </div>
      </div>
      <div>
        <div style={{ fontWeight: 600 }}>{n.customer_name || n.customer_id}</div>
        <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>
          gap: {n.target_gap || "—"}
        </div>
      </div>
      <ComplianceBadge n={n} />
      <DeliveryBadge n={n} />
      <div style={{ fontSize: "var(--text-xs)", color: "var(--text-secondary)" }}>
        {fmtTime(n.sent_at || n.created_at)}
      </div>
    </div>
  );
}

function ComplianceBadge({ n }) {
  const map = {
    approved: { label: "Approved", icon: ShieldCheck, cls: "badge-success" },
    approved_with_modification: { label: "Approved · modified", icon: ShieldCheck, cls: "badge-info" },
    rejected: { label: "Rejected", icon: ShieldX, cls: "badge-danger" },
    pending: { label: "Pending", icon: ShieldAlert, cls: "badge-neutral" },
  };
  const m = map[n.compliance_status] || map.pending;
  const Icon = m.icon;
  return (
    <span className={`badge ${m.cls}`} style={{ width: "fit-content" }}>
      <Icon size={12} /> {m.label}
    </span>
  );
}

function DeliveryBadge({ n }) {
  const status = n.delivery_status;
  if (status === "sent") {
    return (
      <span className="badge badge-success" style={{ width: "fit-content" }}>
        <Mail size={12} /> sent
      </span>
    );
  }
  if (status === "failed" || status === "not_configured") {
    return (
      <span className="badge badge-danger" style={{ width: "fit-content" }}
        title={n.delivery_error || ""}>
        <AlertTriangle size={12} /> {status}
      </span>
    );
  }
  if (status === "blocked_no_consent") {
    return (
      <span className="badge badge-warning" style={{ width: "fit-content" }}>
        <ShieldAlert size={12} /> no consent
      </span>
    );
  }
  if (status === "blocked_compliance") {
    return (
      <span className="badge badge-warning" style={{ width: "fit-content" }}>
        <ShieldAlert size={12} /> compliance
      </span>
    );
  }
  if (n.requires_review) {
    return (
      <span className="badge badge-gold" style={{ width: "fit-content" }}>
        <Clock size={12} /> review
      </span>
    );
  }
  return (
    <span className="badge badge-neutral" style={{ width: "fit-content" }}>
      <Clock size={12} /> queued
    </span>
  );
}
