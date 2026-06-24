"""Real-time event ingester for live demos.

When this script runs it walks the same code path as the production webhook
(``POST /api/engagement/webhook/transaction``):

  1. Writes one or more real ``Transaction`` rows for the chosen customer
     so the Profiler agent's tools and the deterministic life-event detector
     genuinely *see* the new activity in Postgres.
  2. Records an ``EngagementEvent`` via ``services.engagement.ingest_event``.
  3. With active DPDP consent, fires the full five-agent CrewAI pipeline.
  4. Tier 1 nudges (savings / FD / digital) auto-send by email; Tier 2 / 3
     nudges land in the staff Review Queue.

This is *not* a faked demo button. Every step is the real production path —
the only difference from a true core-banking event is that we synthesise
the transaction here instead of reading it off Kafka.

USAGE  (run from the ``backend/`` folder with the venv active)

    python tools/ingest_event.py --list

    python tools/ingest_event.py --customer CUST_009 --scenario salary_hike
    python tools/ingest_event.py --customer CUST_011 --scenario wedding_prep --grant-consent
    python tools/ingest_event.py --customer CUST_007 --scenario new_baby --reset-analysis
    python tools/ingest_event.py --customer CUST_013 --scenario child_education
    python tools/ingest_event.py --customer CUST_004 --scenario large_purchase --grant-consent
    python tools/ingest_event.py --customer CUST_006 --scenario relocation

Available scenarios are documented inline in ``SCENARIOS`` below.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

# Allow ``python tools/ingest_event.py`` from the ``backend/`` folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func  # noqa: E402

from database.connection import SessionLocal, init_db  # noqa: E402
from database.models import (  # noqa: E402
    Analysis, Customer, DeliveryReceipt, Nudge, Transaction,
)
from services import consent as consent_svc  # noqa: E402
from services import engagement as eng_svc  # noqa: E402


# ---------------------------------------------------------------------------
# Scenarios — each is a transaction signature crafted so that the
# deterministic life-event detector + the five-agent crew produce a
# coherent, demo-ready story.
# ---------------------------------------------------------------------------
def _today() -> dt.date:
    return dt.date.today()


def _days_ago(n: int) -> str:
    return (_today() - dt.timedelta(days=n)).isoformat()


SCENARIOS: dict[str, dict] = {
    "salary_hike": {
        "label": "Salary hike — promotion / increment landed",
        "signal": "salary_credit",
        "tx": [
            {"days_ago": 1, "type": "credit", "amount": 125000, "category": "salary",
             "description": "Salary credit · monthly", "channel": "neft"},
        ],
    },
    "wedding_prep": {
        "label": "Wedding preparation — jewellery + venue",
        "signal": "wedding_prep",
        "tx": [
            {"days_ago": 4, "type": "debit", "amount": 110000, "category": "jewellery",
             "description": "Tanishq · gold purchase", "channel": "card"},
            {"days_ago": 2, "type": "debit", "amount": 60000, "category": "wedding",
             "description": "Banquet hall booking · advance", "channel": "neft"},
        ],
    },
    "new_baby": {
        "label": "New baby — hospital + child-care spend (best for age < 40)",
        "signal": "new_baby",
        "tx": [
            {"days_ago": 6, "type": "debit", "amount": 38000, "category": "medical",
             "description": "Apollo Hospital · maternity package", "channel": "card"},
            {"days_ago": 3, "type": "debit", "amount": 9500, "category": "medical",
             "description": "FirstCry · baby essentials", "channel": "upi"},
        ],
    },
    "child_education": {
        "label": "Child education — school / college fee",
        "signal": "child_education",
        "tx": [
            {"days_ago": 5, "type": "debit", "amount": 75000, "category": "education",
             "description": "DPS · annual fee", "channel": "neft"},
        ],
    },
    "large_purchase": {
        "label": "Large purchase — single high-value debit",
        "signal": "large_purchase",
        "tx": [
            {"days_ago": 1, "type": "debit", "amount": 95000, "category": "shopping",
             "description": "MacBook Air M3 · Croma", "channel": "card"},
        ],
    },
    "relocation": {
        "label": "Relocation — furniture + rent",
        "signal": "relocation",
        "tx": [
            {"days_ago": 7, "type": "debit", "amount": 48000, "category": "shopping",
             "description": "IKEA · home furniture", "channel": "card"},
            {"days_ago": 1, "type": "debit", "amount": 28000, "category": "rent",
             "description": "Rent · new flat", "channel": "neft"},
        ],
    },
}


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------
def _next_txn_id(db) -> str:
    """Generate the next ``TXN_NNNNNN`` id by reading the max in the table."""
    row = db.query(func.max(Transaction.id)).scalar()
    n = 0
    if row and isinstance(row, str) and row.startswith("TXN_"):
        try:
            n = int(row.split("_", 1)[1])
        except (IndexError, ValueError):
            n = 0
    return f"TXN_{n + 1:06d}"


def insert_transactions(customer_id: str, scenario: dict) -> list[dict]:
    """Persist the scenario's transactions, updating ``current_balance``."""
    db = SessionLocal()
    try:
        cust = db.query(Customer).filter(Customer.id == customer_id).first()
        if not cust:
            raise SystemExit(f"Customer {customer_id!r} not found in the database.")

        balance = float(cust.current_balance or 0)
        inserted: list[dict] = []
        for spec in scenario["tx"]:
            txn_id = _next_txn_id(db)
            amount = float(spec["amount"])
            balance += amount if spec["type"] == "credit" else -amount
            row = Transaction(
                id=txn_id, customer_id=customer_id,
                date=_days_ago(spec["days_ago"]),
                type=spec["type"], amount=amount,
                description=spec["description"], category=spec["category"],
                channel=spec.get("channel"), balance_after=balance,
            )
            db.add(row)
            db.flush()
            inserted.append({
                "id": row.id, "date": row.date, "type": row.type,
                "amount": row.amount, "category": row.category,
                "description": row.description,
            })
        cust.current_balance = balance
        db.commit()
        return inserted
    finally:
        db.close()


