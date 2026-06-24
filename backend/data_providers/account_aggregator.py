"""Account Aggregator (AA) data provider — RBI consent-based data sharing.

Implements the FIU (Financial Information User) side of the AA flow used by
aggregators like Setu, Finvu, OneMoney and Sahamati's SahamatiNet:

    1. Create a consent request (purpose, FI types, data range, frequency).
    2. Customer approves in the AA app -> consent handle becomes ACTIVE.
    3. Create a data session (FI data request) against the active consent.
    4. Poll / fetch the FI data, then normalise transactions.

This provider is consent-native: get_transactions REQUIRES an active AA consent
handle for the customer (looked up locally), satisfying DPDP purpose-limitation.
Endpoints + auth are configured via env. Field mappings follow the ReBIT FI
schema (Deposit account) used across AA aggregators.
"""
from __future__ import annotations

import logging

import httpx

from config import settings

from .base import DataProvider

log = logging.getLogger("finpulse.account_aggregator")


class ConsentRequired(RuntimeError):
    """Raised when no active AA consent exists for the customer."""


class AccountAggregatorProvider(DataProvider):
    name = "account_aggregator"
    requires_consent = True

    def __init__(self) -> None:
        self._base = settings.aa_base_url.rstrip("/")

    def _client(self) -> httpx.Client:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "client_api_key": settings.aa_client_id,
        }
        if settings.aa_client_secret:
            headers["x-client-secret"] = settings.aa_client_secret
        return httpx.Client(base_url=self._base, headers=headers, timeout=45.0)

    def health(self) -> dict:
        if not settings.has_account_aggregator:
            return {"provider": self.name, "ready": False,
                    "detail": "AA_BASE_URL / client / FIU id not configured"}
        return {"provider": self.name, "ready": True,
                "detail": f"FIU {settings.aa_fiu_id} configured"}

    # --- consent lifecycle -------------------------------------------------
    def create_consent_request(self, customer_phone: str, purpose: str,
                               fi_types: list[str] | None = None) -> dict:
        """Kick off an AA consent request. Returns the consent handle + redirect."""
        body = {
            "fiu": {"id": settings.aa_fiu_id},
            "customer": {"identifiers": [{"type": "MOBILE", "value": customer_phone}]},
            "purpose": {"code": "101", "text": purpose},
            "fiTypes": fi_types or ["DEPOSIT"],
            "consentMode": "STORE",
            "fetchType": "PERIODIC",
        }
        with self._client() as c:
            r = c.post("/consents", json=body)
            r.raise_for_status()
            return r.json()

    def consent_status(self, consent_handle: str) -> dict:
        with self._client() as c:
            r = c.get(f"/consents/{consent_handle}")
            r.raise_for_status()
            return r.json()

    # --- data fetch --------------------------------------------------------
    def _active_consent_handle(self, customer_id: str) -> str | None:
        from database.connection import SessionLocal
        from database.models import Consent
        db = SessionLocal()
        try:
            c = (db.query(Consent)
                 .filter(Consent.customer_id == customer_id,
                         Consent.status == "granted",
                         Consent.aa_consent_handle.isnot(None))
                 .order_by(Consent.granted_at.desc()).first())
            return c.aa_consent_handle if c else None
        finally:
            db.close()

    def _create_data_session(self, consent_handle: str) -> str:
        with self._client() as c:
            r = c.post("/sessions", json={"consentId": consent_handle,
                                          "format": "json"})
            r.raise_for_status()
            return r.json()["sessionId"]

    def _fetch_fi_data(self, session_id: str) -> dict:
        with self._client() as c:
            r = c.get(f"/sessions/{session_id}")
            r.raise_for_status()
            return r.json()

    @staticmethod
    def _norm_txn(d: dict, customer_id: str) -> dict:
        return {
            "id": d.get("txnId"),
            "customer_id": customer_id,
            "date": (d.get("valueDate") or d.get("transactionTimestamp") or "")[:10],
            "type": (d.get("type") or "").lower(),  # CREDIT/DEBIT -> credit/debit
            "amount": float(d.get("amount", 0)),
            "description": d.get("narration"),
            "category": d.get("category", "uncategorised"),
            "channel": d.get("mode", "aa"),
            "balance_after": float(d.get("currentBalance", 0) or 0),
        }

    def get_transactions(self, customer_id: str) -> list[dict]:
        handle = self._active_consent_handle(customer_id)
        if not handle:
            raise ConsentRequired(
                f"No active Account Aggregator consent for {customer_id}. "
                "Create + approve a consent before fetching financial data."
            )
        session_id = self._create_data_session(handle)
        data = self._fetch_fi_data(session_id)
        txns: list[dict] = []
        for fi in data.get("fips", data.get("FI", [])):
            for acc in fi.get("accounts", fi.get("data", [])):
                for t in acc.get("transactions", {}).get("transaction", acc.get("transactions", [])):
                    txns.append(self._norm_txn(t, customer_id))
        return txns

    def get_customer(self, customer_id: str) -> dict | None:
        # AA shares financial data, not CRM profile. Profile/contact come from
        # the bank's own systems (synthetic store here); transactions come live.
        from .synthetic import SyntheticProvider
        return SyntheticProvider().get_customer(customer_id)

    def list_customers(self) -> list[dict]:
        from .synthetic import SyntheticProvider
        return SyntheticProvider().list_customers()
