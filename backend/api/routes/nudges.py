"""Nudge management routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from agents.risk_tier import classify, label, reason, TIER_LOW
from api.schemas.analysis import NudgeOut
from api.security import require_staff
from database.connection import get_db
from database.models import Customer, DeliveryReceipt, Nudge
from services import audit as audit_svc
from services import delivery as delivery_svc

router = APIRouter(prefix="/api/nudges", tags=["nudges"])


def _last_receipts_by_nudge(db: Session, nudge_ids: list[str]) -> dict[str, DeliveryReceipt]:
    """Return {nudge_id: latest DeliveryReceipt} for the given nudge_ids in 1 query."""
    if not nudge_ids:
        return {}
    # subquery: max(id) per nudge_id (id is autoincrement, monotonic with created_at)
    sub = (db.query(DeliveryReceipt.nudge_id, func.max(DeliveryReceipt.id).label("max_id"))
           .filter(DeliveryReceipt.nudge_id.in_(nudge_ids))
           .group_by(DeliveryReceipt.nudge_id).subquery())
    rows = (db.query(DeliveryReceipt)
            .join(sub, DeliveryReceipt.id == sub.c.max_id)
            .all())
    return {r.nudge_id: r for r in rows}


def _customers_by_id(db: Session, customer_ids: list[str]) -> dict[str, Customer]:
    if not customer_ids:
        return {}
    rows = db.query(Customer).filter(Customer.id.in_(customer_ids)).all()
    return {c.id: c for c in rows}


def _enrich(nudge: Nudge, *, customer: Customer | None,
            last: DeliveryReceipt | None) -> dict:
    """Return a dict shaped for NudgeOut from already-fetched related rows."""
    tier = classify(nudge.product_category)
    return {
        "id": nudge.id, "customer_id": nudge.customer_id,
        "customer_name": customer.name if customer else None,
        "priority": nudge.priority,
        "target_gap": nudge.target_gap, "product_name": nudge.product_name,
        "product_category": nudge.product_category,
        "psychological_frame": nudge.psychological_frame,
        "message_draft": nudge.message_draft, "channel": nudge.channel,
        "expected_conversion": nudge.expected_conversion,
        "compliance_status": nudge.compliance_status,
        "compliance_notes": nudge.compliance_notes or {},
        "status": nudge.status,
        "created_at": nudge.created_at.isoformat() + "Z" if nudge.created_at else None,
        "delivery_status": last.status if last else None,
        "delivery_provider": last.provider if last else None,
        "delivery_error": last.error if last else None,
        "sent_at": (last.created_at.isoformat() + "Z"
                    if last and last.status == "sent" and last.created_at else None),
        "tier": tier,
        "tier_label": label(nudge.product_category),
        "tier_reason": reason(nudge.product_category),
        # A nudge requires staff review when it's in a deliverable compliance
        # state, hasn't been sent, AND falls outside Tier 1.
        "requires_review": (tier != TIER_LOW
                            and nudge.compliance_status in ("approved", "approved_with_modification")
                            and nudge.status == "pending"),
    }


def _enrich_one(nudge: Nudge, db: Session) -> dict:
    """Single-nudge variant used by approve/reject — does the 2 lookups inline."""
    cust = db.query(Customer).filter(Customer.id == nudge.customer_id).first()
    last = (db.query(DeliveryReceipt)
            .filter(DeliveryReceipt.nudge_id == nudge.id)
            .order_by(DeliveryReceipt.created_at.desc()).first())
    return _enrich(nudge, customer=cust, last=last)


def _enrich_many(rows: list[Nudge], db: Session) -> list[dict]:
    """Batch the customer + last-receipt lookups into 2 queries total."""
    cust_map = _customers_by_id(db, list({r.customer_id for r in rows}))
    receipt_map = _last_receipts_by_nudge(db, [r.id for r in rows])
    return [_enrich(r, customer=cust_map.get(r.customer_id),
                    last=receipt_map.get(r.id)) for r in rows]


@router.get("", response_model=list[NudgeOut])
def list_nudges(status: str | None = None, limit: int = 200,
                db: Session = Depends(get_db)):
    q = db.query(Nudge)
    if status:
        q = q.filter(Nudge.status == status)
    else:
        # hide nudges superseded by a newer analysis from the default log/queue
        q = q.filter(Nudge.status != "superseded")
    rows = q.order_by(Nudge.created_at.desc()).limit(max(1, min(limit, 500))).all()
    return _enrich_many(rows, db)


@router.get("/{customer_id}", response_model=list[NudgeOut])
def customer_nudges(customer_id: str, db: Session = Depends(get_db)):
    rows = (db.query(Nudge).filter(Nudge.customer_id == customer_id,
                                   Nudge.status != "superseded")
            .order_by(Nudge.priority).all())
    return _enrich_many(rows, db)


@router.put("/{nudge_id}/approve", response_model=NudgeOut)
def approve_nudge(nudge_id: str, db: Session = Depends(get_db),
                  staff: str = Depends(require_staff)):
    n = _set_status(nudge_id, "approved", db)
    audit_svc.record("nudge.approve", customer_id=n.customer_id, actor=staff,
                     entity_type="nudge", entity_id=nudge_id)
    return _enrich_one(n, db)


@router.put("/{nudge_id}/reject", response_model=NudgeOut)
def reject_nudge(nudge_id: str, db: Session = Depends(get_db),
                 staff: str = Depends(require_staff)):
    n = _set_status(nudge_id, "rejected", db)
    audit_svc.record("nudge.reject", customer_id=n.customer_id, actor=staff,
                     entity_type="nudge", entity_id=nudge_id)
    return _enrich_one(n, db)


@router.put("/{nudge_id}/send")
def send_nudge(nudge_id: str, staff: str = Depends(require_staff)):
    """Actually deliver the nudge over its channel (consent + compliance gated)."""
    result = delivery_svc.deliver_nudge(nudge_id, actor=staff)
    if result["status"] not in ("sent",):
        # surface why it didn't go out, but don't 500 — it's a business outcome
        return {"nudge_id": nudge_id, "delivered": False, **result}
    return {"nudge_id": nudge_id, "delivered": True, **result}


@router.get("/{nudge_id}/deliveries")
def nudge_deliveries(nudge_id: str, db: Session = Depends(get_db)):
    rows = (db.query(DeliveryReceipt)
            .filter(DeliveryReceipt.nudge_id == nudge_id)
            .order_by(DeliveryReceipt.created_at.desc()).all())
    return [{
        "id": r.id, "channel": r.channel, "provider": r.provider, "status": r.status,
        "provider_message_id": r.provider_message_id, "error": r.error,
        "created_at": r.created_at.isoformat() + "Z" if r.created_at else None,
    } for r in rows]


def _set_status(nudge_id: str, status: str, db: Session) -> Nudge:
    n = db.query(Nudge).filter(Nudge.id == nudge_id).first()
    if not n:
        raise HTTPException(404, "Nudge not found")
    n.status = status
    db.commit()
    db.refresh(n)
    return n
