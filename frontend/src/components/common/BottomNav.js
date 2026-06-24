"use client";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Home, Sparkles, MessageCircle, User } from "lucide-react";

export const CUSTOMER_TABS = [
  { href: "/customer/home", label: "Home", icon: Home },
  { href: "/customer/insights", label: "Insights", icon: Sparkles },
  { href: "/customer/chat", label: "Chat", icon: MessageCircle },
  { href: "/customer/profile", label: "Profile", icon: User },
];

export default function BottomNav() {
  const pathname = usePathname();
  const router = useRouter();

  // Prefetch sibling tabs once on mount so navigation is instant.
  useEffect(() => {
    CUSTOMER_TABS.forEach((t) => router.prefetch(t.href));
  }, [router]);

  return (
    <nav className="bottom-nav" style={{
      position: "sticky", bottom: 0, left: 0, right: 0, zIndex: 50,
      background: "rgba(255,255,255,0.92)", backdropFilter: "blur(12px)",
      borderTop: "1px solid var(--neutral-200)",
      padding: "8px 4px calc(8px + env(safe-area-inset-bottom))",
    }}>
      {CUSTOMER_TABS.map((t) => {
        const active = pathname.startsWith(t.href);
        const Icon = t.icon;
        return (
          <button key={t.href} onClick={() => router.push(t.href)}
            style={{
              flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4,
              padding: "6px 0", color: active ? "var(--sbi-blue-primary)" : "var(--text-tertiary)",
              transition: "color var(--transition-fast)",
            }}>
            <Icon size={22} strokeWidth={active ? 2.4 : 2} />
            <span style={{ fontSize: 10.5, fontWeight: active ? 700 : 500 }}>{t.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
