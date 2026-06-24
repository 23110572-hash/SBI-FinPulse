"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import AnimatedCounter from "@/components/common/AnimatedCounter";
import { scoreColor, gradeFromScore } from "@/lib/utils";

export default function HealthScoreCard({ score = 0, grade, peerComparison }) {
  const R = 78;
  const CIRC = 2 * Math.PI * R;
  const [offset, setOffset] = useState(CIRC);

  useEffect(() => {
    const t = setTimeout(() => setOffset(CIRC - (score / 100) * CIRC), 120);
    return () => clearTimeout(t);
  }, [score, CIRC]);

  const color = scoreColor(score);
  const label = grade || gradeFromScore(score);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="glass"
      style={{
        borderRadius: "var(--radius-xl)", padding: "28px 24px", textAlign: "center",
        background: "rgba(255,255,255,0.7)", boxShadow: "var(--shadow-lg)",
        border: "1px solid rgba(255,255,255,0.6)",
      }}>
      <div style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", fontWeight: 600,
        textTransform: "uppercase", letterSpacing: 1, marginBottom: 16 }}>
        Financial Health Score
      </div>

      <div style={{ position: "relative", width: 200, height: 200, margin: "0 auto" }}>
        <svg width="200" height="200" style={{ transform: "rotate(-90deg)" }}>
          <circle cx="100" cy="100" r={R} fill="none" stroke="var(--neutral-200)" strokeWidth="14" />
          <motion.circle
            cx="100" cy="100" r={R} fill="none" stroke={color} strokeWidth="14"
            strokeLinecap="round" strokeDasharray={CIRC}
            initial={{ strokeDashoffset: CIRC }} animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.9, ease: [0.4, 0, 0.2, 1] }}
          />
        </svg>
        <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center" }}>
          <div style={{ fontFamily: "var(--font-heading)", fontSize: "3.2rem", fontWeight: 800,
            color, lineHeight: 1 }}>
            <AnimatedCounter value={score} duration={900} />
          </div>
          <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>out of 100</div>
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <span className="badge" style={{ background: `${color}1a`, color, fontSize: "var(--text-sm)", padding: "6px 16px" }}>
          {label}
        </span>
      </div>
      {peerComparison && (
        <p style={{ marginTop: 14, fontSize: "var(--text-sm)", color: "var(--text-secondary)" }}>
          {peerComparison}
        </p>
      )}
    </motion.div>
  );
}
