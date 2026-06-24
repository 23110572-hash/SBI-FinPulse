from .crew import run_crew
from .conversation_agent import generate_reply

# Public pipeline metadata — the underlying LLM is intentionally NOT exposed.
PIPELINE_STEPS = [
    {"step": "profile", "agent": "Customer Profiler"},
    {"step": "wellness", "agent": "Financial Wellness Advisor"},
    {"step": "nudge", "agent": "Nudge Strategist"},
    {"step": "compliance", "agent": "Compliance Officer"},
    {"step": "generate", "agent": "Conversation Agent"},
]

__all__ = ["run_crew", "generate_reply", "PIPELINE_STEPS"]
