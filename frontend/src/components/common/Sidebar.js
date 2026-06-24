"use client";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, Users, Bell, BarChart3, LogOut, Menu, X } from "lucide-react";
import Logo from "./Logo";

const NAV = [
  { href: "/staff/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/staff/customers", label: "Customers", icon: Users },
  { href: "/staff/nudges", label: "Nudges", icon: Bell },
  { href: "/staff/analytics", label: "Analytics", icon: BarChart3 },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);

  // Prefetch sibling tabs (and the landing page) once on mount so navigation is instant.
  useEffect(() => {
    NAV.forEach((n) => router.prefetch(n.href));
    router.prefetch("/");
  }, [router]);

  const go = (href) => { router.push(href); setOpen(false); };
  const current = NAV.find((n) => pathname.startsWith(n.href));

  return (
    <>
      {/* Mobile / tablet top bar with hamburger (≤1023px) */}
      <header className="staff-topbar">
        <button className="staff-burger" aria-label="Open menu" onClick={() => setOpen(true)}>
          <Menu size={24} />
        </button>
        <Logo light showText={false} size={30} />
        <span style={{ fontWeight: 700, fontSize: "var(--text-base)" }}>
          {current?.label || "FinPulse"}
        </span>
      </header>

      {/* Scrim behind the drawer */}
      <div className={`staff-scrim ${open ? "show" : ""}`} onClick={() => setOpen(false)} />

      <aside className={`staff-sidebar ${open ? "open" : ""}`}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "4px 8px 20px" }}>
          <Logo light />
          <button className="staff-sidebar-close" aria-label="Close menu" onClick={() => setOpen(false)}
            style={{ color: "#fff", padding: 4 }}>
            <X size={22} />
          </button>
        </div>

        {NAV.map((n) => {
          const active = pathname.startsWith(n.href);
          const Icon = n.icon;
          return (
            <button key={n.href} onClick={() => go(n.href)}
              style={{
                display: "flex", alignItems: "center", gap: 12, padding: "12px 14px",
                borderRadius: "var(--radius-md)", color: "#fff", textAlign: "left",
                background: active ? "rgba(255,255,255,0.16)" : "transparent",
                fontWeight: active ? 700 : 500, fontSize: "var(--text-sm)",
                transition: "background var(--transition-fast)",
              }}>
              <Icon size={19} />
              {n.label}
            </button>
          );
        })}

        <div style={{ marginTop: "auto" }}>
          <button onClick={() => go("/")}
            style={{
              display: "flex", alignItems: "center", gap: 10, padding: "12px 14px",
              borderRadius: "var(--radius-md)", color: "rgba(255,255,255,0.8)",
              fontSize: "var(--text-sm)", border: "1px solid rgba(255,255,255,0.2)", width: "100%",
            }}>
            <LogOut size={17} /> Logout
          </button>
        </div>
      </aside>
    </>
  );
}
