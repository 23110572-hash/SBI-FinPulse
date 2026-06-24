"""Consent routes — DPDP-aligned consent lifecycle for customers + staff."""
from __future__ import annotations

from fastapi import APIRouter, Body

from services import consent as consent_svc

router = APIRouter(prefix="/api/consent", tags=["consent"])


@router.get("/{customer_id}")
def get_consents(customer_id: str):
    """All consent records for a customer + whether engagement is currently allowed."""
    return {
        "customer_id": customer_id,
        "engagement_active": consent_svc.has_active_consent(
            customer_id, consent_svc.PURPOSE_ENGAGEMENT),
        "consents": consent_svc.list_for_customer(customer_id),
    }


@router.post("/{customer_id}/grant")
def grant_consent(customer_id: str, body: dict = Body(default={})):
    purpose = body.get("purpose", consent_svc.PURPOSE_ENGAGEMENT)
    return consent_svc.grant(
        customer_id,
        purpose=purpose,
        data_categories=body.get("data_categories"),
        channels=body.get("channels"),
        validity_days=int(body.get("validity_days", 365)),
        source=body.get("source", "customer_app"),
        aa_consent_handle=body.get("aa_consent_handle"),
        actor=body.get("actor", "customer"),
    )


@router.post("/{customer_id}/revoke")
def revoke_consent(customer_id: str, body: dict = Body(default={})):
    purpose = body.get("purpose", consent_svc.PURPOSE_ENGAGEMENT)
    revoked = consent_svc.revoke(customer_id, purpose=purpose,
                                 actor=body.get("actor", "customer"))
    return {"customer_id": customer_id, "purpose": purpose, "revoked": revoked}


@router.get("/{customer_id}/check")
def check_consent(customer_id: str, purpose: str = consent_svc.PURPOSE_ENGAGEMENT,
                  channel: str | None = None):
    return consent_svc.check(customer_id, purpose=purpose, channel=channel)
