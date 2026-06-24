"""Proactive engagement routes — events, scans, webhooks, audit trail."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Body, Depends

from api.security import require_staff
from services import audit as audit_svc
from services import engagement as eng

router = APIRouter(prefix="/api/engagement", tags=["engagement"])

# Bounded pool so a flood of inbound webhooks can't spawn N concurrent crew
# runs (each driving multiple LLM calls). Excess jobs queue here instead of
# overwhelming the Groq/Gemini rate-limit and DB pool.
_WEBHOOK_POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix="finpulse-webhook")


@router.get("/events")
def list_events(customer_id: str | None = None, limit: int = 50,
                _: str = Depends(require_staff)):
    return eng.list_events(customer_id=customer_id, limit=limit)


@router.get("/events/{customer_id}")
def customer_events(customer_id: str, limit: int = 50):
    return eng.list_events(customer_id=customer_id, limit=limit)


@router.post("/scan")
def run_scan(_: str = Depends(require_staff)):
    """Trigger a proactive sweep across all customers (runs synchronously)."""
    return eng.scan_all()


@router.post("/process/{customer_id}")
def process_customer(customer_id: str, body: dict = Body(default={}),
                     _: str = Depends(require_staff)):
    """Force-run the engagement pipeline for one customer."""
    auto_send = body.get("auto_send")
    return eng.process_customer(customer_id, trigger="manual", auto_send=auto_send)


@router.post("/webhook/transaction")
def transaction_webhook(body: dict = Body(...)):
    """Inbound real-time event (e.g. core banking pushes a new transaction).

    Records the event and, if the customer has active consent and the signal is
    material, triggers the engagement pipeline in the background.
    """
    customer_id = body.get("customer_id")
    if not customer_id:
        return {"error": "customer_id required"}
    payload = body.get("payload", {k: v for k, v in body.items() if k != "customer_id"})

    # Hand off heavy processing to the bounded pool. We return immediately;
    # the crew run completes asynchronously without blocking the request and
    # without spawning unbounded threads under load.
    _WEBHOOK_POOL.submit(
        eng.ingest_event, customer_id,
        event_type=body.get("event_type", "transaction"),
        signal=body.get("signal"), payload=payload, source="webhook",
    )
    return {"accepted": True, "customer_id": customer_id, "detail": "queued"}


@router.get("/audit")
def audit_log(customer_id: str | None = None, limit: int = 100,
              _: str = Depends(require_staff)):
    return audit_svc.list_logs(customer_id=customer_id, limit=limit)
