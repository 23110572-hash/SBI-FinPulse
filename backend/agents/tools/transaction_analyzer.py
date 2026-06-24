"""Transaction analysis logic — groups spend, computes trends.

Pure-Python core (usable by the heuristic engine) plus an optional CrewAI tool
wrapper exposed via `get_crewai_tool()`.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime


def _month_key(date_str: str) -> str:
    return date_str[:7]  # YYYY-MM


ESSENTIAL = {"rent", "groceries", "utilities", "medical", "transport"}
LIFESTYLE = {"dining", "shopping", "subscriptions", "travel", "jewellery"}
EMI = {"emi"}
INVEST = {"investment", "insurance"}


def analyze_transactions(transactions: list[dict]) -> dict:
    """Group transactions by category, compute month-over-month trends."""
    if not transactions:
        return {"spending_categories": {}, "spending_trends": {}, "monthly_spending": 0}

    by_month_cat: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    cat_totals: dict[str, float] = defaultdict(float)
    months: set[str] = set()

    for t in transactions:
        if t["type"] != "debit":
            continue
        mk = _month_key(t["date"])
        months.add(mk)
        by_month_cat[mk][t["category"]] += t["amount"]
        cat_totals[t["category"]] += t["amount"]

    sorted_months = sorted(months)
    n_months = max(1, len(sorted_months))

    # average monthly spend per high-level bucket
    buckets = {"essentials": 0.0, "lifestyle": 0.0, "emi": 0.0, "investments": 0.0, "others": 0.0}
    for cat, total in cat_totals.items():
        avg = total / n_months
        if cat in ESSENTIAL:
            buckets["essentials"] += avg
        elif cat in LIFESTYLE:
            buckets["lifestyle"] += avg
        elif cat in EMI:
            buckets["emi"] += avg
        elif cat in INVEST:
            buckets["investments"] += avg
        else:
            buckets["others"] += avg
    buckets = {k: round(v) for k, v in buckets.items()}

    # MoM trends: compare last month vs previous month per category
    trends: dict[str, str] = {}
    if len(sorted_months) >= 2:
        last, prev = sorted_months[-1], sorted_months[-2]
        for cat in set(by_month_cat[last]) | set(by_month_cat[prev]):
            cur = by_month_cat[last].get(cat, 0)
            old = by_month_cat[prev].get(cat, 0)
            if old == 0 and cur > 0:
                trends[cat] = "new_category"
            elif old > 0:
                pct = round((cur - old) / old * 100)
                if abs(pct) >= 25:
                    trends[cat] = f"{'+' if pct >= 0 else ''}{pct}% MoM"

    total_monthly = round(sum(cat_totals.values()) / n_months)
    return {
        "spending_categories": buckets,
        "spending_trends": trends,
        "monthly_spending": total_monthly,
        "category_totals": {k: round(v) for k, v in cat_totals.items()},
        "months_analyzed": len(sorted_months),
    }


def get_crewai_tool():
    """Return a CrewAI BaseTool wrapping the analyzer, or None if unavailable."""
    try:
        from crewai.tools import BaseTool
    except Exception:
        return None

    from agents.repository import get_transactions

    class TransactionAnalyzerTool(BaseTool):
        name: str = "Transaction Analyzer"
        description: str = (
            "Analyze a customer's transaction history. Input: customer_id (e.g. 'CUST_001'). "
            "Returns spending categories, month-over-month trends and monthly spend."
        )

        def _run(self, customer_id: str) -> str:
            import json
            txns = get_transactions(customer_id)
            return json.dumps(analyze_transactions(txns))

    return TransactionAnalyzerTool()
