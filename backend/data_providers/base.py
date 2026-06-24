"""Data provider abstraction.

Every source of customer + transaction data implements this interface so the
agent pipeline never knows (or cares) whether the data came from a local
synthetic store, the SBI Innovation Hub sandbox, or an RBI Account Aggregator.

This is the seam that makes the prototype "sandbox-ready by design": swap the
provider via the DATA_PROVIDER env var, agents stay untouched.
"""
from __future__ import annotations

import abc


class DataProvider(abc.ABC):
    """Read access to customer + transaction data for a given source."""

    name: str = "base"
    #: whether this provider requires per-customer consent before data access
    requires_consent: bool = False

    @abc.abstractmethod
    def list_customers(self) -> list[dict]:
        ...

    @abc.abstractmethod
    def get_customer(self, customer_id: str) -> dict | None:
        ...

    @abc.abstractmethod
    def get_transactions(self, customer_id: str) -> list[dict]:
        ...

    def health(self) -> dict:
        """Report whether the provider is ready to serve data."""
        return {"provider": self.name, "ready": True, "detail": "ok"}
