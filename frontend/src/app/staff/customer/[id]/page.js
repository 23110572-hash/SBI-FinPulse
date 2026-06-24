"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, RefreshCw, Sparkles } from "lucide-react";
import Card from "@/components/common/Card";
import Button from "@/components/common/Button";
import { initials, formatCurrency, titleCase } from "@/lib/utils";
import { useCustomer } from "@/hooks/useCustomer";
import { useAnalysis, useAnalysisStream } from "@/hooks/useAnalysis";
import AgentReasoningView from "@/components/staff/AgentReasoningView";
import { api } from "@/lib/api";

export default function CustomerDetail() {
  const { id } = useParams();
  const router = useRouter();
  const { customer } = useCustomer(id);
  const { analysis, reload } = useAnalysis(id);
  const stream = useAnalysisStream(id);
  const [messages, setMessages] = useState([]);

  useEffect(() => { if (stream.result) reload(); }, [stream.result, reload]);
  useEffect(() => { setMessages(analysis?.final_messages || []); }, [analysis]);

  const running = stream.running;
  const storedLogs = analysis?.agent_logs || [];
  const finalMessages = stream.result?.final_messages || messages;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <button onClick={() => router.push("/staff/customers")}
        style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--sbi-blue-light)",
          fontWeight: 600, fontSize: "var(--text-sm)" }}>
        <ArrowLeft size={16} /> Back to customers
      </button>

      {/* profile header */}
      <Card>
        <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
          <div style={{ width: 60, height: 60, borderRadius: "50%", background: "var(--gradient-blue)",
            color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700,
            fontSize: "var(--text-xl)" }}>
            {initials(customer?.name)}
          </div>
          <div style={{ flex: 1, minWidth: 200 }}>
            <h2 style={{ fontSize: "var(--text-2xl)" }}>{customer?.name}</h2>
            <p className="text-secondary" style={{ fontSize: "var(--text-sm)" }}>
              {customer?.age} · {customer?.location} · {customer?.persona} · {formatCurrency(customer?.monthly_income)}/mo
            </p>
          </div>
          <Button onClick={stream.start} disabled={running}>
            {running ? <RefreshCw size={16} className="spin" /> : <Sparkles size={16} />}
            {running ? "Agents running..." : storedLogs.length ? "Re-analyze" : "Run analysis"}
          </Button>
        </div>
        {customer && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 14 }}>
            {customer.products_held?.map((p) => (
              <span key={p} className="badge badge-blue">{titleCase(p)}</span>
            ))}
          </div>
        )}
      </Card>

      <div className="staff-split">
        {/* reasoning pipeline */}
        <div>
          <h3 style={{ fontSize: "var(--text-lg)", marginBottom: 16 }}>Agent Reasoning Pipeline</h3>
          {storedLogs.length === 0 && !running && Object.keys(stream.steps).length === 0 ? (
            <Card style={{ textAlign: "center", padding: 28, color: "var(--text-tertiary)" }}>
              <Sparkles size={28} color="var(--sbi-blue-light)" style={{ margin: "0 auto 10px" }} />
              <p style={{ fontSize: "var(--text-sm)" }}>No analysis yet. Click "Run analysis" to watch the agents work in real time.</p>
            </Card>
          ) : (
            <AgentReasoningView
              plan={stream.stepPlan.length ? stream.stepPlan : undefined}
              steps={stream.steps} storedLogs={storedLogs} />
          )}
          {stream.error && <p style={{ color: "var(--color-danger)", fontSize: "var(--text-sm)" }}>{stream.error}</p>}
        </div>

        {/* generated messages */}
        <div style={{ position: "sticky", top: 20 }}>
          <h3 style={{ fontSize: "var(--text-lg)", marginBottom: 16 }}>Customer Messages</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {finalMessages.length === 0 && (
              <Card style={{ color: "var(--text-tertiary)", fontSize: "var(--text-sm)", textAlign: "center" }}>
                Approved messages will appear here.
              </Card>
            )}
            {finalMessages.map((m, i) => (
              <Card key={i} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <div className="flex items-center justify-between">
                  <span style={{ fontWeight: 700, fontSize: "var(--text-sm)" }}>{m.product}</span>
                  <span className="badge badge-blue">{m.channel}</span>
                </div>
                <p style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", lineHeight: 1.55 }}>{m.message}</p>
                <div style={{ display: "flex", gap: 8 }}>
                  <button className="btn btn-success btn-sm" onClick={() => router.push("/staff/nudges")}>Manage</button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
