"use client";
import { Mail, ShieldCheck, ShieldOff, Lock } from "lucide-react";
import Card from "@/components/common/Card";
import { useConsent } from "@/hooks/useConsent";

/**
 * DPDP consent control. The customer decides whether FinPulse may proactively
 * reach out using their financial data. Email is the only outbound channel —
 * nothing proactive is sent without an active consent here.
 */
export default function ConsentCard({ customerId }) {
  const { consents, active, loading, busy, grant, revoke } = useConsent(customerId);
  const current = consents.find((c) => c.status === "granted") || null;

  return (
    <Card>
      <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 38, height: 38, borderRadius: 10, display: "flex", alignItems: "center",
            justifyContent: "center",
            background: active ? "var(--sbi-blue-subtle)" : "var(--bg-muted, #f1f1f4)",
            color: active ? "var(--sbi-blue, #1A237E)" : "var(--text-tertiary)",
          }}>
            {active ? <ShieldCheck size={20} /> : <ShieldOff size={20} />}
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: "var(--text-base)" }}>Proactive engagement</div>
            <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>
              DPDP Act 2023 · consent &amp; purpose limitation
            </div>
          </div>
        </div>
        <span className={`badge ${active ? "badge-success" : "badge-neutral"}`}>
          {active ? "Active" : "Off"}
        </span>
      </div>

      <p style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", lineHeight: 1.55,
        marginBottom: 14 }}>
        {active
          ? "FinPulse may analyse your transactions and reach out by email with timely, relevant guidance. You can withdraw this anytime."
          : "Allow FinPulse to analyse your transactions and email you timely, relevant financial guidance."}
      </p>

      {active && current && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 14 }}>
          <span className="badge badge-blue">
            <Mail size={12} /> Email
          </span>
        </div>
      )}

      {current?.expires_at && active && (
        <div style={{ fontSize: 11, color: "var(--text-tertiary)", marginBottom: 12,
          display: "flex", alignItems: "center", gap: 6 }}>
          <Lock size={11} /> Valid until {new Date(current.expires_at).toLocaleDateString()}
        </div>
      )}

      <div style={{ display: "flex", gap: 8 }}>
        {active ? (
          <button className="btn btn-danger btn-sm" disabled={busy || loading} onClick={revoke}>
            <ShieldOff size={14} /> Withdraw consent
          </button>
        ) : (
          <button className="btn btn-primary btn-sm" disabled={busy || loading} onClick={() => grant()}>
            <ShieldCheck size={14} /> Allow proactive engagement
          </button>
        )}
      </div>
    </Card>
  );
}
