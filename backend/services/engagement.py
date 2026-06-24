"""Proactive engagement engine.

This is what makes FinPulse *proactive* rather than staff-click-driven:

  - scan_all()        : periodic sweep (run by the scheduler) that detects NEW
                        life events / pattern shifts per customer and acts.
  - ingest_event()    : inbound webhook entry (e.g. a new transaction) that can
                        trigger engagement in real time.
  - process_customer(): runs the agent crew for one customer, gated on consent,
                        and optionally auto-delivers fully-approved nudges.

Every trigger is recorded as an EngagementEvent and audited.
"""
from __future__ import annotations

import datetime as dt
import logging
import uuid

from agents.repository import get_customer, get_transactions
from agents.tools.life_event_detector import detect_life_events
from config import settings
from database.connection import SessionLocal
from database.models import Analysis, EngagementEvent
from services import audit, consent

log = logging.getLogger("finpulse.engagement")


def _now() -> dt.datetime:
    return dt.datetime.utcnow()


def _new_event_id() -> str:
    return f"EVT_{uuid.uuid4().hex[:8].upper()}"


def _last_analysis(db, customer_id: str) -> Analysis | None:
    return (db.query(Analysis).filter(Analysis.customer_id == customer_id)
            .order_by(Analysis.created_at.desc()).first())


def _known_signals(analysis: Analysis | None) -> set[str]:
    if not analysis or not analysis.profile:
        return set()
    events = analysis.profile.get("life_events_detected", []) or []
    return {e.get("event") for e in events if isinstance(e, dict)}


def detect_new_signals(customer_id: str,
                       *,
                       _last: Analysis | None | object = ...) -> list[dict]:
    """Return life-event signals not present in the customer's last analysis.

    ``_last`` lets callers (e.g. scan_all) inject an already-fetched Analysis
    so we don't re-query for the same row.
    """
    cust = get_customer(customer_id)
    if not cust:
        return []
    txns = get_transactions(customer_id)
    detected = detect_life_events(txns, cust)

    if _last is ...:  # not provided — fetch
        db = SessionLocal()
        try:
            known = _known_signals(_last_analysis(db, customer_id))
        finally:
            db.close()
    else:
        known = _known_signals(_last)  # type: ignore[arg-type]

    return [e for e in detected if e.get("event") not in known]


def record_event(customer_id: str, signal: str, *, event_type: str = "life_event",
                 confidence: float = 0.0, source: str = "scheduler",
                 payload: dict | None = None) -> str:
    db = SessionLocal()
    try:
        evt = EngagementEvent(
            id=_new_event_id(), customer_id=customer_id, event_type=event_type,
            signal=signal, confidence=confidence, source=source,
            payload=payload or {}, status="detected",
        )
        db.add(evt)
        db.commit()
        eid = evt.id
    finally:
        db.close()
    audit.record("engagement.event_detected", customer_id=customer_id, actor=f"source:{source}",
                 entity_type="engagement_event", entity_id=eid,
                 detail={"signal": signal, "type": event_type, "confidence": confidence})
    return eid


def _mark_event(event_id: str, status: str) -> None:
    db = SessionLocal()
    try:
        evt = db.query(EngagementEvent).filter(EngagementEvent.id == event_id).first()
        if evt:
            evt.status = status
            if status in ("processed", "skipped"):
                evt.processed_at = _now()
            db.commit()
    finally:
        db.close()


def _is_stale_from(last: Analysis | None) -> bool:
    if not last or not last.created_at:
        return True
    age = _now() - last.created_at
    return age > dt.timedelta(hours=settings.reanalyze_after_hours)


def _is_stale(customer_id: str) -> bool:
    db = SessionLocal()
    try:
        return _is_stale_from(_last_analysis(db, customer_id))
    finally:
        db.close()


def process_customer(customer_id: str, *, trigger: str = "manual",
                     event_id: str | None = None, auto_send: bool | None = None) -> dict:
    """Run the crew for one customer (consent-gated) and optionally auto-deliver.

    Returns a summary dict describing what happened.
    """
    # consent is mandatory for proactive processing
    if trigger != "manual" and not consent.has_active_consent(
            customer_id, consent.PURPOSE_ENGAGEMENT):
        if event_id:
            _mark_event(event_id, "skipped")
        audit.record("engagement.skipped_no_consent", customer_id=customer_id,
                     actor="system", detail={"trigger": trigger})
        return {"customer_id": customer_id, "status": "skipped_no_consent"}

    if event_id:
        _mark_event(event_id, "processing")

    # lazy import: heavy LLM stack
    from agents import run_crew
    from api.store import save_analysis

    result = run_crew(customer_id)
    save_analysis(result)
    audit.record("analysis.run", customer_id=customer_id, actor=f"trigger:{trigger}",
                 entity_type="analysis", detail={"trigger": trigger, "event_id": event_id})

    delivered = []
    do_send = settings.auto_send_approved if auto_send is None else auto_send
    if do_send:
        delivered = _auto_deliver_approved(customer_id)

    if event_id:
        _mark_event(event_id, "processed")

    return {"customer_id": customer_id, "status": "processed", "trigger": trigger,
            "nudges": len(result.get("nudge_plan", {}).get("nudges", [])),
            "delivered": delivered}


