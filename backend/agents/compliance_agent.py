"""Compliance Agent (CrewAI)."""
from __future__ import annotations

from agents.llms import get_groq_llm
from agents.tools.compliance_checker import get_crewai_tool as compliance_tool
from agents.tools.rag_search import get_crewai_tool as rag_tool
from config import settings


def build_compliance_agent():
    try:
        from crewai import Agent
    except Exception:
        return None

    tools = [t for t in (rag_tool(), compliance_tool()) if t is not None]
    return Agent(
        role="Regulatory Compliance Officer",
        goal=("Validate every nudge against RBI Fair Practices Code, DPDP Act 2023 and SBI "
              "internal policies. Ensure zero misselling risk."),
        backstory=("You are a compliance officer with deep expertise in Indian banking "
                   "regulations. You are strict but fair: you approve good recommendations and "
                   "flag problematic ones with specific regulatory references."),
        tools=tools,
        llm=get_groq_llm(temperature=0.1, slot=2),
        verbose=settings.agent_verbose,
        allow_delegation=False,
    )
