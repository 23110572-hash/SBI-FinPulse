"use client";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import Logo from "./Logo";
import { CUSTOMER_TABS } from "./BottomNav";

// Desktop-only vertical navigation rail that replaces the bottom tab bar (≥1024px).
export default function NavRail() {
  const pathname = usePathname();
  const router = useRouter();

  // Prefetch sibling tabs once on mount so navigation is instant.
  useEffect(() => {
    CUSTOMER_TABS.forEach((t) => router.prefetch(t.href));
    router.prefetch("/");
  }, [router]);

  return (
    <aside className="nav-rail">
      <div className="nav-rail-brand">
        <Logo />
      </div>

      {CUSTOMER_TABS.map((t) => {
        const active = pathname.startsWith(t.href);
        const Icon = t.icon;
        return (
          <button key={t.href} onClick={() => router.push(t.href)}
            onMouseEnter={() => router.prefetch(t.href)}
            className={`nav-rail-item ${active ? "active" : ""}`}>
            <Icon size={20} strokeWidth={active ? 2.4 : 2} />
            {t.label}
          </button>
        );
      })}

      <button className="nav-rail-switch" onClick={() => router.push("/")}>
        <LogOut size={17} /> Logout
      </button>
    </aside>
  );
}
