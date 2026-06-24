"""Synthetic data provider — reads the locally seeded SQLite store.

This is the default/demo source. It is the only provider that ships with data;
the others connect to live (sandboxed) external systems.
"""
from __future__ import annotations

from database.connection import SessionLocal
from database.models import Customer, Transaction

from .base import DataProvider


class SyntheticProvider(DataProvider):
    name = "synthetic"
    requires_consent = False

    def get_customer(self, customer_id: str) -> dict | None:
        db = SessionLocal()
        try:
            c = db.query(Customer).filter(Customer.id == customer_id).first()
            if not c:
                return None
            return {
                "id": c.id,
                "customer_id": c.id,
                "name": c.name,
                "age": c.age,
                "location": c.location,
                "persona": c.persona,
                "income_band": c.income_band,
                "monthly_income": c.monthly_income,
                "monthly_spending": c.monthly_spending,
                "savings_rate": c.savings_rate,
                "current_balance": c.current_balance,
                "risk_appetite": c.risk_appetite,
                "digital_activity": c.digital_activity,
                "products_held": c.products_held or [],
                "products_not_held": c.products_not_held or [],
                "phone": c.phone,
                "email": c.email,
                "whatsapp_opt_in": bool(c.whatsapp_opt_in),
                "preferred_language": c.preferred_language or "en",
            }
        finally:
            db.close()

    def get_transactions(self, customer_id: str) -> list[dict]:
        db = SessionLocal()
        try:
            rows = (db.query(Transaction)
                    .filter(Transaction.customer_id == customer_id)
                    .order_by(Transaction.date).all())
            return [{
                "id": t.id,
                "customer_id": t.customer_id,
                "date": t.date,
                "type": t.type,
                "amount": t.amount,
                "description": t.description,
                "category": t.category,
                "channel": t.channel,
                "balance_after": t.balance_after,
            } for t in rows]
        finally:
            db.close()

    def list_customers(self) -> list[dict]:
        db = SessionLocal()
        try:
            return [{
                "id": c.id, "name": c.name, "age": c.age, "location": c.location,
                "persona": c.persona, "income_band": c.income_band,
                "monthly_income": c.monthly_income, "digital_activity": c.digital_activity,
            } for c in db.query(Customer).all()]
        finally:
            db.close()
