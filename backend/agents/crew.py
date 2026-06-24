"""SBI FinPulse Engagement Crew (CrewAI).

Five LLM agents, each using real tools, executed as discrete steps so the
pipeline can be streamed step-by-step to the staff "Agent Reasoning View":

  1. Profiler (Groq)               -> customer profile + life events
  2. Wellness (Groq)               -> 0-100 financial health score
  3. Nudge Strategist (Gemini Pro) -> personalised nudges (RAG)
  4. Compliance (Gemini Pro)       -> RBI/DPDP/IRDAI validation
  5. Conversation (Gemini Flash)   -> customer-ready messages

Live-LLM only. Requires GEMINI_API_KEY and GROQ_API_KEY.
"""
from __future__ import annotations

import datetime as dt
import json

from agents.compliance_agent import build_compliance_agent
from agents.crew_models import (ComplianceOutput, MessagesOutput,
                                NudgePlanOutput, ProfileOutput, WellnessOutput)
from agents.llms import get_groq_llm
from agents.nudge_agent import build_nudge_agent
from agents.profiler_agent import build_profiler_agent
from agents.repository import get_customer
from agents.wellness_agent import build_wellness_agent
from config import settings

# Agent display metadata. The underlying LLM is intentionally NOT exposed
# to the UI — clients see only the agent role.
STEP_META = {
    "profile": ("Customer Profiler",),
    "wellness": ("Financial Wellness Advisor",),
    "nudge": ("Nudge Strategist",),
    "compliance": ("Compliance Officer",),
    "generate": ("Conversation Agent",),
}


def _ts() -> str:
    return dt.datetime.utcnow().isoformat() + "Z"


def _make_step_log(step: str, output: dict, raw: str) -> dict:
    (agent,) = STEP_META[step]
    return {"step": step, "agent": agent, "status": "complete",
            "summary": (raw[:280] if raw else "Completed."),
            "output": output, "timestamp": _ts()}


def _run_task(agent, task) -> dict:
    """Run a single agent+task as a one-shot crew and return structured dict."""
    from crewai import Crew, Process
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=settings.agent_verbose)
    crew.kickoff()
    return _output_dict(task), getattr(task.output, "raw", "") if task.output else ""


def _output_dict(task) -> dict:
    out = task.output
    if out is None:
        return {}
    if getattr(out, "pydantic", None) is not None:
        return out.pydantic.model_dump()
    if getattr(out, "json_dict", None):
        return out.json_dict
    raw = getattr(out, "raw", str(out))
    try:
        return json.loads(raw)
    except Exception:
        return {"raw": raw}


def _build_conversation_agent():
    from crewai import Agent

    from agents.tools.rag_search import get_crewai_tool as rag_tool
    return Agent(
        role="Empathetic Financial Companion",
        goal="Deliver approved nudges through natural, warm, human-like messages.",
        backstory=("You are FinPulse AI, a friendly financial companion for SBI customers. You "
                   "speak warmly, explain simply, respect a 'no', and support Hindi and English."),
        tools=[t for t in (rag_tool(),) if t is not None],
        llm=get_groq_llm(temperature=0.6, slot=3),
        verbose=settings.agent_verbose,
        allow_delegation=False,
    )


