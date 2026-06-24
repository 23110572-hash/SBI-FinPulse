"""Analysis + nudge schemas (loose dicts for the rich agent JSON)."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AnalysisResult(BaseModel):
    customer_id: str
    profile: dict[str, Any] = {}
    wellness: dict[str, Any] = {}
    nudge_plan: dict[str, Any] = {}
    compliance: dict[str, Any] = {}
    final_messages: list[dict[str, Any]] = []
    agent_logs: list[dict[str, Any]] = []
    created_at: str | None = None


class NudgeOut(BaseModel):
    id: str
    customer_id: str
    customer_name: str | None = None
    priority: int
    target_gap: str | None = None
    product_name: str | None = None
    product_category: str | None = None
    psychological_frame: str | None = None
    message_draft: str | None = None
    channel: str | None = None
    expected_conversion: str | None = None
    compliance_status: str = "pending"
    compliance_notes: dict[str, Any] = {}
    status: str = "pending"
    created_at: str | None = None
    delivery_status: str | None = None  # last delivery receipt status
    delivery_provider: str | None = None
    delivery_error: str | None = None
    sent_at: str | None = None
    # Risk-tiered approval — populated by api.routes.nudges._enrich.
    tier: int | None = None
    tier_label: str | None = None
    tier_reason: str | None = None
    requires_review: bool = False

    class Config:
        from_attributes = True
