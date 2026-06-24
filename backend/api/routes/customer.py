"""Customer routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas.customer import CustomerDetail, CustomerSummary, TransactionOut
from database.connection import get_db
from database.models import Customer, Transaction

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=list[CustomerSummary])
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(404, "Customer not found")
    return c


@router.get("/{customer_id}/transactions", response_model=list[TransactionOut])
def get_transactions(customer_id: str, limit: int = 200, db: Session = Depends(get_db)):
    return (db.query(Transaction)
            .filter(Transaction.customer_id == customer_id)
            .order_by(Transaction.date.desc())
            .limit(limit).all())