# --------------------------- individual steps ------------------------------
def step_profile(customer_id: str) -> tuple[dict, str]:
    from crewai import Task
    customer = get_customer(customer_id)
    if not customer:
        raise ValueError(f"Customer {customer_id} not found")
    task = Task(
        description=(
            f"Analyze ALL transactions for customer {customer_id}. Use the Transaction Analyzer "
            f"tool (input: '{customer_id}') and the Life Event Detector tool (input: "
            f"'{customer_id}'). The customer's static profile is: {json.dumps(customer)}. Combine "
            f"the tool outputs with this static data into a complete profile: spending categories, "
            f"month-over-month trends, detected life events with confidence, and product gaps. "
            f"IMPORTANT: copy the Life Event Detector output verbatim into life_events_detected — "
            f"do not summarise, omit or rewrite any of its entries."
        ),
        expected_output="A complete customer profile JSON matching the ProfileOutput schema.",
        agent=build_profiler_agent(),
        output_pydantic=ProfileOutput,
    )
    profile, raw = _run_task(task.agent, task)

    # Belt-and-suspenders: the deterministic life-event detector is the
    # source of truth. Re-merge its output so the LLM can't drop events
    # by accident when synthesising the final ProfileOutput JSON.
    from agents.repository import get_transactions
    from agents.tools.life_event_detector import detect_life_events
    from agents.tools.transaction_analyzer import analyze_transactions

    detected = detect_life_events(get_transactions(customer_id), customer or {})
    if detected:
        existing = profile.get("life_events_detected") or []
        seen = {e.get("event") for e in existing if isinstance(e, dict)}
        for ev in detected:
            if ev.get("event") not in seen:
                existing.append(ev)
                seen.add(ev.get("event"))
        profile["life_events_detected"] = existing

    # Authoritative financial facts come from the SOURCE record + deterministic
    # transaction analyzer — NEVER from the LLM. Models routinely drop or
    # mangle exact figures (balance, income, savings rate, products), which
    # would crater the wellness score even for a customer with a healthy
    # balance. Overwrite them so scoring is computed on real numbers.
    if customer:
        txn_stats = analyze_transactions(get_transactions(customer_id))
        profile["monthly_income"] = customer.get("monthly_income") or profile.get("monthly_income", 0)
        profile["current_balance"] = customer.get("current_balance") or profile.get("current_balance", 0)
        profile["savings_rate"] = customer.get("savings_rate") or profile.get("savings_rate", 0.0)
        profile["products_held"] = customer.get("products_held") or profile.get("products_held", [])
        profile["products_not_held"] = customer.get("products_not_held") or profile.get("products_not_held", [])
        # spending buckets + monthly spend straight from the analyzer (has the
        # "emi" / "investments" keys the wellness calculator looks for)
        profile["spending_categories"] = (txn_stats.get("spending_categories")
                                          or profile.get("spending_categories", {}))
        profile["monthly_spending"] = (txn_stats.get("monthly_spending")
                                       or customer.get("monthly_spending")
                                       or profile.get("monthly_spending", 0))
        # static descriptors too — keeps the UI accurate
        for f in ("name", "age", "location", "persona", "income_band",
                  "risk_appetite", "digital_activity"):
            if customer.get(f) is not None:
                profile[f] = customer[f]

    return profile, raw


def step_wellness(profile: dict) -> tuple[dict, str]:
    from crewai import Task
    task = Task(
        description=(
            "Calculate a financial health score (0-100) for this customer profile. Call the "
            "Wellness Calculator tool passing this profile JSON as input:\n"
            f"{json.dumps(profile)}\n"
            "Break the score down by savings, emergency fund, insurance, investments and debt. "
            "Identify critical gaps and quick wins, and add a peer comparison statement."
        ),
        expected_output="A wellness assessment JSON matching the WellnessOutput schema.",
        agent=build_wellness_agent(),
        output_pydantic=WellnessOutput,
    )
    wellness, raw = _run_task(task.agent, task)

    # The SCORE is deterministic. The LLM is asked to call the calculator and
    # reproduce its JSON, but it can drift when transcribing — so recompute the
    # numbers ourselves and make them authoritative. The LLM run still powers
    # the live reasoning view; only the figures are pinned to the real math.
    from agents.tools.wellness_calculator import calculate_wellness
    truth = calculate_wellness(profile)
    wellness = wellness if isinstance(wellness, dict) else {}
    wellness["customer_id"] = profile.get("customer_id") or wellness.get("customer_id")
    wellness["overall_score"] = truth["overall_score"]
    wellness["grade"] = truth["grade"]
    wellness["breakdown"] = truth["breakdown"]
    # keep the LLM's narrative if it produced one, else fall back to deterministic
    if not wellness.get("critical_gaps"):
        wellness["critical_gaps"] = truth["critical_gaps"]
    if not wellness.get("quick_wins"):
        wellness["quick_wins"] = truth["quick_wins"]
    if not wellness.get("peer_comparison"):
        wellness["peer_comparison"] = truth["peer_comparison"]
    return wellness, raw


