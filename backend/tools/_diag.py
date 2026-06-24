"""Temp diagnostic: verify Rahul (CUST_001) nudges, message source, delivery."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import SessionLocal
from database.models import Analysis, Nudge, DeliveryReceipt
from agents.risk_tier import classify, label

CID = "CUST_001"
db = SessionLocal()

a = (db.query(Analysis).filter(Analysis.customer_id == CID)
     .order_by(Analysis.created_at.desc()).first())
w = (a.wellness or {}) if a else {}
print(f"\nSCORE: {w.get('overall_score')} ({w.get('grade')})  at {a.created_at if a else '—'}")

print("\n=== final_messages (Agent 5 output) ===")
for m in ((a.final_messages or []) if a else []):
    print(f"  prio={m.get('priority')} product={m.get('product')!r}")
    print(f"     msg={(m.get('message') or '')[:120]!r}")

print("\n=== NUDGES (pending only) ===")
for n in (db.query(Nudge).filter(Nudge.customer_id == CID, Nudge.status != "superseded")
          .order_by(Nudge.priority).all()):
    tier = classify(n.product_category)
    print(f"  {n.id} prio={n.priority} cat={n.product_category!r} tier={tier} ({label(n.product_category)})")
    print(f"     compliance={n.compliance_status}  status={n.status}  product={n.product_name!r}")
    print(f"     stored_msg={(n.message_draft or '')[:120]!r}")

print("\n=== DELIVERY RECEIPTS ===")
rs = (db.query(DeliveryReceipt).filter(DeliveryReceipt.customer_id == CID)
      .order_by(DeliveryReceipt.created_at.desc()).all())
if not rs:
    print("  NONE")
for r in rs:
    print(f"  {r.created_at}  {r.channel}/{r.provider}  status={r.status}  error={r.error}")
db.close()
