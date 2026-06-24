"""Customer Profiler Agent (CrewAI)."""
from __future__ import annotations

from agents.llms import get_groq_llm
from agents.tools.life_event_detector import get_crewai_tool as life_tool
from agents.tools.transaction_analyzer import get_crewai_tool as txn_tool
from config import settings


def build_profiler_agent():
    try:
        from crewai import Agent
    except Exception:
        return None

    tools = [t for t in (txn_tool(), life_tool()) if t is not None]
    return Agent(
        role="Senior Customer Analyst",
        goal=("Analyze customer transaction history and build a comprehensive profile "
              "including spending patterns, life events and financial behaviour."),
        backstory=("You are an expert financial analyst at SBI with 15 years of experience "
                   "in understanding customer behaviour from transaction data. You detect "
                   "subtle patterns that indicate major life events."),
        tools=tools,
        llm=get_groq_llm(temperature=0.2, slot=1),
        verbose=settings.agent_verbose,
        allow_delegation=False,
    )
