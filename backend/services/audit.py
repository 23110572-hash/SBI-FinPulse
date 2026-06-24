"""Audit trail service — records every consequential action for compliance."""
from __future__ import annotations

import logging

from database.connection import SessionLocal
from database.models import AuditLog

log = logging.getLogger("finpulse.audit")


def record(action: str, *, customer_id: str | None = None, actor: str = "system",
           entity_type: str | None = None, entity_id: str | None = None,
           detail: dict | None = None) -> None:
    """Append an audit entry. Never raises into the caller."""
    db = SessionLocal()
    try:
        db.add(AuditLog(
            action=action, customer_id=customer_id, actor=actor,
            entity_type=entity_type, entity_id=entity_id, detail=detail or {},
        ))
        db.commit()
    except Exception as e:  # auditing must never break the main flow
        log.warning("audit record failed for %s: %s", action, e)
        db.rollback()
    finally:
        db.close()


def list_logs(customer_id: str | None = None, limit: int = 100) -> list[dict]:
    db = SessionLocal()
    try:
        q = db.query(AuditLog)
        if customer_id:
            q = q.filter(AuditLog.customer_id == customer_id)
        rows = q.order_by(AuditLog.created_at.desc()).limit(limit).all()
        return [{
            "id": r.id, "customer_id": r.customer_id, "actor": r.actor,
            "action": r.action, "entity_type": r.entity_type, "entity_id": r.entity_id,
            "detail": r.detail, "created_at": r.created_at.isoformat() + "Z" if r.created_at else None,
        } for r in rows]
    finally:
        db.close()
