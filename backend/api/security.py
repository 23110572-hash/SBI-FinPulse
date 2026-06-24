"""Authentication / authorization dependencies.

- require_staff : protects the staff console + nudge management + dashboard.
                  Expects `Authorization: Bearer <STAFF_API_TOKEN>`.
- customer_scope: ensures a caller may only act on their own customer id
                  (or a staff token may act on anyone). Enforced only when
                  ENFORCE_CUSTOMER_SCOPE=true so the demo stays frictionless.

Both are no-ops (open) when the relevant token isn't configured, so the app
runs out-of-the-box and tightens automatically once tokens are set.
"""
from __future__ import annotations

from fastapi import Header, HTTPException

from config import settings


def _bearer(value: str | None) -> str | None:
    if not value:
        return None
    return value[7:].strip() if value.lower().startswith("bearer ") else value.strip()


def require_staff(authorization: str | None = Header(default=None)) -> str:
    """Dependency guarding staff-only routes."""
    if not settings.staff_api_token:
        # token not configured -> open (demo mode)
        return "staff:anonymous"
    token = _bearer(authorization)
    if token != settings.staff_api_token:
        raise HTTPException(status_code=401, detail="Staff authentication required")
    return "staff:authenticated"


def customer_scope(customer_id: str,
                   x_customer_token: str | None = Header(default=None),
                   authorization: str | None = Header(default=None)) -> str:
    """Dependency ensuring the caller may act on this customer id."""
    if not settings.enforce_customer_scope:
        return customer_id
    # staff token grants access to any customer
    if settings.staff_api_token and _bearer(authorization) == settings.staff_api_token:
        return customer_id
    # otherwise the per-customer token must match the customer id
    if not x_customer_token or x_customer_token != customer_id:
        raise HTTPException(status_code=403, detail="Not authorised for this customer")
    return customer_id
