"""Lightweight data access used by agent tools and the analysis engine.

Delegates to the active DataProvider (synthetic / SBI sandbox / Account
Aggregator), selected via the DATA_PROVIDER env var. Agents call these helpers
and never need to know where the data physically comes from.

A request-scoped cache (set via ``set_run_cache``) lets a single crew run share
one fetch of a customer + their transactions across all five agents and the
deterministic re-merge — saving 3-5 round-trips to the database per run.
"""
from __future__ import annotations

import contextvars

from data_providers import get_provider

# Per-run cache. Set by ``run_crew`` (or any orchestrator) at the start of a
# request and cleared on the way out. Threads / async tasks each get their own
# view — ContextVar ensures we don't leak data across concurrent crew runs.
_run_cache: "contextvars.ContextVar[dict | None]" = contextvars.ContextVar(
    "finpulse_run_cache", default=None)


class _Cache:
    """Tiny manager so callers can ``with begin_run_cache(): …``."""

    def __enter__(self):
        self._token = _run_cache.set({})
        return self

    def __exit__(self, *_exc):
        _run_cache.reset(self._token)


def begin_run_cache() -> _Cache:
    """Context manager: scope a fresh cache to the current crew run."""
    return _Cache()


def get_customer(customer_id: str) -> dict | None:
    cache = _run_cache.get()
    if cache is not None and ("cust", customer_id) in cache:
        return cache[("cust", customer_id)]
    val = get_provider().get_customer(customer_id)
    if cache is not None:
        cache[("cust", customer_id)] = val
    return val


def get_transactions(customer_id: str) -> list[dict]:
    cache = _run_cache.get()
    if cache is not None and ("txn", customer_id) in cache:
        return cache[("txn", customer_id)]
    val = get_provider().get_transactions(customer_id)
    if cache is not None:
        cache[("txn", customer_id)] = val
    return val


def list_customers() -> list[dict]:
    return get_provider().list_customers()
