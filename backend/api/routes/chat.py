"""Chat routes — conversation with FinPulse AI."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agents import generate_reply
from api.schemas.chat import ChatRequest, ChatResponse
from database.connection import get_db
from database.models import ChatLog, Customer

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == req.customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")

    history = [{"role": c.role, "content": c.content} for c in
               db.query(ChatLog).filter(ChatLog.customer_id == req.customer_id)
               .order_by(ChatLog.created_at).all()]

    result = generate_reply(req.message, customer_name=customer.name,
                            history=history, language=req.language)

    db.add(ChatLog(customer_id=req.customer_id, role="user",
                   content=req.message, language=req.language))
    db.add(ChatLog(customer_id=req.customer_id, role="assistant",
                   content=result["reply"], sources=result["sources"], language=req.language))
    db.commit()
    return result


@router.get("/history/{customer_id}")
def history(customer_id: str, db: Session = Depends(get_db)):
    rows = (db.query(ChatLog).filter(ChatLog.customer_id == customer_id)
            .order_by(ChatLog.created_at).all())
    return [{"role": r.role, "content": r.content, "sources": r.sources or [],
             "language": r.language,
             "created_at": r.created_at.isoformat() + "Z" if r.created_at else None}
            for r in rows]
