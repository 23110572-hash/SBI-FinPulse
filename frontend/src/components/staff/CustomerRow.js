"use client";
import { useRouter } from "next/navigation";
import { ChevronRight } from "lucide-react";
import { initials, formatCurrency } from "@/lib/utils";

export default function CustomerRow({ customer }) {
  const router = useRouter();
  return (
    <button onClick={() => router.push(`/staff/customer/${customer.id}`)}
      style={{ display: "flex", alignItems: "center", gap: 14, width: "100%", textAlign: "left",
        padding: "14px 16px", borderBottom: "1px solid var(--neutral-100)", background: "transparent",
        transition: "background var(--transition-fast)" }}
      onMouseEnter={(e) => (e.currentTarget.style.background = "var(--sbi-blue-subtle)")}
      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
      <div style={{ width: 42, height: 42, borderRadius: "50%", background: "var(--gradient-blue)",
        color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700,
        flexShrink: 0, fontSize: "var(--text-sm)" }}>
        {initials(customer.name)}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, fontSize: "var(--text-sm)" }}>{customer.name}</div>
        <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>
          {customer.location} · {customer.persona}
        </div>
      </div>
      <div style={{ textAlign: "right" }}>
        <div style={{ fontSize: "var(--text-sm)", fontWeight: 600 }}>{formatCurrency(customer.monthly_income, true)}/mo</div>
        <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>{customer.income_band}</div>
      </div>
      <ChevronRight size={18} color="var(--text-tertiary)" />
    </button>
  );
}
