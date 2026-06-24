"""Data provider registry.

Selects the active provider from settings.data_provider and exposes a single
get_provider() the rest of the app uses. Falls back to synthetic if a remote
provider isn't configured, so the demo never hard-fails.
"""
from __future__ import annotations

import logging
from functools import lru_cache

from config import settings

from .base import DataProvider
from .synthetic import SyntheticProvider

log = logging.getLogger("finpulse.data_providers")


@lru_cache
def get_provider() -> DataProvider:
    mode = (settings.data_provider or "synthetic").lower()

    if mode == "sbi_sandbox":
        if settings.has_sbi_sandbox:
            from .sbi_sandbox import SBISandboxProvider
            return SBISandboxProvider()
        log.warning("DATA_PROVIDER=sbi_sandbox but SBI sandbox not configured; "
                    "falling back to synthetic.")

    elif mode == "account_aggregator":
        if settings.has_account_aggregator:
            from .account_aggregator import AccountAggregatorProvider
            return AccountAggregatorProvider()
        log.warning("DATA_PROVIDER=account_aggregator but AA not configured; "
                    "falling back to synthetic.")

    return SyntheticProvider()


def active_provider_name() -> str:
    return get_provider().name


__all__ = ["DataProvider", "get_provider", "active_provider_name"]
