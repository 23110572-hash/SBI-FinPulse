"""SBI Innovation Hub / APIX sandbox data provider.

Connects to SBI's sandbox APIs (provisioned to shortlisted teams in Round 2).
Endpoints + auth are configured via env; responses are normalised into the same
dict shape the agents already consume, so nothing downstream changes.

Because SBI's exact API contract is only disclosed inside the sandbox, the
endpoint paths and field mappings are kept configurable / defensive. Fill in
SBI_API_BASE + credentials in .env and adjust the path constants if SBI's
catalogue differs.
"""
from __future__ import annotations

import logging

import httpx

from config import settings

from .base import DataProvider

log = logging.getLogger("finpulse.sbi_sandbox")

# Adjust these to match the SBI sandbox catalogue once provisioned.
PATH_CUSTOMERS = "/v1/customers"
PATH_CUSTOMER = "/v1/customers/{id}"
PATH_TRANSACTIONS = "/v1/customers/{id}/transactions"


class SBISandboxProvider(DataProvider):
    name = "sbi_sandbox"
    requires_consent = False  # sandbox uses mock data; prod would add consent

    def __init__(self) -> None:
        self._base = settings.sbi_api_base.rstrip("/")

    def _client(self) -> httpx.Client:
        headers = {"Accept": "application/json"}
        if settings.sbi_api_key:
            headers["x-api-key"] = settings.sbi_api_key
        if settings.sbi_client_id:
            headers["client-id"] = settings.sbi_client_id
            headers["client-secret"] = settings.sbi_client_secret
        return httpx.Client(base_url=self._base, headers=headers, timeout=30.0)

    def health(self) -> dict:
        if not settings.has_sbi_sandbox:
            return {"provider": self.name, "ready": False,
                    "detail": "SBI_API_BASE / credentials not configured"}
        try:
            with self._client() as c:
                r = c.get(PATH_CUSTOMERS, params={"limit": 1})
                r.raise_for_status()
            return {"provider": self.name, "ready": True, "detail": "reachable"}
        except Exception as e:
            return {"provider": self.name, "ready": False, "detail": str(e)}

    # --- normalisation -----------------------------------------------------
    @staticmethod
    def _norm_customer(d: dict) -> dict:
        return {
            "id": d.get("customerId") or d.get("id"),
            "customer_id": d.get("customerId") or d.get("id"),
            "name": d.get("name") or d.get("fullName"),
            "age": d.get("age"),
            "location": d.get("city") or d.get("location"),
            "persona": d.get("segment") or d.get("persona"),
            "income_band": d.get("incomeBand"),
            "monthly_income": d.get("monthlyIncome", 0),
            "monthly_spending": d.get("monthlySpending", 0),
            "savings_rate": d.get("savingsRate", 0.0),
            "current_balance": d.get("balance") or d.get("currentBalance", 0.0),
            "risk_appetite": d.get("riskAppetite"),
            "digital_activity": d.get("digitalActivity"),
            "products_held": d.get("productsHeld", []),
            "products_not_held": d.get("productsNotHeld", []),
            "phone": d.get("mobile") or d.get("phone"),
            "email": d.get("email"),
            "whatsapp_opt_in": bool(d.get("whatsappOptIn", False)),
            "preferred_language": d.get("language", "en"),
        }

    @staticmethod
    def _norm_txn(d: dict, customer_id: str) -> dict:
        return {
            "id": d.get("txnId") or d.get("id"),
            "customer_id": customer_id,
            "date": (d.get("valueDate") or d.get("date") or "")[:10],
            "type": (d.get("drCr") or d.get("type") or "").lower().replace("dr", "debit").replace("cr", "credit"),
            "amount": float(d.get("amount", 0)),
            "description": d.get("narration") or d.get("description"),
            "category": d.get("category", "uncategorised"),
            "channel": d.get("mode") or d.get("channel"),
            "balance_after": float(d.get("balanceAfter", 0) or 0),
        }

    def list_customers(self) -> list[dict]:
        with self._client() as c:
            r = c.get(PATH_CUSTOMERS)
            r.raise_for_status()
            data = r.json()
        rows = data.get("data", data) if isinstance(data, dict) else data
        return [self._norm_customer(d) for d in rows]

    def get_customer(self, customer_id: str) -> dict | None:
        with self._client() as c:
            r = c.get(PATH_CUSTOMER.format(id=customer_id))
            if r.status_code == 404:
                return None
            r.raise_for_status()
            d = r.json()
        return self._norm_customer(d.get("data", d) if isinstance(d, dict) else d)

    def get_transactions(self, customer_id: str) -> list[dict]:
        with self._client() as c:
            r = c.get(PATH_TRANSACTIONS.format(id=customer_id))
            r.raise_for_status()
            data = r.json()
        rows = data.get("data", data) if isinstance(data, dict) else data
        return [self._norm_txn(d, customer_id) for d in rows]
