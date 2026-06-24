// Stylised SBI-inspired keyhole mark + wordmark (original, not the official logo).
export default function Logo({ size = 34, light = false, showText = true }) {
  const ring = light ? "#ffffff" : "#1A237E";
  const fill = light ? "rgba(255,255,255,0.18)" : "#E8EAF6";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <svg width={size} height={size} viewBox="0 0 48 48" fill="none" aria-label="FinPulse">
        <circle cx="24" cy="24" r="22" fill={fill} stroke={ring} strokeWidth="2.5" />
        <circle cx="24" cy="18" r="5" fill={ring} />
        <rect x="21" y="20" width="6" height="13" rx="3" fill={ring} />
        <path d="M11 30 L18 30 L21 24 L26 34 L29 28 L37 28" stroke={light ? "#C49B2A" : "#3F51B5"}
          strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      </svg>
      {showText && (
        <div style={{ lineHeight: 1 }}>
          <div style={{ fontFamily: "var(--font-heading)", fontWeight: 800, fontSize: 17,
            color: light ? "#fff" : "var(--sbi-blue-primary)" }}>
            FinPulse
          </div>
          <div style={{ fontSize: 9.5, letterSpacing: 2, textTransform: "uppercase",
            color: light ? "rgba(255,255,255,0.7)" : "var(--text-tertiary)" }}>
            by SBI
          </div>
        </div>
      )}
    </div>
  );
}
