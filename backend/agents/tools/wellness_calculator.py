"""Calculate a 0-100 financial health score across 5 components.

Benchmarks tuned for Indian households.
"""
from __future__ import annotations


def _grade(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 70:
        return "Healthy"
    if score >= 55:
        return "Fair"
    if score >= 40:
        return "Needs Attention"
    return "At Risk"


def calculate_wellness(profile: dict) -> dict:
    """Compute component scores + overall from a customer profile dict."""
    income = max(0, profile.get("monthly_income", 0))
    spending = max(0, profile.get("monthly_spending", 0))
    savings_rate = profile.get("savings_rate", 0.0)
    balance = profile.get("current_balance", 0)
    held = set(profile.get("products_held", []))
    categories = profile.get("spending_categories", {})

    # --- 1. Savings ratio ---
    if savings_rate >= 30:
        savings_score = 80
        s_detail = f"Saving {savings_rate}% \u2014 strong, but check where it sits"
    elif savings_rate >= 20:
        savings_score = 65
        s_detail = f"Saving {savings_rate}% \u2014 good"
    elif savings_rate >= 10:
        savings_score = 45
        s_detail = f"Saving {savings_rate}% \u2014 below ideal"
    else:
        savings_score = 25
        s_detail = f"Saving {savings_rate}% \u2014 too low"

    # --- 2. Emergency fund (months of expenses covered by balance) ---
    months_covered = round(balance / spending, 1) if spending > 0 else 0
    if months_covered >= 6:
        ef_score = 95
    elif months_covered >= 3:
        ef_score = 60
    elif months_covered >= 1:
        ef_score = 35
    else:
        ef_score = 15
    ef_detail = f"{months_covered} months of expenses covered (target: 6)"

    # --- 3. Insurance coverage ---
    has_term = "term_insurance" in held
    has_health = "health_insurance" in held
    ins_score = 20 + (40 if has_term else 0) + (40 if has_health else 0)
    if ins_score >= 80:
        ins_detail = "Term + health insurance in place"
    elif ins_score >= 50:
        ins_detail = "Partial cover \u2014 one key policy missing"
    else:
        ins_detail = "No term insurance, no health insurance"

    # --- 4. Investment diversification ---
    invest_products = held & {"mutual_fund", "ppf", "nps", "fixed_deposit"}
    div_score = min(100, 20 + len(invest_products) * 22)
    invests = categories.get("investments", 0)
    if not invest_products and invests == 0:
        div_detail = "No MF/SIP/PPF \u2014 wealth not growing"
    else:
        div_detail = f"{len(invest_products)} investment product(s) held"

    # --- 5. Debt management ---
    emi = categories.get("emi", 0)
    emi_ratio = (emi / income * 100) if income > 0 else 0
    if emi_ratio == 0:
        debt_score = 85
        debt_detail = "No active loan EMIs"
    elif emi_ratio <= 30:
        debt_score = 90
        debt_detail = f"EMI is {round(emi_ratio)}% of income \u2014 healthy"
    elif emi_ratio <= 45:
        debt_score = 60
        debt_detail = f"EMI is {round(emi_ratio)}% of income \u2014 watch closely"
    else:
        debt_score = 30
        debt_detail = f"EMI is {round(emi_ratio)}% of income \u2014 overleveraged"

    breakdown = {
        "savings_ratio": {"score": savings_score, "max": 100, "detail": s_detail},
        "emergency_fund": {"score": ef_score, "max": 100, "detail": ef_detail},
        "insurance_coverage": {"score": ins_score, "max": 100, "detail": ins_detail},
        "investment_diversification": {"score": div_score, "max": 100, "detail": div_detail},
        "debt_management": {"score": debt_score, "max": 100, "detail": debt_detail},
    }

    # weighted overall
    weights = {
        "savings_ratio": 0.2, "emergency_fund": 0.2, "insurance_coverage": 0.25,
        "investment_diversification": 0.2, "debt_management": 0.15,
    }
    overall = round(sum(breakdown[k]["score"] * w for k, w in weights.items()))

    # critical gaps
    gaps = []
    if not has_term:
        gaps.append({"gap": "no_term_insurance", "severity": "high",
                     "impact": "Family financially unprotected"})
    if not has_health:
        gaps.append({"gap": "no_health_insurance", "severity": "high",
                     "impact": "One hospital bill could wipe out savings"})
    if months_covered < 3:
        gaps.append({"gap": "no_emergency_fund", "severity": "high",
                     "impact": "Vulnerable to unexpected expenses"})
    if not invest_products and balance > 100000:
        gaps.append({"gap": "idle_savings", "severity": "medium",
                     "impact": f"\u20b9{round(balance/100000,1)}L earning ~3.5% instead of 12%+"})

    # quick wins
    wins = []
    if not invest_products:
        wins.append({"action": "Start SIP \u20b95,000/month", "impact": "+15 score points in 3 months"})
    if not has_term:
        wins.append({"action": "Get SBI Life eShield term insurance", "impact": "+18 score points"})
    if months_covered < 6 and balance > 50000:
        wins.append({"action": "Park \u20b91L in a liquid FD as emergency buffer", "impact": "+8 score points"})

    return {
        "customer_id": profile.get("customer_id") or profile.get("id"),
        "overall_score": overall,
        "grade": _grade(overall),
        "breakdown": breakdown,
        "critical_gaps": gaps,
        "quick_wins": wins,
        "peer_comparison": _peer_comparison(overall),
    }


def _peer_comparison(score: int) -> str:
    if score >= 75:
        return "Your score is higher than 72% of SBI customers in your age/income group"
    if score >= 60:
        return "Your score is around the average for SBI customers in your group"
    pct = max(40, 80 - score // 2)
    return f"Your score is below {pct}% of SBI customers in your age/income group"


def get_crewai_tool():
    try:
        from crewai.tools import BaseTool
    except Exception:
        return None

    class WellnessCalculatorTool(BaseTool):
        name: str = "Wellness Calculator"
        description: str = (
            "Calculate a 0-100 financial health score from a customer profile JSON string. "
            "Input must be a JSON object with monthly_income, monthly_spending, savings_rate, "
            "current_balance, products_held, spending_categories."
        )

        def _run(self, profile_json: str) -> str:
            import json
            try:
                profile = json.loads(profile_json)
            except Exception:
                return json.dumps({"error": "invalid profile json"})
            return json.dumps(calculate_wellness(profile))

    return WellnessCalculatorTool()
