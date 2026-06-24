"""Persistence helpers: save crew analysis + nudges, in-memory activity feed."""
from __future__ import annotations

import datetime as dt
import uuid

from agents.tools.compliance_checker import check_compliance, disclosure_for
from agents.risk_tier import infer_product_category
from database.connection import SessionLocal
from database.models import Analysis, Customer, Nudge

# in-memory recent activity feed for the staff dashboard
ACTIVITY: list[dict] = []
MAX_ACTIVITY = 50


def push_activity(entry: dict) -> None:
    entry.setdefault("time", dt.datetime.utcnow().isoformat() + "Z")
    ACTIVITY.insert(0, entry)
    del ACTIVITY[MAX_ACTIVITY:]


def save_analysis(result: dict) -> None:
    """Persist the full analysis and its nudges to the database."""
    db = SessionLocal()
    try:
        cid = result["customer_id"]
        db.add(Analysis(
            customer_id=cid,
            profile=result.get("profile"),
            wellness=result.get("wellness"),
            nudge_plan=result.get("nudge_plan"),
            compliance=result.get("compliance"),
            final_messages=result.get("final_messages"),
            agent_logs=result.get("agent_logs"),
        ))

        # Don't destroy history. Prior PENDING nudges are marked "superseded"
        # so they drop out of the review queue, while already sent/approved/
        # rejected nudges (and their delivery receipts) stay intact as an
        # immutable audit trail. Hard-deleting would also violate the
        # delivery_receipts foreign key and crash a re-analysis.
        (db.query(Nudge)
         .filter(Nudge.customer_id == cid, Nudge.status == "pending")
         .update({Nudge.status: "superseded"}, synchronize_session=False))

        compliance_by_priority = {
            c.get("nudge_priority"): c
            for c in result.get("compliance", {}).get("compliance_results", [])
        }
        # Agent 5 (Conversation) writes the warm, customer-ready message per
        # priority. That — not the strategist's rough draft — is what we deliver.
        final_by_priority = {
            m.get("priority"): m
            for m in (result.get("final_messages") or [])
            if isinstance(m, dict) and m.get("priority") is not None
        }
        customer = db.query(Customer).filter(Customer.id == cid).first()
        cust_name = customer.name if customer else cid

        for n in result.get("nudge_plan", {}).get("nudges", []):
            llm_review = compliance_by_priority.get(n.get("priority"), {})
            product = n.get("product_recommended", {}) or {}
            # The strategist LLM is inconsistent with product keys — read every
            # variant so name/category are never silently dropped (a missing
            # category made every nudge default to Tier 2 and show no product).
            prod_name = (product.get("name") or product.get("product_name")
                         or product.get("product") or product.get("title"))
            prod_cat = (product.get("category") or product.get("product_type")
                        or product.get("type") or "")
            # If the LLM gave no category, infer it from the product name so
            # tier routing + disclosures still work (otherwise everything
            # silently defaults to Tier 2 and a low-risk FD never auto-sends).
            if not prod_cat:
                prod_cat = infer_product_category(prod_name or "")
            nudge_id = f"NUDGE_{uuid.uuid4().hex[:8].upper()}"

            # Deterministic, consent-aware compliance is authoritative over the
            # LLM's narrative result. We KEEP the compliance agent's reasoning
            # under `agent_review` so the staff console can show why the AI
            # reasoned the way it did, while the deterministic verdict governs.
            # Pass the RESOLVED category so disclosure checks see it too.
            n_for_check = {**n, "customer_id": cid,
                           "product_recommended": {**product, "category": prod_cat}}
            det = check_compliance(n_for_check, customer_id=cid)
            comp = {**det, "agent_review": llm_review}
            comp_status = det.get("status", "pending")

            # The DELIVERABLE message is Agent 5's polished, customer-ready text
            # (falling back to the strategist draft only if the agent produced
            # none, e.g. it skipped a nudge it judged non-compliant).
            final_msg = final_by_priority.get(n.get("priority"), {})
            msg = (final_msg.get("message") or n.get("message_draft") or "").strip()

            # Append the mandatory disclosure to the OUTGOING message if it's
            # missing, so the email a customer receives is always compliant.
            disc = disclosure_for(prod_cat)
            if disc and not any(tok in msg.lower()
                                for tok in ("risk", "solicitation", "free-look", "subject to")):
                msg = f"{msg}\n\n{disc}"

            db.add(Nudge(
                id=nudge_id,
                customer_id=cid,
                priority=n.get("priority", 1),
                target_gap=n.get("target_gap"),
                product_name=prod_name,
                product_category=prod_cat,
                psychological_frame=n.get("psychological_frame"),
                message_draft=msg,
                channel=n.get("channel"),
                expected_conversion=n.get("expected_conversion"),
                compliance_status=comp_status,
                compliance_notes=comp,
                status="pending",
            ))
            push_activity({
                "customer_id": cid, "customer_name": cust_name,
                "event": ", ".join(e.get("event", "") for e in
                                   result.get("profile", {}).get("life_events_detected", [])) or "analysis",
                "product": prod_name or "-",
                "status": comp_status,
            })
        db.commit()
    finally:
        db.close()


def latest_analysis(customer_id: str) -> dict | None:
    db = SessionLocal()
    try:
        a = (db.query(Analysis).filter(Analysis.customer_id == customer_id)
             .order_by(Analysis.created_at.desc()).first())
        if not a:
            return None
        return {
            "customer_id": a.customer_id,
            "profile": a.profile,
            "wellness": a.wellness,
            "nudge_plan": a.nudge_plan,
            "compliance": a.compliance,
            "final_messages": a.final_messages,
            "agent_logs": a.agent_logs,
            "created_at": a.created_at.isoformat() + "Z" if a.created_at else None,
        }
    finally:
        db.close()
