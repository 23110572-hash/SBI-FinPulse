export default function Skeleton({ width = "100%", height = 16, radius = 8, style = {} }) {
  return (
    <div
      className="skeleton"
      style={{ width, height, borderRadius: radius, ...style }}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <Skeleton width="60%" height={20} />
      <Skeleton width="100%" height={14} />
      <Skeleton width="90%" height={14} />
      <Skeleton width="40%" height={32} radius={12} />
    </div>
  );
}

/**
 * Full-height placeholder that approximates a content page's footprint, so a
 * first/uncached load doesn't collapse the layout and then jump (no CLS).
 */
export function PageSkeleton({ cards = 3 }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12, alignItems: "center" }}>
        <Skeleton width={140} height={140} radius={999} />
        <Skeleton width="50%" height={18} />
        <Skeleton width="70%" height={12} />
      </div>
      {[...Array(cards)].map((_, i) => <SkeletonCard key={i} />)}
    </div>
  );
}
