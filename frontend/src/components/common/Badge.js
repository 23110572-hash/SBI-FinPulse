import { statusBadgeClass, titleCase } from "@/lib/utils";

export default function Badge({ children, variant = "neutral", className = "" }) {
  return <span className={`badge badge-${variant} ${className}`}>{children}</span>;
}

export function StatusBadge({ status }) {
  return <span className={`badge ${statusBadgeClass(status)}`}>{titleCase(status)}</span>;
}
