"use client";
import AgentStepCard from "./AgentStepCard";

const DEFAULT_PLAN = [
  { step: "profile", agent: "Customer Profiler" },
  { step: "wellness", agent: "Financial Wellness Advisor" },
  { step: "nudge", agent: "Nudge Strategist" },
  { step: "compliance", agent: "Compliance Officer" },
  { step: "generate", agent: "Conversation Agent" },
];

// steps: { stepName: { status, log } }  |  logsFromStored: [{step, status, output, summary, agent}]
export default function AgentReasoningView({ plan = DEFAULT_PLAN, steps = {}, storedLogs = [] }) {
  const logByStep = {};
  storedLogs.forEach((l) => { logByStep[l.step] = l; });

  return (
    <div>
      {plan.map((p, i) => {
        const live = steps[p.step];
        const stored = logByStep[p.step];
        const status = live?.status || (stored ? "complete" : "pending");
        const log = live?.log || stored || null;
        return (
          <AgentStepCard key={p.step} step={p.step} meta={p}
            status={status} log={log} isLast={i === plan.length - 1} />
        );
      })}
    </div>
  );
}
