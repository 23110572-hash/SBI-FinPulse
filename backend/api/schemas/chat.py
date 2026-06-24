"""Chat schemas."""
from __future__ import annotations

from pydantic import BaseModel


class ChatRequest(BaseModel):
    customer_id: str
    message: str
    language: str = "en"


class ChatSource(BaseModel):
    title: str
    snippet: str
    source_file: str | None = None


class ChatResponse(BaseModel):
    reply: str
    sources: list[ChatSource] = []
    quick_replies: list[str] = []


class ChatMessageOut(BaseModel):
    role: str
    content: str
    sources: list = []
    language: str = "en"
    created_at: str | None = None
