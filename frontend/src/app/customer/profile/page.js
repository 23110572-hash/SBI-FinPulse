"use client";
import { User, MapPin, Briefcase, Wallet, CheckCircle2, Circle } from "lucide-react";
import { useCustomerId, useCustomer } from "@/hooks/useCustomer";
import { formatCurrency, titleCase, initials } from "@/lib/utils";
import Card from "@/components/common/Card";
import ConsentCard from "@/components/customer/ConsentCard";
import { PageSkeleton } from "@/components/common/Skeleton";

export default function ProfilePage() {
  const [customerId] = useCustomerId();
  const { customer, loading } = useCustomer(customerId);

  return (
    <div>
      <div className="gradient-header" style={{ textAlign: "center", paddingBottom: 40 }}>
        <div style={{ width: 76, height: 76, borderRadius: "50%", background: "rgba(255,255,255,0.18)",
          display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 12px",
          fontSize: 26, fontWeight: 700, fontFamily: "var(--font-heading)" }}>
          {initials(customer?.name)}
        </div>
        <h2 style={{ fontSize: "var(--text-2xl)" }}>{customer?.name || "..."}</h2>
        <p style={{ color: "rgba(255,255,255,0.78)", fontSize: "var(--text-sm)" }}>{customer?.persona}</p>
      </div>

      <div className="page-pad" style={{ marginTop: -24, display: "flex", flexDirection: "column", gap: 16 }}>
        {loading && !customer && <PageSkeleton cards={2} />}
        {customer && (
          <>
            <Card>
              <h3 style={{ fontSize: "var(--text-lg)", marginBottom: 14 }}>Profile</h3>
              <Row icon={User} label="Age" value={`${customer.age} years`} />
              <Row icon={MapPin} label="Location" value={customer.location} />
              <Row icon={Briefcase} label="Income band" value={customer.income_band} />
              <Row icon={Wallet} label="Monthly income" value={formatCurrency(customer.monthly_income)} />
              <Row icon={Wallet} label="Current balance" value={formatCurrency(customer.current_balance, true)} />
            </Card>

            <Card>
              <h3 style={{ fontSize: "var(--text-lg)", marginBottom: 14 }}>Your SBI Products</h3>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 16 }}>
                {customer.products_held.map((p) => (
                  <span key={p} className="badge badge-success"><CheckCircle2 size={13} /> {titleCase(p)}</span>
                ))}
              </div>
              <div style={{ fontSize: "var(--text-sm)", fontWeight: 600, color: "var(--text-tertiary)", marginBottom: 8 }}>
                Not yet held
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {customer.products_not_held.map((p) => (
                  <span key={p} className="badge badge-neutral"><Circle size={11} /> {titleCase(p)}</span>
                ))}
              </div>
            </Card>

            <Card>
              <h3 style={{ fontSize: "var(--text-lg)", marginBottom: 14 }}>Preferences</h3>
              <Row label="Risk appetite" value={titleCase(customer.risk_appetite)} />
              <Row label="Digital activity" value={titleCase(customer.digital_activity)} />
              <Row label="Savings rate" value={`${customer.savings_rate}%`} />
            </Card>

            <ConsentCard customerId={customerId} />
          </>
        )}
      </div>
    </div>
  );
}

function Row({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center justify-between" style={{ padding: "9px 0" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, color: "var(--text-secondary)" }}>
        {Icon && <Icon size={16} />}
        <span style={{ fontSize: "var(--text-sm)" }}>{label}</span>
      </div>
      <span style={{ fontSize: "var(--text-sm)", fontWeight: 600 }}>{value}</span>
    </div>
  );
}
