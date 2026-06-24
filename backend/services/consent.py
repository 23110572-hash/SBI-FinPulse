"""Consent service — DPDP-aligned consent lifecycle + checks.

A consent is purpose-bound, scoped to data categories and channels, and time-
boxed. The engagement engine and delivery layer call `has_active_consent` /
`check` BEFORE acting, so every proactive touch traces back to a live consent.
"""
from __future__ import annotations

import datetime as dt
import uuid

from database.connection import SessionLocal
from database.models import Consent

from . import audit

# canonical purposes
PURPOSE_ENGAGEMENT = "proactive_engagement"
PURPOSE_MARKETING = "marketing"
PURPOSE_ANALYSIS = "data_analysis"

DEFAULT_CATEGORIES = ["profile", "transactions", "balance"]
DEFAULT_CHANNELS = ["email"]


def _now() -> dt.datetime:
    return dt.datetime.utcnow()


def grant(customer_id: str, purpose: str = PURPOSE_ENGAGEMENT, *,
          data_categories: list[str] | None = None,
          channels: list[str] | None = None,
          validity_days: int = 365, source: str = "customer_app",
          aa_consent_handle: str | None = None, actor: str = "customer") -> dict:
    db = SessionLocal()
    try:
        # supersede any existing active consent for the same purpose
        existing = (db.query(Consent)
                    .filter(Consent.customer_id == customer_id,
                            Consent.purpose == purpose,
                            Consent.status == "granted").all())
        for e in existing:
            e.status = "revoked"
            e.revoked_at = _now()

        cid = f"CNS_{uuid.uuid4().hex[:8].upper()}"
        c = Consent(
            id=cid, customer_id=customer_id, purpose=purpose,
            data_categories=data_categories or DEFAULT_CATEGORIES,
            channels=channels or DEFAULT_CHANNELS,
            status="granted", granted_at=_now(),
            expires_at=_now() + dt.timedelta(days=validity_days),
            source=source, aa_consent_handle=aa_consent_handle,
        )
        db.add(c)
        db.commit()
        db.refresh(c)
        result = _to_dict(c)
    finally:
        db.close()
    audit.record("consent.grant", customer_id=customer_id, actor=actor,
                 entity_type="consent", entity_id=result["id"],
                 detail={"purpose": purpose, "channels": result["channels"]})
    return result


def revoke(customer_id: str, purpose: str = PURPOSE_ENGAGEMENT, actor: str = "customer") -> int:
    db = SessionLocal()
    try:
        rows = (db.query(Consent)
                .filter(Consent.customer_id == customer_id,
                        Consent.purpose == purpose,
                        Consent.status == "granted").all())
        for r in rows:
            r.status = "revoked"
            r.revoked_at = _now()
        n = len(rows)
        db.commit()
    finally:
        db.close()
    audit.record("consent.revoke", customer_id=customer_id, actor=actor,
                 entity_type="consent", detail={"purpose": purpose, "count": n})
    return n


def _active(db, customer_id: str, purpose: str) -> Consent | None:
    c = (db.query(Consent)
         .filter(Consent.customer_id == customer_id,
                 Consent.purpose == purpose,
                 Consent.status == "granted")
         .order_by(Consent.granted_at.desc()).first())
    if not c:
        return None
    if c.expires_at and c.expires_at < _now():
        c.status = "expired"
        db.commit()
        return None
    return c


def has_active_consent(customer_id: str, purpose: str = PURPOSE_ENGAGEMENT) -> bool:
    db = SessionLocal()
    try:
        return _active(db, customer_id, purpose) is not None
    finally:
        db.close()


def check(customer_id: str, *, purpose: str = PURPOSE_ENGAGEMENT,
          channel: str | None = None) -> dict:
    """Return a structured consent decision used by compliance + delivery."""
    db = SessionLocal()
    try:
        c = _active(db, customer_id, purpose)
        if not c:
            return {"allowed": False, "reason": f"no active consent for '{purpose}'",
                    "purpose": purpose}
        if channel and channel not in (c.channels or []):
            return {"allowed": False, "reason": f"channel '{channel}' not in consent scope",
                    "purpose": purpose, "consent_id": c.id, "channels": c.channels}
        return {"allowed": True, "purpose": purpose, "consent_id": c.id,
                "channels": c.channels, "expires_at": c.expires_at.isoformat() + "Z"
                if c.expires_at else None}
    finally:
        db.close()


def list_for_customer(customer_id: str) -> list[dict]:
    db = SessionLocal()
    try:
        rows = (db.query(Consent).filter(Consent.customer_id == customer_id)
                .order_by(Consent.granted_at.desc()).all())
        return [_to_dict(r) for r in rows]
    finally:
        db.close()


def _to_dict(c: Consent) -> dict:
    return {
        "id": c.id, "customer_id": c.customer_id, "purpose": c.purpose,
        "data_categories": c.data_categories or [], "channels": c.channels or [],
        "status": c.status, "source": c.source,
        "granted_at": c.granted_at.isoformat() + "Z" if c.granted_at else None,
        "expires_at": c.expires_at.isoformat() + "Z" if c.expires_at else None,
        "revoked_at": c.revoked_at.isoformat() + "Z" if c.revoked_at else None,
        "aa_consent_handle": c.aa_consent_handle,
    }
