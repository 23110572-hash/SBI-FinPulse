"""Financial Wellness Agent (CrewAI)."""
from __future__ import annotations

from agents.llms import get_groq_llm
from agents.tools.wellness_calculator import get_crewai_tool as wellness_tool
from config import settings


def build_wellness_agent():
    try:
        from crewai import Agent
    except Exception:
        return None

    tools = [t for t in (wellness_tool(),) if t is not None]
    return Agent(
        role="Financial Wellness Advisor",
        goal=("Calculate a comprehensive financial health score (0-100) and identify "
              "critical gaps and improvement opportunities."),
        backstory=("You are a certified financial planner specialising in holistic financial "
                   "health assessment: savings adequacy, insurance coverage, investment "
                   "diversification, debt management and emergency preparedness."),
        tools=tools,
        llm=get_groq_llm(temperature=0.2, slot=1),
        verbose=settings.agent_verbose,
        allow_delegation=False,
    )
