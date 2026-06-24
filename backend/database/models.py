"""SQLAlchemy ORM models for FinPulse."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import (JSON, Column, DateTime, Float, ForeignKey, Index,
                        Integer, String, Text)
from sqlalchemy.orm import relationship

from .connection import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True)  # CUST_001
    name = Column(String, nullable=False)
    age = Column(Integer)
    location = Column(String)
    persona = Column(String)
    income_band = Column(String)
    monthly_income = Column(Integer, default=0)
    monthly_spending = Column(Integer, default=0)
    savings_rate = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    risk_appetite = Column(String)
    digital_activity = Column(String)
    products_held = Column(JSON, default=list)
    products_not_held = Column(JSON, default=list)
    # contact details (required for real nudge delivery)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    whatsapp_opt_in = Column(Integer, default=0)  # 0/1
    preferred_language = Column(String, default="en")

    transactions = relationship("Transaction", back_populates="customer")
    nudges = relationship("Nudge", back_populates="customer")
    chats = relationship("ChatLog", back_populates="customer")
    consents = relationship("Consent", back_populates="customer")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)  # TXN_000001
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    date = Column(String, index=True)
    type = Column(String)  # credit / debit
    amount = Column(Float)
    description = Column(String)
    category = Column(String, index=True)
    channel = Column(String)
    balance_after = Column(Float)

    customer = relationship("Customer", back_populates="transactions")


class Analysis(Base):
    """Stores the latest full crew analysis output per customer."""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    profile = Column(JSON)
    wellness = Column(JSON)
    nudge_plan = Column(JSON)
    compliance = Column(JSON)
    final_messages = Column(JSON)
    agent_logs = Column(JSON)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class Nudge(Base):
    __tablename__ = "nudges"

    id = Column(String, primary_key=True)  # NUDGE_xxx
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    priority = Column(Integer, default=1)
    target_gap = Column(String)
    product_name = Column(String)
    product_category = Column(String)
    psychological_frame = Column(String)
    message_draft = Column(Text)
    channel = Column(String)
    expected_conversion = Column(String)
    compliance_status = Column(String, default="pending")  # approved / pending / rejected / approved_with_modification
    compliance_notes = Column(JSON, default=dict)
    status = Column(String, default="pending")  # pending / sent / approved / rejected / failed
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    customer = relationship("Customer", back_populates="nudges")
    deliveries = relationship("DeliveryReceipt", back_populates="nudge")


class Consent(Base):
    """DPDP-aligned consent artefact.

    A consent is purpose-bound, scoped to data categories and channels, and has
    a validity window. Nothing proactive may fire without an active consent that
    covers the relevant purpose.
    """
    __tablename__ = "consents"

    id = Column(String, primary_key=True)  # CNS_xxx
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    purpose = Column(String, index=True)        # e.g. proactive_engagement, marketing, data_analysis
    data_categories = Column(JSON, default=list)  # ["transactions","profile","balance"]
    channels = Column(JSON, default=list)         # ["whatsapp","sms","email","app_notification"]
    status = Column(String, default="granted", index=True)  # granted / revoked / expired
    granted_at = Column(DateTime, default=dt.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    source = Column(String, default="customer_app")  # customer_app / account_aggregator / onboarding
    aa_consent_handle = Column(String, nullable=True)  # AA consent artefact id, if sourced via AA

    customer = relationship("Customer", back_populates="consents")

    # The active-consent lookup filters on (customer_id, purpose, status) on
    # every proactive run, delivery and consent check — index it as a unit.
    __table_args__ = (
        Index("ix_consent_active_lookup", "customer_id", "purpose", "status"),
    )


class AuditLog(Base):
    """Immutable-ish audit trail for every consequential action.

    Records who/what did what, to whom, and why — for compliance review.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, index=True, nullable=True)
    actor = Column(String, default="system")     # system / staff:<id> / agent:<name>
    action = Column(String, index=True)          # consent.grant, nudge.send, analysis.run, ...
    entity_type = Column(String, nullable=True)  # nudge / consent / analysis
    entity_id = Column(String, nullable=True)
    detail = Column(JSON, default=dict)
    created_at = Column(DateTime, default=dt.datetime.utcnow, index=True)


class EngagementEvent(Base):
    """A proactive trigger detected for a customer.

    Produced by the engagement engine (scheduled scan) or an inbound webhook
    (e.g. a new transaction). Drives the proactive pipeline.
    """
    __tablename__ = "engagement_events"

    id = Column(String, primary_key=True)  # EVT_xxx
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    event_type = Column(String, index=True)   # life_event / pattern_shift / transaction / inactivity
    signal = Column(String)                    # salary_hike, large_purchase, ...
    confidence = Column(Float, default=0.0)
    source = Column(String, default="scheduler")  # scheduler / webhook / manual
    payload = Column(JSON, default=dict)
    status = Column(String, default="detected", index=True)  # detected / processing / processed / skipped
    created_at = Column(DateTime, default=dt.datetime.utcnow, index=True)
    processed_at = Column(DateTime, nullable=True)


class DeliveryReceipt(Base):
    """Result of an actual send attempt for a nudge over a channel."""
    __tablename__ = "delivery_receipts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nudge_id = Column(String, ForeignKey("nudges.id"), index=True)
    customer_id = Column(String, index=True)
    channel = Column(String)
    provider = Column(String)               # meta / twilio / smtp
    status = Column(String)                 # sent / failed / not_configured / blocked_no_consent
    provider_message_id = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    nudge = relationship("Nudge", back_populates="deliveries")


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, ForeignKey("customers.id"), index=True)
    role = Column(String)  # user / assistant
    content = Column(Text)
    sources = Column(JSON, default=list)
    language = Column(String, default="en")
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    customer = relationship("Customer", back_populates="chats")
