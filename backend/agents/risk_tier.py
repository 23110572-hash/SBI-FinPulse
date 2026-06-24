"""Risk-tier classification for proactive nudges.

Indian regulation does not allow 100% automation for several financial
products. Each nudge is mapped to one of three tiers; only Tier 1 may be
auto-sent. Tier 2 and Tier 3 must be human-approved before delivery.

  Tier 1  Low risk   — Savings / FD / RD / Digital / UPI / Wallet
                       Defensible under RBI Fair Practices Code.
                       AUTO-SEND if compliance approves.

  Tier 2  Medium     — Credit cards, personal/home/auto/education loans
                       RBI Master Direction on Digital Lending DNCR.04
                       requires a "suitability assessment".
                       STAFF REVIEW required.

  Tier 3  High risk  — Mutual funds, insurance, ULIPs, equity
                       IRDAI Advertising Code (insurance) needs
                       principal-officer sign-off; SEBI IA Regulations
                       (MF/equity) restrict recommendations to
                       registered Investment Advisors.
                       STAFF REVIEW required.

Unknown categories default to Tier 2 — fail safe, never auto-send if we
don't know what the product is.
"""
from __future__ import annotations

from typing import Final


TIER_LOW: Final[int] = 1
TIER_MEDIUM: Final[int] = 2
TIER_HIGH: Final[int] = 3


# Canonical category → tier. Keys are matched substring-insensitively
# against `product_category` so e.g. "fixed_deposit" or "FD" or
# "Fixed Deposit" all land on Tier 1.
_TIER_RULES: list[tuple[int, tuple[str, ...]]] = [
    (TIER_HIGH, (
        "mutual_fund", "mutual fund", " mf", "sip",
        "insurance", "ulip", "term_insurance", "term insurance",
        "health_insurance", "health insurance", "life_insurance", "life insurance",
        "equity", "stocks", "demat", "investment",
    )),
    (TIER_MEDIUM, (
        "credit_card", "credit card",
        "personal_loan", "personal loan",
        "home_loan", "home loan",
        "auto_loan", "auto loan", "car_loan", "car loan",
        "education_loan", "education loan",
        "loan", "overdraft",
    )),
    (TIER_LOW, (
        "savings", "savings_account", "savings account",
        "fixed_deposit", "fixed deposit", " fd",
        "recurring_deposit", "recurring deposit", " rd",
        "digital", "upi", "wallet", "yono", "netbanking", "internet banking",
    )),
]

# Regulatory citation per tier — surfaced in the staff UI so reviewers see
# why a nudge requires human sign-off.
TIER_REASON: Final[dict[int, str]] = {
    TIER_LOW: "Low-risk product — auto-approved under RBI Fair Practices Code.",
    TIER_MEDIUM: ("RBI Master Direction on Digital Lending DNCR.04 requires "
                  "a suitability assessment for credit products."),
    TIER_HIGH: ("IRDAI Advertising Code requires principal-officer sign-off "
                "for insurance, and SEBI Investment Advisor Regulations restrict "
                "MF / equity recommendations to registered Investment Advisors."),
}

TIER_LABEL: Final[dict[int, str]] = {
    TIER_LOW: "Tier 1 · Low risk",
    TIER_MEDIUM: "Tier 2 · Medium risk",
    TIER_HIGH: "Tier 3 · High risk",
}


def classify(product_category: str | None) -> int:
    """Return the tier (1/2/3) for a product category. Defaults to Tier 2."""
    text = (product_category or "").strip().lower()
    if not text:
        return TIER_MEDIUM  # unknown → safer default
    haystack = " " + text + " "
    for tier, needles in _TIER_RULES:
        for n in needles:
            if n in haystack:
                return tier
    return TIER_MEDIUM


def infer_product_category(name: str = "", product_type: str = "") -> str:
    """Best-effort canonical category from a product NAME / type.

    The strategist LLM frequently emits only a product name (e.g. "SBI Life
    eShield Next", "SBI Liquid Fund", "SBI Fixed Deposit") with no category
    field. Without a category, tier routing + disclosures break. This maps the
    name to a canonical snake_case category that `classify` and the compliance
    checker understand. Returns "" if nothing matches (caller keeps the default).
    """
    text = f" {name or ''} {product_type or ''} ".lower()

    # --- insurance (Tier 3) ---
    if any(w in text for w in ("term insurance", "eshield", "term life",
                               "life cover", "smart shield", "life insurance")):
        return "term_insurance"
    if any(w in text for w in ("health insurance", "arogya", "medical insurance",
                               "health plan", "critical illness", "mediclaim")):
        return "health_insurance"
    if "ulip" in text:
        return "ulip"
    if "insurance" in text:
        return "term_insurance"
    # --- investments (Tier 3) ---
    if any(w in text for w in ("mutual fund", "mutual_fund", "bluechip", "blue chip",
                               "liquid fund", "equity fund", "elss", "index fund",
                               "balanced fund", "debt fund", "sip", " fund")):
        return "mutual_fund"
    if any(w in text for w in ("equity", "stocks", "demat")):
        return "equity"
    # --- credit (Tier 2) ---
    if "credit card" in text:
        return "credit_card"
    if any(w in text for w in ("personal loan", "home loan", "auto loan", "car loan",
                               "education loan", "overdraft", " loan")):
        return "personal_loan"
    # --- low risk (Tier 1) ---
    if any(w in text for w in ("fixed deposit", "fixed_deposit", " fd ", "term deposit",
                               "tax saver fd", "tax saving fd")):
        return "fixed_deposit"
    if any(w in text for w in ("recurring deposit", " rd ", "recurring")):
        return "recurring_deposit"
    if "ppf" in text or "public provident" in text:
        return "fixed_deposit"   # govt small-savings → treat as low risk
    if "nps" in text or "pension" in text:
        return "fixed_deposit"
    if any(w in text for w in ("savings", "upi", "yono", "wallet", "digital",
                               "netbanking", "net banking", "debit card")):
        return "savings"
    return ""


def is_auto_sendable(product_category: str | None) -> bool:
    """True iff the product category is Tier 1 (auto-sendable)."""
    return classify(product_category) == TIER_LOW


def reason(product_category: str | None) -> str:
    """Human-readable regulatory reason for the tier of this category."""
    return TIER_REASON[classify(product_category)]


def label(product_category: str | None) -> str:
    return TIER_LABEL[classify(product_category)]
