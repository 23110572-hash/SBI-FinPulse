"""LangGraph StateGraph for the FinPulse engagement pipeline.

Wraps the CrewAI step functions as graph nodes so the workflow is visual,
debuggable and streamable. Each node runs one LLM agent and updates shared state.

States:  profile -> wellness -> nudge -> compliance -> generate -> complete
"""
from __future__ import annotations

from typing import Any, Callable, Optional, TypedDict

from agents import crew


class EngagementState(TypedDict, total=False):
    customer_id: str
    customer_profile: dict
    wellness_assessment: dict
    nudge_plan: dict
    compliance_result: dict
    final_messages: list
    current_step: str
    agent_logs: list
    error: Optional[str]


def _emit(state: EngagementState, on_step: Optional[Callable], step: str, status: str, log=None):
    if on_step:
        on_step(step, status, log)


def build_graph(on_step: Optional[Callable[[str, str, Any], None]] = None):
    """Build and compile the LangGraph StateGraph."""
    from langgraph.graph import END, StateGraph

    def node_profile(state: EngagementState) -> EngagementState:
        _emit(state, on_step, "profile", "running")
        profile, raw = crew.step_profile(state["customer_id"])
        log = crew._make_step_log("profile", profile, raw)
        _emit(state, on_step, "profile", "complete", log)
        return {"customer_profile": profile, "current_step": "wellness",
                "agent_logs": state.get("agent_logs", []) + [log]}

    def node_wellness(state: EngagementState) -> EngagementState:
        _emit(state, on_step, "wellness", "running")
        wellness, raw = crew.step_wellness(state["customer_profile"])
        log = crew._make_step_log("wellness", wellness, raw)
        _emit(state, on_step, "wellness", "complete", log)
        return {"wellness_assessment": wellness, "current_step": "nudge",
                "agent_logs": state.get("agent_logs", []) + [log]}

    def node_nudge(state: EngagementState) -> EngagementState:
        _emit(state, on_step, "nudge", "running")
        plan, raw = crew.step_nudge(state["customer_profile"], state["wellness_assessment"])
        log = crew._make_step_log("nudge", plan, raw)
        _emit(state, on_step, "nudge", "complete", log)
        return {"nudge_plan": plan, "current_step": "compliance",
                "agent_logs": state.get("agent_logs", []) + [log]}

    def node_compliance(state: EngagementState) -> EngagementState:
        _emit(state, on_step, "compliance", "running")
        result, raw = crew.step_compliance(state["nudge_plan"])
        log = crew._make_step_log("compliance", result, raw)
        _emit(state, on_step, "compliance", "complete", log)
        return {"compliance_result": result, "current_step": "generate",
                "agent_logs": state.get("agent_logs", []) + [log]}

    def node_generate(state: EngagementState) -> EngagementState:
        _emit(state, on_step, "generate", "running")
        messages, raw = crew.step_generate(state["nudge_plan"], state["compliance_result"])
        log = crew._make_step_log("generate", messages, raw)
        _emit(state, on_step, "generate", "complete", log)
        return {"final_messages": messages.get("final_messages", []), "current_step": "complete",
                "agent_logs": state.get("agent_logs", []) + [log]}

    def route_after_compliance(state: EngagementState) -> str:
        results = state.get("compliance_result", {}).get("compliance_results", [])
        approved = [r for r in results if r.get("status") != "rejected"]
        return "generate" if approved else "complete"

    g = StateGraph(EngagementState)
    g.add_node("profile", node_profile)
    g.add_node("wellness", node_wellness)
    g.add_node("nudge", node_nudge)
    g.add_node("compliance", node_compliance)
    g.add_node("generate", node_generate)

    g.set_entry_point("profile")
    g.add_edge("profile", "wellness")
    g.add_edge("wellness", "nudge")
    g.add_edge("nudge", "compliance")
    g.add_conditional_edges("compliance", route_after_compliance,
                            {"generate": "generate", "complete": END})
    g.add_edge("generate", END)
    return g.compile()


def run_engagement(customer_id: str, on_step: Optional[Callable] = None) -> EngagementState:
    """Execute the engagement graph for a customer."""
    graph = build_graph(on_step)
    initial: EngagementState = {"customer_id": customer_id, "current_step": "profile",
                                "agent_logs": [], "error": None}
    final = graph.invoke(initial)
    if on_step:
        on_step("complete", "complete", {"step": "complete", "agent": "Crew",
                                         "status": "complete", "summary": "Pipeline finished."})
    return final
