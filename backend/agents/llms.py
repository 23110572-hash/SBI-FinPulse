"""LLM factory helpers for CrewAI agents and the chat agent.

All factories require valid API keys. They raise a clear error if a key is
missing — there is no offline fallback.
"""
from __future__ import annotations

from functools import lru_cache

from config import settings


def _require(cond: bool, name: str) -> None:
    if not cond:
        raise RuntimeError(
            f"{name} is required but not configured. Add it to backend/.env and restart.")


def _patch_litellm_strip_cache_breakpoint() -> None:
    """Drop CrewAI's `cache_breakpoint` marker on the LiteLLM fallback path.

    CrewAI's *native* provider adapters strip this hint via
    BaseLLM._format_messages, but the LiteLLM path (used for `groq/...`,
    `cerebras/...`, etc.) forwards it verbatim. Strict OpenAI-compatible
    providers like Groq reject it with:
        property 'cache_breakpoint' is unsupported
    Patch once at import time so every Groq call is clean.
    """
    from crewai import LLM
    from crewai.llms.cache import CACHE_BREAKPOINT_KEY

    if getattr(LLM, "_finpulse_strip_cache_breakpoint", False):
        return

    original = LLM._format_messages_for_provider

    def _stripped(self, messages):
        cleaned = [
            {k: v for k, v in msg.items() if k != CACHE_BREAKPOINT_KEY}
            for msg in (messages or [])
        ]
        return original(self, cleaned)

    LLM._format_messages_for_provider = _stripped
    LLM._finpulse_strip_cache_breakpoint = True


def _patch_litellm_retry_transient() -> None:
    """Wrap LLM.call with a small retry loop for transient transport errors.

    Groq's edge occasionally drops sockets mid-request, surfacing as
    `WinError 10054` / `httpx.ConnectError` / `litellm.InternalServerError`.
    These are not real failures — a quick retry with backoff almost always
    succeeds and saves the entire 5-agent crew run from aborting.
    Rate-limit errors get a longer wait so we respect Groq's TPM ceiling.
    """
    import logging
    import time

    from crewai import LLM

    if getattr(LLM, "_finpulse_retry_wrapped", False):
        return

    log = logging.getLogger("finpulse.llm.retry")
    original_call = LLM.call

    # Best-effort imports — older LiteLLM releases may not expose every name.
    try:
        from litellm.exceptions import (  # type: ignore
            APIConnectionError, InternalServerError, RateLimitError,
            ServiceUnavailableError, Timeout,
        )
        TRANSIENT = (APIConnectionError, InternalServerError,
                     ServiceUnavailableError, Timeout)
        RATE_LIMITED = (RateLimitError,)
    except Exception:  # pragma: no cover — fall back to message-based detection
        TRANSIENT = ()
        RATE_LIMITED = ()

    TRANSIENT_HINTS = ("10054", "ConnectError", "remote host",
                       "Connection aborted", "Read timed out")

    def _is_transient(exc: Exception) -> bool:
        if TRANSIENT and isinstance(exc, TRANSIENT):
            return True
        msg = str(exc)
        return any(h in msg for h in TRANSIENT_HINTS)

    def _is_rate_limited(exc: Exception) -> bool:
        if RATE_LIMITED and isinstance(exc, RATE_LIMITED):
            return True
        return "rate limit" in str(exc).lower() or "RateLimit" in type(exc).__name__

    def _retrying_call(self, *args, **kwargs):
        max_attempts = 4
        backoff = 1.5  # seconds, multiplied by attempt number
        last_exc: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                return original_call(self, *args, **kwargs)
            except Exception as exc:  # noqa: BLE001 — surface anything non-transient
                last_exc = exc
                if attempt == max_attempts:
                    raise
                if _is_rate_limited(exc):
                    delay = max(backoff * attempt * 4, 6.0)  # respect TPM
                    log.warning("LLM rate-limited (attempt %s/%s); waiting %.1fs",
                                attempt, max_attempts, delay)
                    time.sleep(delay)
                    continue
                if _is_transient(exc):
                    delay = backoff * attempt
                    log.warning("LLM transient error (%s); retry %s/%s after %.1fs",
                                type(exc).__name__, attempt, max_attempts, delay)
                    time.sleep(delay)
                    continue
                raise  # not transient — fail fast
        if last_exc:  # pragma: no cover — unreachable, kept for type-narrow
            raise last_exc

    LLM.call = _retrying_call
    LLM._finpulse_retry_wrapped = True


_patch_litellm_strip_cache_breakpoint()
_patch_litellm_retry_transient()


def get_groq_llm(temperature: float = 0.3, slot: int = 1):
    """Fast analysis LLM as a CrewAI LLM.

    `slot` selects which Groq API key to use (1, 2 or 3). The five crew
    agents are spread across the three keys to stay under the 12K TPM
    per-key free-tier limit.
    """
    _require(settings.has_groq, "GROQ_API_KEY")
    api_key = settings.groq_key_for(slot)
    from crewai import LLM
    return LLM(model=f"groq/{settings.groq_model}", temperature=temperature,
               api_key=api_key)


def get_gemini_llm(model: str | None = None, temperature: float = 0.4):
    """Reasoning LLM (Gemini) as a CrewAI LLM."""
    _require(settings.has_gemini, "GEMINI_API_KEY")
    from crewai import LLM
    return LLM(model=f"gemini/{model or settings.gemini_pro_model}",
               temperature=temperature, api_key=settings.gemini_api_key)


def get_chat_llm():
    """LangChain chat model for the conversation agent. Uses Groq primarily.

    Memoised so the conversation agent reuses the same client (and underlying
    httpx pool) across messages instead of rebuilding it on every reply.
    """
    return _build_chat_llm()


@lru_cache(maxsize=1)
def _build_chat_llm():
    if settings.has_groq:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_key_for(3),
            temperature=0.6,
        )
    _require(settings.has_gemini, "GEMINI_API_KEY or GROQ_API_KEY")
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=settings.gemini_flash_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.6,
    )
