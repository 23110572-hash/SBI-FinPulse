"""Application settings loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central configuration for the FinPulse backend."""

    # --- LLM API keys ---
    gemini_api_key: str = ""
    # Three Groq keys split across the five crew agents to stay below the
    # per-key TPM rate limit. Slots 2/3 fall back to slot 1 if blank.
    groq_api_key: str = ""
    groq_api_key_2: str = ""
    groq_api_key_3: str = ""
    hf_token: str = ""

    # --- Model ids ---
    gemini_pro_model: str = "gemini-2.5-pro"
    gemini_flash_model: str = "gemini-2.5-flash"
    groq_model: str = "llama-3.3-70b-versatile"

    # Verbose CrewAI agent/crew logging to stdout. Off by default (keeps the
    # terminal clean); the live reasoning still streams to the UI via SSE.
    agent_verbose: bool = False

    # --- Embeddings (Hugging Face only) ---
    hf_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    hf_inference_provider: str = "hf-inference"

    # --- Storage ---
    # PostgreSQL (Neon) only — set DATABASE_URL in .env. No local SQLite.
    database_url: str = ""
    chroma_persist_dir: str = str(BASE_DIR / "chroma_db")

    # --- Chroma vector store ---
    # mode: "cloud" (Chroma Cloud) or "local" (persistent dir)
    chroma_mode: str = "cloud"
    chroma_api_key: str = ""
    chroma_tenant: str = ""
    chroma_database: str = "SBI"

    # --- CORS ---
    cors_origins: str = "http://localhost:3000"

    # =====================================================================
    # Data provider — where customer + transaction data actually comes from.
    # "synthetic"           : local seeded SQLite (default, demo)
    # "sbi_sandbox"         : SBI Innovation Hub / APIX sandbox APIs
    # "account_aggregator"  : RBI Account Aggregator (Sahamati / Setu / Finvu)
    # =====================================================================
    data_provider: str = "synthetic"

    # SBI Innovation Hub / APIX sandbox
    sbi_api_base: str = ""
    sbi_api_key: str = ""
    sbi_client_id: str = ""
    sbi_client_secret: str = ""

    # Account Aggregator (FIU side)
    aa_base_url: str = ""
    aa_client_id: str = ""
    aa_client_secret: str = ""
    aa_fiu_id: str = ""

    # =====================================================================
    # Nudge delivery channels (real senders, key-gated).
    # =====================================================================
    # Email is the only outbound channel we use. SMTP is required.
    # WhatsApp / SMS env values are kept for backwards compatibility but
    # are not used by the proactive engine.
    whatsapp_provider: str = "meta"
    meta_wa_token: str = ""
    meta_wa_phone_id: str = ""

    # Twilio (WhatsApp + SMS) — unused, kept so legacy config doesn't crash
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    twilio_sms_from: str = ""

    # Email (SMTP) — primary channel
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "FinPulse <noreply@finpulse.local>"

    # Auto-deliver compliance-approved nudges. Default ON: at SBI scale a
    # human approval queue is impractical — the compliance agent is the gate.
    auto_send_approved: bool = True

    # Channel that the engagement engine will use for proactive sends.
    proactive_channel: str = "email"

    # =====================================================================
    # Proactive engagement scheduler.
    # =====================================================================
    enable_scheduler: bool = True
    # Daily cron sweep time (24h clock, server timezone).
    scheduler_daily_hour: int = 22
    scheduler_daily_minute: int = 0
    # Optional fallback: legacy interval scan (kept for tests; usually unused).
    scheduler_interval_minutes: int = 0
    # Only re-run a customer if their last analysis is older than this.
    reanalyze_after_hours: int = 12
    # Hard cap: never send more than one email to the same customer in this
    # rolling window (hours). Default 24h ⇒ "max 1 nudge / customer / day".
    delivery_cooldown_hours: int = 24
    # Don't re-engage on the SAME target_gap within this many days.
    same_gap_cooldown_days: int = 30

    # =====================================================================
    # Auth — staff console + customer scoping.
    # =====================================================================
    # Bearer token required for staff/dashboard/nudge-management routes.
    staff_api_token: str = ""
    # If false, customer routes are open (demo). If true, a matching
    # X-Customer-Token header (or staff token) is required.
    enforce_customer_scope: bool = False

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key != "your_google_gemini_api_key")

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key and self.groq_api_key != "your_groq_api_key")

    def groq_key_for(self, slot: int) -> str:
        """Return the Groq API key for a numbered slot (1, 2 or 3).

        Slots 2 and 3 fall back to slot 1 when not configured, so a single
        key still works in development.
        """
        keys = {1: self.groq_api_key,
                2: self.groq_api_key_2 or self.groq_api_key,
                3: self.groq_api_key_3 or self.groq_api_key}
        return keys.get(slot, self.groq_api_key)

    @property
    def has_hf(self) -> bool:
        return bool(self.hf_token and self.hf_token.startswith("hf_"))

    @property
    def has_chroma_cloud(self) -> bool:
        return bool(self.chroma_api_key and self.chroma_tenant and self.chroma_database)

    @property
    def embeddings_ready(self) -> bool:
        return self.has_hf

    @property
    def llm_available(self) -> bool:
        return self.has_gemini or self.has_groq

    # --- data provider readiness ---
    @property
    def has_sbi_sandbox(self) -> bool:
        return bool(self.sbi_api_base and (self.sbi_api_key or self.sbi_client_id))

    @property
    def has_account_aggregator(self) -> bool:
        return bool(self.aa_base_url and self.aa_client_id and self.aa_fiu_id)

    # --- delivery readiness ---
    @property
    def has_meta_whatsapp(self) -> bool:
        return bool(self.meta_wa_token and self.meta_wa_phone_id)

    @property
    def has_twilio(self) -> bool:
        return bool(self.twilio_account_sid and self.twilio_auth_token)

    @property
    def has_smtp(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)

    def whatsapp_ready(self) -> bool:
        return self.has_meta_whatsapp if self.whatsapp_provider == "meta" else self.has_twilio

    def channel_ready(self, channel: str) -> bool:
        c = (channel or "").lower()
        if c in ("whatsapp", "wa"):
            return self.whatsapp_ready()
        if c in ("sms",):
            return self.has_twilio and bool(self.twilio_sms_from)
        if c in ("email", "app_notification", "app", "push"):
            return self.has_smtp
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
