"""Detect life events from transaction patterns using signature matching."""
from __future__ import annotations

from collections import defaultdict


def detect_life_events(transactions: list[dict], customer: dict) -> list[dict]:
    """Return a list of detected life events with confidence + details."""
    events: list[dict] = []
    if not transactions:
        return events

    # aggregate by month + category
    by_month_cat: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    salary_by_month: dict[str, float] = defaultdict(float)
    for t in transactions:
        mk = t["date"][:7]
        if t["type"] == "credit" and t["category"] == "salary":
            salary_by_month[mk] += t["amount"]
        elif t["type"] == "debit":
            by_month_cat[mk][t["category"]] += t["amount"]

    months = sorted(set(by_month_cat) | set(salary_by_month))

    # --- Salary hike ---
    sal_months = sorted(salary_by_month)
    if len(sal_months) >= 2:
        first = salary_by_month[sal_months[0]]
        last = salary_by_month[sal_months[-1]]
        if first > 0 and last > first * 1.15:
            events.append({
                "event": "salary_hike",
                "confidence": 0.95,
                "details": f"\u20b9{round(first/1000)}K \u2192 \u20b9{round(last/1000)}K",
            })

    # --- Wedding preparation ---
    wedding_spend = sum(by_month_cat[m].get("wedding", 0) for m in months)
    jewellery_spend = sum(by_month_cat[m].get("jewellery", 0) for m in months)
    if wedding_spend > 50000 or jewellery_spend > 80000:
        conf = 0.82 if wedding_spend and jewellery_spend else 0.65
        events.append({
            "event": "wedding_preparation",
            "confidence": conf,
            "details": "Jewellery + venue/catering spends detected",
        })

    # --- New baby / child ---
    medical = sum(by_month_cat[m].get("medical", 0) for m in months)
    if medical > 40000 and customer.get("age", 99) < 40:
        events.append({
            "event": "new_baby",
            "confidence": 0.7,
            "details": "Elevated hospital/medical spend",
        })

    # --- Child education ---
    education = sum(by_month_cat[m].get("education", 0) for m in months)
    if education > 60000:
        events.append({
            "event": "child_education",
            "confidence": 0.78,
            "details": "Recurring school/college fee payments",
        })

    # --- Relocation ---
    big_shopping = max((by_month_cat[m].get("shopping", 0) for m in months), default=0)
    if big_shopping > 40000 and "rent" in {c for m in months for c in by_month_cat[m]}:
        events.append({
            "event": "relocation",
            "confidence": 0.6,
            "details": "Large electronics/furniture purchase + rent",
        })

    # --- Approaching retirement (profile based) ---
    if customer.get("age", 0) >= 55:
        events.append({
            "event": "approaching_retirement",
            "confidence": 0.9,
            "details": f"Age {customer['age']} \u2014 retirement horizon",
        })

    return events


def get_crewai_tool():
    try:
        from crewai.tools import BaseTool
    except Exception:
        return None

    from agents.repository import get_customer, get_transactions

    class LifeEventDetectorTool(BaseTool):
        name: str = "Life Event Detector"
        description: str = (
            "Detect major life events (wedding, baby, relocation, salary hike, retirement) "
            "from a customer's transactions. Input: customer_id."
        )

        def _run(self, customer_id: str) -> str:
            import json
            txns = get_transactions(customer_id)
            cust = get_customer(customer_id) or {}
            return json.dumps(detect_life_events(txns, cust))

    return LifeEventDetectorTool()