def step_nudge(profile: dict, wellness: dict) -> tuple[dict, str]:
    from crewai import Task
    task = Task(
        description=(
            "Design up to 3 personalised nudges for this customer.\n"
            f"PROFILE: {json.dumps(profile)}\n"
            f"WELLNESS: {json.dumps(wellness)}\n"
            "For each critical gap or life event, use the SBI Knowledge Search tool to find the "
            "best matching SBI product with REAL names and details. Choose a behavioural frame "
            "(loss_aversion, social_proof, anchoring, urgency) and an optimal timing strategy. "
            "Set channel='email' for every nudge — email is the only proactive channel "
            "FinPulse uses. Draft a warm personalised message under 60 words using the "
            "customer's first name and specific numbers from the profile."
        ),
        expected_output="A nudge plan JSON matching the NudgePlanOutput schema.",
        agent=build_nudge_agent(),
        output_pydantic=NudgePlanOutput,
    )
    return _run_task(task.agent, task)


def step_compliance(nudge_plan: dict) -> tuple[dict, str]:
    from crewai import Task
    task = Task(
        description=(
            "Validate each proposed nudge against regulations.\n"
            f"NUDGE PLAN: {json.dumps(nudge_plan)}\n"
            "Use the SBI Knowledge Search tool to consult RBI Fair Practices, DPDP Act and IRDAI "
            "rules, and the Compliance Checker tool (pass each nudge JSON) to validate. For each "
            "nudge set status to approved, approved_with_modification or rejected, list required "
            "modifications and cite regulatory references. Flag misselling / guaranteed-return "
            "language."
        ),
        expected_output="A compliance report JSON matching the ComplianceOutput schema.",
        agent=build_compliance_agent(),
        output_pydantic=ComplianceOutput,
    )
    return _run_task(task.agent, task)


def step_generate(nudge_plan: dict, compliance: dict) -> tuple[dict, str]:
    from crewai import Task
    task = Task(
        description=(
            "Craft natural, warm, conversational customer-ready messages from the APPROVED nudges "
            "(status approved or approved_with_modification). Skip rejected nudges. Apply every "
            "required compliance modification by appending the mandatory disclaimers.\n"
            f"NUDGE PLAN: {json.dumps(nudge_plan)}\n"
            f"COMPLIANCE: {json.dumps(compliance)}\n"
            "Reference the customer's specific situation and include accurate SBI product details."
        ),
        expected_output="Customer-ready messages JSON matching the MessagesOutput schema.",
        agent=_build_conversation_agent(),
        output_pydantic=MessagesOutput,
    )
    return _run_task(task.agent, task)


# --------------------------- orchestration ---------------------------------
def run_crew(customer_id: str, on_step=None) -> dict:
    """Run the full pipeline step-by-step.

    `on_step(step_name, status, payload)` is an optional callback invoked as each
    step starts ("running") and completes ("complete"), enabling live streaming.
    """
    from agents.repository import begin_run_cache

    def emit(step, status, log=None):
        if on_step:
            on_step(step, status, log)

    logs: list[dict] = []

    def make_log(step, output, raw):
        return _make_step_log(step, output, raw)

    # One shared cache for the whole crew run — saves repeated customer +
    # transaction fetches across the 3 tools + deterministic re-merge.
    with begin_run_cache():
        emit("profile", "running")
        profile, raw = step_profile(customer_id)
        log = make_log("profile", profile, raw); logs.append(log); emit("profile", "complete", log)

        emit("wellness", "running")
        wellness, raw = step_wellness(profile)
        log = make_log("wellness", wellness, raw); logs.append(log); emit("wellness", "complete", log)

        emit("nudge", "running")
        nudge_plan, raw = step_nudge(profile, wellness)
        log = make_log("nudge", nudge_plan, raw); logs.append(log); emit("nudge", "complete", log)

        emit("compliance", "running")
        compliance, raw = step_compliance(nudge_plan)
        log = make_log("compliance", compliance, raw); logs.append(log); emit("compliance", "complete", log)

        emit("generate", "running")
        messages, raw = step_generate(nudge_plan, compliance)
        log = make_log("generate", messages, raw); logs.append(log); emit("generate", "complete", log)

        final = {
            "customer_id": customer_id,
            "profile": profile,
            "wellness": wellness,
            "nudge_plan": nudge_plan,
            "compliance": compliance,
            "final_messages": messages.get("final_messages", []),
            "agent_logs": logs,
            "created_at": _ts(),
        }
        emit("complete", "complete", {"step": "complete", "agent": "Crew", "status": "complete",
                                      "summary": "Engagement pipeline finished.", "timestamp": _ts()})
    return final
