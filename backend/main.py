"""SBI FinPulse — FastAPI application entry point."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import (analysis, chat, consent, customer, dashboard,
                        engagement, insights, nudges)
from config import settings
from data_providers import active_provider_name
from database.connection import init_db
from services.scheduler import start_scheduler, stop_scheduler


def _configure_logging() -> None:
    """Keep the terminal clean — quiet chatty third-party libraries."""
    logging.basicConfig(level=logging.WARNING)
    for noisy in ("httpx", "httpcore", "LiteLLM", "litellm", "chromadb",
                  "apscheduler", "urllib3", "openai", "sentence_transformers"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    # our own app logs stay at INFO
    logging.getLogger("finpulse").setLevel(logging.INFO)


_configure_logging()

app = FastAPI(
    title="SBI FinPulse API",
    description="Agentic AI-powered digital engagement platform for SBI.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


@app.get("/")
def root():
    return {
        "service": "SBI FinPulse API",
        "status": "online",
        "gemini_configured": settings.has_gemini,
        "groq_configured": settings.has_groq,
        "data_provider": active_provider_name(),
        "scheduler_enabled": settings.enable_scheduler,
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    """Operational readiness of the data + delivery + proactive subsystems."""
    from data_providers import get_provider
    return {
        "data_provider": get_provider().health(),
        "channels": {
            "whatsapp": settings.whatsapp_ready(),
            "sms": settings.has_twilio and bool(settings.twilio_sms_from),
            "email": settings.has_smtp,
        },
        "scheduler_enabled": settings.enable_scheduler,
        "auto_send_approved": settings.auto_send_approved,
        "enforce_customer_scope": settings.enforce_customer_scope,
    }


app.include_router(customer.router)
app.include_router(analysis.router)
app.include_router(chat.router)
app.include_router(insights.router)
app.include_router(nudges.router)
app.include_router(dashboard.router)
app.include_router(consent.router)
app.include_router(engagement.router)
