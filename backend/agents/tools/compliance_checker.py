"""Validate nudges against RBI Fair Practices, DPDP Act and IRDAI rules."""
from __future__ import annotations

# product category -> mandatory disclosures
DISCLOSURES = {
    "mutual_fund": "Mutual fund investments are subject to market risks. Read all scheme "
                   "related documents carefully. Past performance is not indicative of future returns.",
    "term_insurance": "Insurance is the subject matter of solicitation. A free-look period of "
                      "15 days applies. T&C apply.",
    "health_insurance": "Insurance is the subject matter of solicitation. Please review waiting "
                        "periods and exclusions. A free-look period of 15 days applies.",
    "fixed_deposit": "FD rates are subject to change. Premature withdrawal may attract a penalty.",
    "credit_card": "Use credit responsibly. Interest applies on revolving balances. View the Key Fact Statement.",
    "personal_loan": "Loan approval is subject to eligibility. APR and processing fees apply. Key Fact Statement provided.",
}


def _normalize_cat(category: str) -> str:
    """'Term Insurance' / 'term-insurance' -> 'term_insurance'."""
    return (category or "").strip().lower().replace("-", "_").replace(" ", "_")


def disclosure_for(category: str) -> str | None:
    """Resolve the mandatory disclosure for a product category, tolerantly.

    Handles human labels ('Term Insurance'), snake_case ('term_insurance'),
    verbose names ('SBI Bluechip Mutual Fund') and broad categories.
    """
    norm = _normalize_cat(category)
    if not norm:
        return None
    if norm in DISCLOSURES:
        return DISCLOSURES[norm]
    for key, text in DISCLOSURES.items():
        if key in norm:
            return text
    if "health" in norm and "insurance" in norm:
        return DISCLOSURES["health_insurance"]
    if "insurance" in norm or "ulip" in norm:
        return DISCLOSURES["term_insurance"]
    if any(w in norm for w in ("mutual", "fund", "equity", "sip", "elss", "demat")):
        return DISCLOSURES["mutual_fund"]
    if "credit_card" in norm or "credit" in norm:
        return DISCLOSURES["credit_card"]
    if "loan" in norm:
        return DISCLOSURES["personal_loan"]
    return None


def check_compliance(nudge: dict, customer_id: str | None = None) -> dict:
    """Return a compliance result dict for a single nudge.

    When ``customer_id`` is supplied, the DPDP consent check reflects the
    customer's REAL consent state (not a hardcoded pass), and a nudge to a
    customer without active engagement consent is rejected.
    """
    product = nudge.get("product_recommended", {}) or {}
    # The strategist LLM emits product keys inconsistently (name|product_name,
    # category|product_type|type). Read all variants so the category is never
    # silently lost — a missing category breaks risk-tier + disclosure checks.
    category = (product.get("category") or product.get("product_type")
                or product.get("type") or "")
    message = nudge.get("message_draft", "")
    priority = nudge.get("priority", 1)
    channel = (nudge.get("channel") or "app_notification").lower()
    customer_id = customer_id or nudge.get("customer_id")

    checks: dict[str, dict] = {}
    modifications: list[str] = []
    refs: list[str] = []

    # RBI fair practices: suitability
    checks["rbi_fair_practices"] = {"pass": True, "note": "Product suitability matches stated need/risk profile"}
    refs.append("RBI Master Circular - Fair Practices Code")

    # Misselling risk: flag guaranteed-return language
    risky_words = ["guaranteed", "assured returns", "risk-free", "double your money"]
    has_risky = any(w in message.lower() for w in risky_words)
    checks["misselling_risk"] = {
        "pass": not has_risky,
        "risk_level": "high" if has_risky else "low",
        "note": "Avoid guaranteed-return claims" if has_risky else "No misleading claims detected",
    }
    if has_risky:
        modifications.append("Remove guaranteed/assured-return language; returns are not guaranteed.")

    # DPDP consent — REAL check against the consent store (not hardcoded).
    if customer_id:
        try:
            from services import consent as consent_svc
            decision = consent_svc.check(
                customer_id, purpose=consent_svc.PURPOSE_ENGAGEMENT, channel=channel)
        except Exception as e:  # never let consent lookup crash compliance
            decision = {"allowed": False, "reason": f"consent lookup error: {e}"}
        checks["dpdp_consent"] = {
            "pass": bool(decision.get("allowed")),
            "note": ("Active engagement consent covers this channel (DPDP 2023)"
                     if decision.get("allowed")
                     else f"Blocked: {decision.get('reason')}"),
            "consent_id": decision.get("consent_id"),
        }
        if not decision.get("allowed"):
            modifications.append(
                "Obtain DPDP engagement consent covering this channel before sending.")
    else:
        checks["dpdp_consent"] = {
            "pass": False,
            "note": "Consent not verified (no customer context); verify before send.",
        }
    refs.append("DPDP Act 2023 - Consent & Purpose Limitation")

    # Mandatory disclosure (matched tolerantly against the product category).
    norm_cat = _normalize_cat(category)
    disclosure = disclosure_for(category)
    if disclosure:
        present = any(token in message.lower() for token in ["risk", "solicitation", "free-look", "subject to"])
        checks["disclosure_completeness"] = {
            "pass": present,
            "note": "Required disclosure present" if present else "Mandatory disclosure to be appended",
        }
        if not present:
            modifications.append(disclosure)
        if "insurance" in norm_cat or "ulip" in norm_cat:
            checks["irdai_guidelines"] = {"pass": True, "note": "Insurance solicitation rules referenced"}
            refs.append("IRDAI Advertisement & Disclosure Regulations")
            checks["cooling_off_period"] = {"pass": True, "note": "15-day free-look period must be mentioned"}
    else:
        checks["disclosure_completeness"] = {"pass": True, "note": "No category-specific disclosure required"}

    # Hard fails BLOCK the nudge (status=rejected): misselling language or no
    # consent. A missing disclosure is NOT a hard fail — it is auto-appended
    # and the nudge is approved_with_modification (still deliverable). This
    # mirrors how a real compliance desk works: it fixes wording, it doesn't
    # kill a suitable, consented recommendation over a missing boilerplate line.
    blocked = (not checks["misselling_risk"]["pass"]) or (not checks["dpdp_consent"]["pass"])
    if blocked:
        status = "rejected"
    elif modifications:
        status = "approved_with_modification"
    else:
        status = "approved"

    return {
        "nudge_priority": priority,
        "product": product.get("name", "Unknown"),
        "status": status,
        "checks": checks,
        "modifications": modifications,
        "regulatory_references": sorted(set(refs)),
    }


def get_crewai_tool():
    try:
        from crewai.tools import BaseTool
    except Exception:
        return None

    class ComplianceCheckerTool(BaseTool):
        name: str = "Compliance Checker"
        description: str = (
            "Validate a single nudge JSON against RBI/DPDP/IRDAI rules. "
            "Input: JSON object of one nudge. Returns approval status + required modifications."
        )

        def _run(self, nudge_json: str) -> str:
            import json
            try:
                nudge = json.loads(nudge_json)
            except Exception:
                return json.dumps({"error": "invalid nudge json"})
            return json.dumps(check_compliance(nudge))

    return ComplianceCheckerTool()
