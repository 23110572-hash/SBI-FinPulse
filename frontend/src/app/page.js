"use client";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Smartphone, Building2, ArrowRight } from "lucide-react";
import Logo from "@/components/common/Logo";

export default function LandingPage() {
  const router = useRouter();

  return (
    <div style={{ minHeight: "100vh", background: "var(--gradient-header)", display: "flex",
      alignItems: "center", justifyContent: "center", padding: 24 }}>
      <motion.div
        initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
        style={{ maxWidth: 460, width: "100%", textAlign: "center" }}>
        <div style={{ display: "flex", justifyContent: "center", marginBottom: 20 }}>
          <Logo light size={56} showText={false} />
        </div>
        <h1 style={{ color: "#fff", fontSize: "2.4rem", marginBottom: 8 }}>SBI FinPulse</h1>
        <p style={{ color: "rgba(255,255,255,0.78)", marginBottom: 40, fontSize: "1.05rem" }}>
          Agentic AI for proactive, hyper-personalised banking engagement.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <ChoiceCard
            icon={<Smartphone size={26} />} title="Customer App"
            subtitle="Health score, insights & AI chat"
            onClick={() => router.push("/customer/home")} />
          <ChoiceCard
            icon={<Building2 size={26} />} title="Bank Staff Dashboard"
            subtitle="Engagement monitoring & audit log"
            onClick={() => router.push("/staff/dashboard")} />
        </div>
      </motion.div>
    </div>
  );
}

function ChoiceCard({ icon, title, subtitle, onClick }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={onClick}
      className="glass"
      style={{ display: "flex", alignItems: "center", gap: 16, padding: 20,
        borderRadius: "var(--radius-lg)", color: "#fff", textAlign: "left", width: "100%" }}>
      <div style={{ width: 52, height: 52, borderRadius: "var(--radius-md)",
        background: "rgba(255,255,255,0.18)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        {icon}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700, fontSize: "1.05rem" }}>{title}</div>
        <div style={{ fontSize: "0.85rem", color: "rgba(255,255,255,0.72)" }}>{subtitle}</div>
      </div>
      <ArrowRight size={20} />
    </motion.button>
  );
}