def _auto_deliver_approved(customer_id: str) -> list[dict]:
    """Send AT MOST one approved nudge per customer per delivery window.

    Caps applied (in order):
      1. 24-hour customer-level cooldown — if any email was successfully sent
         to this customer in the last DELIVERY_COOLDOWN_HOURS, skip.
      2. 30-day same-gap cooldown — if a nudge for the same target_gap was
         delivered to this customer in the last SAME_GAP_COOLDOWN_DAYS, skip
         that nudge and try the next one.
      3. Risk tier — only Tier 1 (savings/FD/digital) is auto-sendable. Tier 2
         (credit) and Tier 3 (MF/insurance) are routed to the staff Review
         Queue per RBI DNCR.04 / IRDAI / SEBI IA regulations.
      4. Channel is forced to PROACTIVE_CHANNEL (email).
      5. Compliance gate: approved or approved_with_modification.
    Returns the list of receipts (0 or 1 entries).
    """
    from agents.risk_tier import (TIER_LOW, classify, label, reason)
    from database.models import DeliveryReceipt, Nudge
    from services import delivery

    cooldown_hours = max(1, settings.delivery_cooldown_hours)
    same_gap_days = max(1, settings.same_gap_cooldown_days)
    now = _now()
    cooldown_cutoff = now - dt.timedelta(hours=cooldown_hours)
    gap_cutoff = now - dt.timedelta(days=same_gap_days)

    db = SessionLocal()
    try:
        # 1. Customer-level 24h cap.
        recently_sent = (db.query(DeliveryReceipt)
                         .filter(DeliveryReceipt.customer_id == customer_id,
                                 DeliveryReceipt.status == "sent",
                                 DeliveryReceipt.created_at >= cooldown_cutoff)
                         .first())
        if recently_sent:
            log.info("auto-deliver: %s within %sh cooldown — skipped",
                     customer_id, cooldown_hours)
            audit.record("engagement.skipped_cooldown", customer_id=customer_id,
                         actor="system",
                         detail={"reason": "delivery_cooldown",
                                 "hours": cooldown_hours,
                                 "last_sent_receipt_id": recently_sent.id})
            return []

        # 2. Same-gap 30-day cooldown — collect gaps already addressed.
        recent_gap_rows = (db.query(Nudge.target_gap)
                           .join(DeliveryReceipt,
                                 DeliveryReceipt.nudge_id == Nudge.id)
                           .filter(Nudge.customer_id == customer_id,
                                   DeliveryReceipt.status == "sent",
                                   DeliveryReceipt.created_at >= gap_cutoff)
                           .all())
        recent_gaps = {row[0] for row in recent_gap_rows if row[0]}

        # 3. Candidate nudges: approved (or approved_with_modification),
        # status=pending, ordered by priority.
        approved_statuses = ("approved", "approved_with_modification")
        candidates = (db.query(Nudge)
                      .filter(Nudge.customer_id == customer_id,
                              Nudge.compliance_status.in_(approved_statuses),
                              Nudge.status == "pending")
                      .order_by(Nudge.priority.asc()).all())

        # 3a. Tier 2/3 — record in audit and leave for staff review.
        for n in candidates:
            tier = classify(n.product_category)
            if tier == TIER_LOW:
                continue
            audit.record("engagement.queued_for_review", customer_id=customer_id,
                         actor="system", entity_type="nudge", entity_id=n.id,
                         detail={"tier": tier, "tier_label": label(n.product_category),
                                 "reason": reason(n.product_category),
                                 "product_category": n.product_category,
                                 "product_name": n.product_name})

        # 3b. Pick the highest-priority Tier-1 candidate that hasn't already
        # been emailed about its target_gap recently.
        chosen: Nudge | None = None
        for n in candidates:
            if classify(n.product_category) != TIER_LOW:
                continue
            if n.target_gap and n.target_gap in recent_gaps:
                continue
            chosen = n
            break

        if not chosen:
            return []

        # Force the proactive channel before delivery so the agent's choice
        # (whatsapp/sms/etc.) cannot leak into the real send path.
        if chosen.channel != settings.proactive_channel:
            chosen.channel = settings.proactive_channel
            db.commit()
        chosen_id = chosen.id
    finally:
        db.close()

    receipt = delivery.deliver_nudge(chosen_id, actor="engagement_engine")
    return [receipt]


