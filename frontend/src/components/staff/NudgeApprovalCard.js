"use client";
import { Check, X, Send } from "lucide-react";
import { StatusBadge } from "@/components/common/Badge";
import { FRAME_LABELS, CHANNEL_LABELS } from "@/lib/constants";

export default function NudgeApprovalCard({ nudge, onApprove, onReject, onSend }) {
  const notes = nudge.compliance_notes || {};
  const mods = notes.modifications || [];
  const refs = notes.regulatory_references || [];

  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div className="flex items-center justify-between">
        <div>
          <div style={{ fontWeight: 700 }}>{nudge.product_name}</div>
          <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>
            Priority {nudge.priority} · {(nudge.product_category || "").replace(/_/g, " ")}
          </div>
        </div>
        <StatusBadge status={nudge.compliance_status} />
      </div>

      <p style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", lineHeight: 1.55,
        background: "var(--sbi-blue-subtle)", padding: 12, borderRadius: 10 }}>
        {nudge.message_draft}
      </p>

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {nudge.psychological_frame && <span className="badge badge-gold">{FRAME_LABELS[nudge.psychological_frame] || nudge.psychological_frame}</span>}
        {nudge.channel && <span className="badge badge-blue">{CHANNEL_LABELS[nudge.channel] || nudge.channel}</span>}
        {nudge.expected_conversion && <span className="badge badge-success">{nudge.expected_conversion} conv.</span>}
      </div>

      {mods.length > 0 && (
        <div style={{ fontSize: "var(--text-xs)", color: "var(--color-warning)" }}>
          <strong>Compliance edits:</strong> {mods.join(" ")}
        </div>
      )}
      {refs.length > 0 && (
        <div style={{ fontSize: 11, color: "var(--text-tertiary)" }}>{refs.join(" · ")}</div>
      )}

      <div style={{ display: "flex", gap: 8 }}>
        {nudge.status !== "sent" && (
          <>
            <button className="btn btn-success btn-sm" onClick={() => onSend(nudge.id)}><Send size={14} /> Send</button>
            <button className="btn btn-secondary btn-sm" onClick={() => onApprove(nudge.id)}><Check size={14} /> Approve</button>
            <button className="btn btn-danger btn-sm" onClick={() => onReject(nudge.id)}><X size={14} /> Reject</button>
          </>
        )}
        {nudge.status === "sent" && <span className="badge badge-success"><Check size={13} /> Delivered</span>}
      </div>
    </div>
  );
}
