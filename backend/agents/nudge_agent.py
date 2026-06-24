"""Nudge Strategist Agent (CrewAI)."""
from __future__ import annotations

from agents.llms import get_groq_llm
from agents.tools.rag_search import get_crewai_tool as rag_tool
from config import settings


def build_nudge_agent():
    try:
        from crewai import Agent
    except Exception:
        return None

    tools = [t for t in (rag_tool(),) if t is not None]
    return Agent(
        role="Behavioral Finance Strategist",
        goal=("Design the most effective personalised nudge: the right product, the right "
              "psychological frame, the right timing and the right channel."),
        backstory=("You are a behavioural economics expert who ethically uses cognitive biases "
                   "(loss aversion, social proof, anchoring, urgency) to help customers make "
                   "better financial decisions."),
        tools=tools,
        llm=get_groq_llm(temperature=0.5, slot=2),
        verbose=settings.agent_verbose,
        allow_delegation=False,
    )