def scan_all() -> dict:
    """Periodic sweep across all customers. Triggered by the scheduler.

    Guarded by a Postgres advisory lock so that if the web app runs with more
    than one worker, only ONE of them actually performs the sweep — otherwise
    every worker would fire at 22:00 and a customer could be emailed N times.
    The lock is held only for the duration of the scan and released after.
    """
    from sqlalchemy import text
    from database.connection import engine

    _LOCK_ID = 774411  # arbitrary constant shared by all workers
    lock_conn = None
    try:
        lock_conn = engine.connect()
        got = lock_conn.execute(text("SELECT pg_try_advisory_lock(:k)"),
                                {"k": _LOCK_ID}).scalar()
        if not got:
            log.info("scan_all: another worker holds the scan lock — skipping.")
            return {"scanned": 0, "triggered": 0, "skipped": 0, "events": [],
                    "note": "not_leader"}
    except Exception as e:
        # If locking isn't available, fall through and run (single-worker case).
        log.warning("scan_all: advisory lock unavailable (%s); running unguarded.", e)
        if lock_conn is not None:
            lock_conn.close()
            lock_conn = None

    try:
        return _scan_all_impl()
    finally:
        if lock_conn is not None:
            try:
                lock_conn.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": _LOCK_ID})
            except Exception:
                pass
            lock_conn.close()


def _scan_all_impl() -> dict:
    from data_providers import get_provider
    summary = {"scanned": 0, "triggered": 0, "skipped": 0, "events": []}
    try:
        customers = get_provider().list_customers()
    except Exception as e:
        log.warning("scan_all: could not list customers: %s", e)
        return summary

    for c in customers:
        cid = c["id"]
        summary["scanned"] += 1

        # Proactive engagement is consent-gated. If the customer has NOT granted
        # proactive_engagement consent, we do nothing for them — no signal
        # detection, no crew/LLM run, no nudge generation. The daily job only
        # ever works on customers who opted in.
        if not consent.has_active_consent(cid, consent.PURPOSE_ENGAGEMENT):
            summary["skipped"] += 1
            continue

        # one fetch of the last analysis per customer, reused for both
        # "new signals?" and "stale?" decisions.
        db = SessionLocal()
        try:
            last = _last_analysis(db, cid)
        finally:
            db.close()
        try:
            new_signals = detect_new_signals(cid, _last=last)
        except Exception as e:
            log.warning("scan_all: detect failed for %s: %s", cid, e)
            continue
        if not new_signals:
            continue

        for sig in new_signals:
            eid = record_event(cid, sig.get("event", "unknown"),
                               confidence=sig.get("confidence", 0.0), source="scheduler",
                               payload=sig)
            summary["events"].append({"customer_id": cid, "signal": sig.get("event"),
                                      "event_id": eid})

        # Re-run the crew (and generate fresh nudges) only if the last analysis
        # is stale — avoids re-billing the LLM for an analysis we already have.
        if _is_stale_from(last):
            try:
                process_customer(cid, trigger="scheduler")
                summary["triggered"] += 1
            except Exception as e:
                log.warning("scan_all: process failed for %s: %s", cid, e)
        else:
            summary["skipped"] += 1
    audit.record("engagement.scan", actor="scheduler", detail=summary)
    return summary


def ingest_event(customer_id: str, *, event_type: str = "transaction",
                 signal: str | None = None, payload: dict | None = None,
                 source: str = "webhook") -> dict:
    """Real-time entry point (webhook). Records the event and may trigger now."""
    payload = payload or {}

    # derive a signal from a raw transaction if not given
    if not signal and event_type == "transaction":
        amt = float(payload.get("amount", 0) or 0)
        cat = (payload.get("category") or "").lower()
        ttype = (payload.get("type") or "").lower()
        if cat == "salary" and ttype == "credit":
            signal = "salary_credit"
        elif amt >= 50000 and ttype == "debit":
            signal = "large_purchase"
        else:
            signal = "transaction"

    eid = record_event(customer_id, signal or event_type, event_type=event_type,
                       confidence=float(payload.get("confidence", 0.7)), source=source,
                       payload=payload)

    triggered = False
    if consent.has_active_consent(customer_id, consent.PURPOSE_ENGAGEMENT):
        # only spin up the crew for meaningful signals
        if signal in ("salary_credit", "large_purchase") or event_type == "life_event":
            try:
                process_customer(customer_id, trigger=source, event_id=eid)
                triggered = True
            except Exception as e:
                log.warning("ingest_event: process failed for %s: %s", customer_id, e)
                _mark_event(eid, "detected")
        else:
            _mark_event(eid, "detected")
    else:
        _mark_event(eid, "skipped")

    return {"event_id": eid, "signal": signal, "triggered": triggered}


def list_events(customer_id: str | None = None, limit: int = 50) -> list[dict]:
    db = SessionLocal()
    try:
        q = db.query(EngagementEvent)
        if customer_id:
            q = q.filter(EngagementEvent.customer_id == customer_id)
        rows = q.order_by(EngagementEvent.created_at.desc()).limit(limit).all()
        return [{
            "id": r.id, "customer_id": r.customer_id, "event_type": r.event_type,
            "signal": r.signal, "confidence": r.confidence, "source": r.source,
            "status": r.status, "payload": r.payload,
            "created_at": r.created_at.isoformat() + "Z" if r.created_at else None,
            "processed_at": r.processed_at.isoformat() + "Z" if r.processed_at else None,
        } for r in rows]
    finally:
        db.close()
