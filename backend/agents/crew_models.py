"""Pydantic output models for CrewAI task structured outputs."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LifeEvent(BaseModel):
    event: str
    confidence: float
    details: str


class ProfileOutput(BaseModel):
    customer_id: str
    name: str = ""
    age: int = 0
    location: str = ""
    persona: str = ""
    income_band: str = ""
    monthly_income: int = 0
    monthly_spending: int = 0
    savings_rate: float = 0.0
    current_balance: float = 0.0
    spending_categories: dict[str, float] = Field(default_factory=dict)
    spending_trends: dict[str, str] = Field(default_factory=dict)
    life_events_detected: list[LifeEvent] = Field(default_factory=list)
    products_held: list[str] = Field(default_factory=list)
    products_not_held: list[str] = Field(default_factory=list)
    risk_appetite: str = ""
    digital_activity: str = ""


class WellnessComponent(BaseModel):
    score: int
    max: int = 100
    detail: str


class Gap(BaseModel):
    gap: str
    severity: str
    impact: str


class QuickWin(BaseModel):
    action: str
    impact: str


class WellnessOutput(BaseModel):
    customer_id: str
    overall_score: int
    grade: str
    breakdown: dict[str, WellnessComponent] = Field(default_factory=dict)
    critical_gaps: list[Gap] = Field(default_factory=list)
    quick_wins: list[QuickWin] = Field(default_factory=list)
    peer_comparison: str = ""


class Nudge(BaseModel):
    priority: int
    target_gap: str = ""
    product_recommended: dict[str, Any] = Field(default_factory=dict)
    psychological_frame: str = ""
    message_draft: str = ""
    timing_strategy: str = ""
    channel: str = ""
    expected_conversion: str = ""
    follow_up: str = ""


class NudgePlanOutput(BaseModel):
    customer_id: str
    nudges: list[Nudge] = Field(default_factory=list)


class ComplianceResult(BaseModel):
    nudge_priority: int
    product: str = ""
    status: str
    checks: dict[str, Any] = Field(default_factory=dict)
    modifications: list[str] = Field(default_factory=list)
    regulatory_references: list[str] = Field(default_factory=list)


class ComplianceOutput(BaseModel):
    customer_id: str
    compliance_results: list[ComplianceResult] = Field(default_factory=list)


class FinalMessage(BaseModel):
    priority: int
    product: str = ""
    channel: str = ""
    frame: str = ""
    message: str
    compliance_status: str = ""


class MessagesOutput(BaseModel):
    customer_id: str
    final_messages: list[FinalMessage] = Field(default_factory=list)
