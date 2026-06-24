import BottomNav from "@/components/common/BottomNav";
import NavRail from "@/components/common/NavRail";
import { ShieldCheck, Sparkles } from "lucide-react";

export default function CustomerLayout({ children }) {
  return (
    <div className="customer-shell">
      <NavRail />

      <div className="customer-stage">
        <main className="customer-surface">
          <div className="customer-content">{children}</div>
          <BottomNav />
        </main>

        {/* Contextual info panel — fills the viewport on wide screens (≥1280px) */}
        <aside className="customer-aside" aria-hidden="true">
          <div className="aside-hero">
            <Sparkles size={22} />
            <h3 style={{ color: "#fff", fontSize: "var(--text-lg)", margin: "10px 0 6px" }}>
              Agentic AI, working for you
            </h3>
            <p style={{ fontSize: "var(--text-sm)", color: "rgba(255,255,255,0.82)", lineHeight: 1.55 }}>
              FinPulse analyses your finances, spots life events and surfaces the next best step —
              proactively and privately.
            </p>
          </div>

          <div className="aside-card">
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <ShieldCheck size={18} color="var(--color-success)" />
              <span style={{ fontWeight: 700, fontSize: "var(--text-sm)" }}>Private &amp; compliant</span>
            </div>
            <p style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", lineHeight: 1.55 }}>
              Every insight respects RBI guidelines and the DPDP Act. Your data never leaves the bank&apos;s
              secure environment.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
