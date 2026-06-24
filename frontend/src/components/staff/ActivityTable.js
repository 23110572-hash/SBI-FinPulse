"use client";
import { StatusBadge } from "@/components/common/Badge";
import { timeAgo, titleCase } from "@/lib/utils";

export default function ActivityTable({ activity = [] }) {
  return (
    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
      <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--neutral-200)" }}>
        <h3 style={{ fontSize: "var(--text-lg)" }}>Recent Agent Activity</h3>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table className="table-stack" style={{ width: "100%", borderCollapse: "collapse", fontSize: "var(--text-sm)" }}>
          <thead>
            <tr style={{ textAlign: "left", color: "var(--text-tertiary)", fontSize: "var(--text-xs)",
              textTransform: "uppercase", letterSpacing: 0.5 }}>
              <Th>Customer</Th><Th>Event Detected</Th><Th>Product Suggested</Th><Th>Status</Th><Th>Time</Th>
            </tr>
          </thead>
          <tbody>
            {activity.length === 0 && (
              <tr><td colSpan={5} style={{ padding: 30, textAlign: "center", color: "var(--text-tertiary)" }}>
                No activity yet. Run an analysis from a customer page.
              </td></tr>
            )}
            {activity.map((a, i) => (
              <tr key={i} style={{ borderTop: "1px solid var(--neutral-100)" }}>
                <Td data-label="Customer"><strong>{a.customer_name}</strong></Td>
                <Td data-label="Event">{titleCase(a.event)}</Td>
                <Td data-label="Product">{a.product}</Td>
                <Td data-label="Status"><StatusBadge status={a.status} /></Td>
                <Td data-label="Time" style={{ color: "var(--text-tertiary)" }}>{timeAgo(a.time)}</Td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const Th = ({ children }) => <th style={{ padding: "12px 20px", fontWeight: 600 }}>{children}</th>;
const Td = ({ children, style, ...props }) => <td style={{ padding: "13px 20px", ...style }} {...props}>{children}</td>;
