"""Conversation Agent — empathetic financial companion (Gemini 2.5 Flash).

Live LLM only. Uses RAG context from ChromaDB + a windowed message history.
"""
from __future__ import annotations

from agents.llms import get_chat_llm
from rag.pipeline import answer_with_context

SYSTEM_PROMPT = """You are FinPulse AI, a warm, knowledgeable financial companion for SBI customers.

Style rules:
- Friendly, conversational, never pushy. Respect a "no" gracefully.
- Keep replies under 100 words. Use bullets for lists. 1-2 emojis max.
- Use the customer's first name when known.
- Always use REAL SBI product names and details from the provided CONTEXT.
- Never invent rates; if the context does not have a number, say you'll confirm it.
- Explain jargon simply.
- If the user writes in Hindi, reply in Hindi.
- End with a short question or call to action.
"""

QUICK_REPLIES = ["Tell me more", "Not interested", "Start SIP", "Compare options"]


def generate_reply(message: str, customer_name: str | None = None,
                   history: list[dict] | None = None, language: str = "en") -> dict:
    """Return {reply, sources, quick_replies} using the live LLM + RAG."""
    context, sources = answer_with_context(message, k=4)
    source_payload = [{"title": s["title"], "snippet": s["snippet"][:240],
                       "source_file": s.get("source_file")} for s in sources]

    llm = get_chat_llm()
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    msgs = [SystemMessage(content=SYSTEM_PROMPT)]
    if customer_name:
        msgs.append(SystemMessage(content=f"The customer's name is {customer_name}."))
    for h in (history or [])[-20:]:
        if h["role"] == "user":
            msgs.append(HumanMessage(content=h["content"]))
        else:
            msgs.append(AIMessage(content=h["content"]))
    lang_note = " Reply in Hindi (Devanagari)." if language == "hi" else ""
    msgs.append(HumanMessage(
        content=f"CONTEXT (SBI knowledge base):\n{context}\n\nCUSTOMER MESSAGE: {message}{lang_note}"))

    resp = llm.invoke(msgs)
    reply = resp.content if hasattr(resp, "content") else str(resp)
    return {"reply": reply, "sources": source_payload, "quick_replies": QUICK_REPLIES}