def reset_state(customer_id: str) -> dict:
    """Drop prior analysis + nudges + delivery receipts so the demo starts clean.

    The 24-hour cooldown and 30-day same-gap cooldown both consult these
    tables — clearing them lets the same scenario run repeatedly during a demo
    without being throttled.
    """
    db = SessionLocal()
    try:
        nudge_ids = [
            row[0] for row in
            db.query(Nudge.id).filter(Nudge.customer_id == customer_id).all()
        ]
        deliveries = 0
        if nudge_ids:
            deliveries = (db.query(DeliveryReceipt)
                          .filter(DeliveryReceipt.nudge_id.in_(nudge_ids))
                          .delete(synchronize_session=False))
        nudges = (db.query(Nudge).filter(Nudge.customer_id == customer_id)
                  .delete(synchronize_session=False))
        analyses = (db.query(Analysis).filter(Analysis.customer_id == customer_id)
                    .delete(synchronize_session=False))
        db.commit()
        return {"analyses": analyses, "nudges": nudges, "deliveries": deliveries}
    finally:
        db.close()


def ensure_consent(customer_id: str) -> dict:
    if consent_svc.has_active_consent(customer_id, consent_svc.PURPOSE_ENGAGEMENT):
        return {"status": "already_active"}
    rec = consent_svc.grant(customer_id, channels=["email"], source="demo_ingester",
                            actor="ops:ingest_event")
    return {"status": "granted_now", "consent_id": rec["id"]}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def list_scenarios() -> None:
    print("\nAvailable scenarios:\n")
    for k, v in SCENARIOS.items():
        print(f"  {k:18s}  {v['label']}")
    print()


def main() -> int:
    p = argparse.ArgumentParser(
        description="Inject a real-time engagement event for a customer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See module docstring for usage examples.",
    )
    p.add_argument("--customer", help="Customer id, e.g. CUST_007")
    p.add_argument("--scenario", choices=list(SCENARIOS.keys()),
                   help="Which life-event signature to write into Postgres")
    p.add_argument("--list", action="store_true",
                   help="Show available scenarios and exit")
    p.add_argument("--grant-consent", action="store_true",
                   help="Grant DPDP engagement consent (email channel) if not already active")
    p.add_argument("--reset-analysis", action="store_true",
                   help="Clear prior analysis + nudges + delivery receipts for this "
                        "customer so the crew runs without hitting cooldowns")
    p.add_argument("--no-trigger", action="store_true",
                   help="Write transactions only, do NOT call the engagement engine")
    args = p.parse_args()

    if args.list or (not args.customer and not args.scenario):
        list_scenarios()
        return 0

    if not args.customer:
        print("error: --customer is required (e.g. --customer CUST_007)", file=sys.stderr)
        return 2
    if not args.scenario:
        print("error: --scenario is required. Run --list to see options.", file=sys.stderr)
        return 2

    scenario = SCENARIOS[args.scenario]
    print()
    print(f"  Customer  : {args.customer}")
    print(f"  Scenario  : {args.scenario}  ({scenario['label']})")
    print(f"  Signal    : {scenario['signal']}")
    print()

    init_db()  # idempotent

    if args.reset_analysis:
        r = reset_state(args.customer)
        print(f"  reset     : {r['analyses']} analysis · {r['nudges']} nudges · "
              f"{r['deliveries']} receipts")

    if args.grant_consent:
        c = ensure_consent(args.customer)
        print(f"  consent   : {c['status']}")

    inserted = insert_transactions(args.customer, scenario)
    print(f"  inserted  : {len(inserted)} transaction(s)")
    for t in inserted:
        sign = "+" if t["type"] == "credit" else "-"
        print(f"              {t['date']}  {sign}Rs.{int(t['amount']):>8,d}  "
              f"{t['category']:<12s}  {t['description']}")

    if args.no_trigger:
        print()
        print("  (engagement engine NOT triggered — --no-trigger set)")
        print()
        return 0

    payload = {
        "scenario": args.scenario,
        "transaction_ids": [t["id"] for t in inserted],
        "amount_total": sum(t["amount"] for t in inserted),
    }
    result = eng_svc.ingest_event(
        args.customer, event_type="life_event",
        signal=scenario["signal"], payload=payload, source="demo_ingester",
    )

    print()
    print(f"  event id  : {result.get('event_id')}")
    print(f"  crew run  : {'YES' if result.get('triggered') else 'no'}")

    if not result.get("triggered"):
        print()
        print("  Crew did not run — the customer has no active engagement consent.")
        print("  Re-run with --grant-consent to grant a synthetic email consent for the demo.")
    else:
        print()
        print("  Five-agent pipeline executed against live data.")
        print("    - Open the staff Engagement Log to see the new nudge.")
        print("    - Tier 1 nudges have already been emailed.")
        print("    - Tier 2 / 3 nudges are waiting in the Review Queue.")
        print("    - Refresh the customer Home tab to see the fresh analysis.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
