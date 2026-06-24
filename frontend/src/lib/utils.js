// Formatters and helpers.

export function formatCurrency(amount, compact = false) {
  if (amount == null || isNaN(amount)) return "₹0";
  const n = Number(amount);
  if (compact) {
    if (Math.abs(n) >= 10000000) return `₹${(n / 10000000).toFixed(2)} Cr`;
    if (Math.abs(n) >= 100000) return `₹${(n / 100000).toFixed(2)} L`;
    if (Math.abs(n) >= 1000) return `₹${(n / 1000).toFixed(1)}K`;
  }
  return `₹${n.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

export function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

export function timeAgo(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

// Score color thresholds: 70+ green, 40-69 amber, <40 red.
export function scoreColor(score) {
  if (score >= 70) return "var(--color-success)";
  if (score >= 40) return "var(--color-warning)";
  return "var(--color-danger)";
}

export function scoreColorLight(score) {
  if (score >= 70) return "var(--color-success-light)";
  if (score >= 40) return "var(--color-warning-light)";
  return "var(--color-danger-light)";
}

export function gradeFromScore(score) {
  if (score >= 80) return "Excellent";
  if (score >= 70) return "Healthy";
  if (score >= 55) return "Fair";
  if (score >= 40) return "Needs Attention";
  return "At Risk";
}

export function statusBadgeClass(status) {
  const map = {
    sent: "badge-success",
    approved: "badge-success",
    approved_with_modification: "badge-warning",
    pending: "badge-warning",
    reviewing: "badge-info",
    rejected: "badge-danger",
    failed: "badge-danger",
  };
  return map[status] || "badge-neutral";
}

export function titleCase(str) {
  if (!str) return "";
  return str.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function initials(name) {
  if (!name) return "?";
  return name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
}
