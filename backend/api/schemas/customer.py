"""Pydantic schemas for customer data."""
from __future__ import annotations

from pydantic import BaseModel


class TransactionOut(BaseModel):
    id: str
    customer_id: str
    date: str
    type: str
    amount: float
    description: str
    category: str
    channel: str
    balance_after: float

    class Config:
        from_attributes = True


class CustomerSummary(BaseModel):
    id: str
    name: str
    age: int | None = None
    location: str | None = None
    persona: str | None = None
    income_band: str | None = None
    monthly_income: int = 0
    digital_activity: str | None = None

    class Config:
        from_attributes = True


class CustomerDetail(CustomerSummary):
    monthly_spending: int = 0
    savings_rate: float = 0.0
    current_balance: float = 0.0
    risk_appetite: str | None = None
    products_held: list[str] = []
    products_not_held: list[str] = []

    class Config:
        from_attributes = True
