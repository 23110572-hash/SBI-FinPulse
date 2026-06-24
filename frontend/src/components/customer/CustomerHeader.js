"use client";
import { useState } from "react";
import { ChevronDown } from "lucide-react";
import Logo from "@/components/common/Logo";
import { useCustomers } from "@/hooks/useCustomer";

// Gradient header with a built-in customer switcher (demo convenience — no auth).
export default function CustomerHeader({ name, subtitle, customerId, onSwitch, children }) {
  const [open, setOpen] = useState(false);
  const { customers } = useCustomers();

  // The dropdown is rendered OUTSIDE the .gradient-header element because that
  // element uses `overflow: hidden` (for its rounded glow), which would clip
  // the menu to the header height and break scrolling. The wrapper below has
  // no overflow clipping, so the full, scrollable list shows correctly.
  return (
    <div style={{ position: "relative" }}>
      <div className="gradient-header">
        <div className="flex items-center justify-between" style={{ marginBottom: children ? 20 : 0 }}>
          <div>
            <div style={{ fontSize: "var(--text-sm)", color: "rgba(255,255,255,0.75)" }}>{subtitle || "Welcome back"}</div>
            <button onClick={() => setOpen(!open)}
              style={{ display: "flex", alignItems: "center", gap: 8, color: "#fff",
                background: "rgba(255,255,255,0.14)", border: "1px solid rgba(255,255,255,0.22)",
                padding: "5px 8px 5px 12px", borderRadius: "var(--radius-full)", marginTop: 4,
                transition: "background var(--transition-fast)" }}>
              <h2 style={{ fontSize: "var(--text-2xl)", color: "#fff" }}>{name || "..."}</h2>
              <ChevronDown size={20} color="#fff"
                style={{ transform: open ? "rotate(180deg)" : "none", transition: "transform var(--transition-base)" }} />
            </button>
          </div>
          <Logo light showText={false} size={40} />
        </div>
        {children}
      </div>

      {open && (
        <>
          {/* click-outside backdrop to dismiss the menu */}
          <div onClick={() => setOpen(false)}
            style={{ position: "fixed", inset: 0, zIndex: 55 }} />
          <div className="card" style={{ position: "absolute", left: 24, right: 24, top: 88, zIndex: 60,
            maxHeight: 360, overflowY: "auto", padding: 8, boxShadow: "var(--shadow-xl)" }}>
            <div style={{ fontSize: "var(--text-xs)", fontWeight: 700, color: "var(--text-tertiary)",
              textTransform: "uppercase", letterSpacing: 0.5, padding: "8px 12px 6px" }}>
              Switch account
            </div>
            {customers.map((c) => (
              <button key={c.id} onClick={() => { onSwitch(c.id); setOpen(false); }}
                style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%", padding: "10px 12px",
                  borderRadius: 8, background: c.id === customerId ? "var(--sbi-blue-subtle)" : "transparent",
                  color: "var(--text-primary)" }}>
                <span style={{ fontWeight: 600, fontSize: "var(--text-sm)" }}>{c.name}</span>
                <span style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>{c.persona}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
