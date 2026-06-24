"""Seed the PostgreSQL (Neon) database from generated JSON data.

This DROPS and RECREATES all tables so the schema always matches the current
models, then loads synthetic customers + transactions.

Run:  python database/seed.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# allow running as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import SessionLocal, reset_db  # noqa: E402
from database.models import Customer, Transaction  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def seed() -> None:
    customers_file = DATA_DIR / "customers.json"
    txns_file = DATA_DIR / "transactions.json"

    if not customers_file.exists() or not txns_file.exists():
        print("Data files missing. Run: python data/generate_data.py first.")
        return

    # drop + recreate everything so new columns/tables exist on Neon
    reset_db()
    print("Schema reset (all tables dropped and recreated).")

    db = SessionLocal()
    try:
        customers = json.loads(customers_file.read_text(encoding="utf-8"))
        for c in customers:
            db.add(Customer(
                id=c["customer_id"],
                name=c["name"],
                age=c["age"],
                location=c["location"],
                persona=c["persona"],
                income_band=c["income_band"],
                monthly_income=c["monthly_income"],
                monthly_spending=c["monthly_spending"],
                savings_rate=c["savings_rate"],
                current_balance=c["current_balance"],
                risk_appetite=c["risk_appetite"],
                digital_activity=c["digital_activity"],
                products_held=c["products_held"],
                products_not_held=c["products_not_held"],
                phone=c.get("phone"),
                email=c.get("email"),
                whatsapp_opt_in=1 if c.get("whatsapp_opt_in") else 0,
                preferred_language=c.get("preferred_language", "en"),
            ))
        db.commit()

        txns = json.loads(txns_file.read_text(encoding="utf-8"))
        batch_size = 200
        for i in range(0, len(txns), batch_size):
            for t in txns[i:i + batch_size]:
                db.add(Transaction(
                    id=t["id"],
                    customer_id=t["customer_id"],
                    date=t["date"],
                    type=t["type"],
                    amount=t["amount"],
                    description=t["description"],
                    category=t["category"],
                    channel=t["channel"],
                    balance_after=t["balance_after"],
                ))
            db.commit()

        print(f"Seeded {len(customers)} customers and {len(txns)} transactions.")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
