"""Insights + wellness routes derived from the latest analysis."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.store import latest_analysis

router = APIRouter(prefix="/api", tags=["insights"])


def _build_insights(analysis: dict) -> list[dict]:
    insights: list[dict] = []
    profile = analysis.get("profile", {})
    wellness = analysis.get("wellness", {})
    nudge_plan = analysis.get("nudge_plan", {})

    for ev in profile.get("life_events_detected", []):
        insights.append({
            "type": "life_event",
            "icon": "PartyPopper",
            "title": ev.get("event", "").replace("_", " ").title(),
            "description": ev.get("details", ""),
            "confidence": ev.get("confidence"),
            "action": "Explore options",
        })

    for gap in wellness.get("critical_gaps", []):
        insights.append({
            "type": "alert",
            "icon": "TrendingDown",
            "title": gap.get("gap", "").replace("_", " ").title(),
            "description": gap.get("impact", ""),
            "severity": gap.get("severity"),
            "action": "Fix this",
        })

    for win in wellness.get("quick_wins", []):
        insights.append({
            "type": "opportunity",
            "icon": "Lightbulb",
            "title": win.get("action", ""),
            "description": win.get("impact", ""),
            "action": "Act now",
        })

    for n in nudge_plan.get("nudges", []):
        product = n.get("product_recommended", {})
        insights.append({
            "type": "product_suggestion",
            "icon": "Target",
            "title": product.get("name", "Recommended for you"),
            "description": n.get("message_draft", ""),
            "channel": n.get("channel"),
            "action": "Learn more",
        })
    return insights


@router.get("/insights/{customer_id}")
def get_insights(customer_id: str):
    analysis = latest_analysis(customer_id)
    if not analysis:
        raise HTTPException(404, "No analysis yet. Run analysis first.")
    return {"customer_id": customer_id, "insights": _build_insights(analysis)}


@router.get("/wellness/{customer_id}")
def get_wellness(customer_id: str):
    analysis = latest_analysis(customer_id)
    if not analysis:
        raise HTTPException(404, "No analysis yet. Run analysis first.")
    return analysis.get("wellness", {})
