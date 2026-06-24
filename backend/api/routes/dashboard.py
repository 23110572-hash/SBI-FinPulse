"""Staff dashboard aggregate routes."""
from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from api.store import ACTIVITY
from database.connection import get_db
from database.models import Analysis, Customer, Nudge

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    # one round-trip per scalar count instead of pulling full tables.
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    analyzed = db.query(func.count(distinct(Analysis.customer_id))).scalar() or 0

    # bucketed nudge counts via SQL aggregation (no full-table scan).
    nudge_rows = (db.query(Nudge.status, func.count(Nudge.id))
                  .group_by(Nudge.status).all())
    nudges_total = sum(c for _, c in nudge_rows)
    sent = sum(c for s, c in nudge_rows if s == "sent")
    approved = sum(c for s, c in nudge_rows if s in ("approved", "sent"))

    # life events: only pull the JSON column we need, not whole rows.
    life_events = 0
    for (profile,) in db.query(Analysis.profile).all():
        life_events += len((profile or {}).get("life_events_detected", []))

    response_rate = round((sent / nudges_total * 100) if nudges_total else 0, 1)
    return {
        "customers_analyzed": analyzed,
        "total_customers": total_customers,
        "nudges_generated": nudges_total,
        "nudges_approved": approved,
        "response_rate": response_rate,
        "life_events_detected": life_events,
    }


@router.get("/activity")
def activity():
    return {"activity": ACTIVITY}


@router.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    # Group counts in SQL instead of pulling every Nudge row + Counter().
    by_category_rows = (db.query(Nudge.product_category, func.count(Nudge.id))
                        .group_by(Nudge.product_category).all())
    by_channel_rows = (db.query(Nudge.channel, func.count(Nudge.id))
                       .group_by(Nudge.channel).all())
    by_frame_rows = (db.query(Nudge.psychological_frame, func.count(Nudge.id))
                     .group_by(Nudge.psychological_frame).all())

    by_category = Counter()
    for cat, n in by_category_rows:
        by_category[cat or "other"] += n
    by_channel = Counter()
    for ch, n in by_channel_rows:
        by_channel[ch or "app_notification"] += n
    by_frame = Counter()
    for fr, n in by_frame_rows:
        by_frame[fr or "other"] += n

    # Life events + score buckets — pull only the two JSON columns we need.
    event_counter: Counter = Counter()
    score_buckets = {"0-39": 0, "40-54": 0, "55-69": 0, "70-84": 0, "85-100": 0}
    for profile, wellness in db.query(Analysis.profile, Analysis.wellness).all():
        for ev in (profile or {}).get("life_events_detected", []):
            event_counter[ev.get("event", "other")] += 1
        score = (wellness or {}).get("overall_score")
        if score is not None:
            if score < 40:
                score_buckets["0-39"] += 1
            elif score < 55:
                score_buckets["40-54"] += 1
            elif score < 70:
                score_buckets["55-69"] += 1
            elif score < 85:
                score_buckets["70-84"] += 1
            else:
                score_buckets["85-100"] += 1

    return {
        "nudges_by_category": [{"name": k, "value": v} for k, v in by_category.items()],
        "nudges_by_channel": [{"name": k, "value": v} for k, v in by_channel.items()],
        "nudges_by_frame": [{"name": k, "value": v} for k, v in by_frame.items()],
        "life_events": [{"name": k.replace("_", " ").title(), "value": v}
                        for k, v in event_counter.items()],
        "score_distribution": [{"range": k, "count": v} for k, v in score_buckets.items()],
    }
