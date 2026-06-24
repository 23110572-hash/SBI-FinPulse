
from __future__ import annotations

import time
from functools import lru_cache
from pathlib import Path
from threading import Lock

from config import settings

KB_DIR = Path(__file__).resolve().parent / "knowledge_base"
COLLECTION = "sbi_finpulse_kb"

# TTL cache for search_kb. Same query repeats many times across the crew
# (compliance + nudge agents both call SBI Knowledge Search) and across chat
# turns. 10-minute TTL keeps results reasonably fresh while removing 90%+
# of duplicate Chroma round-trips.
_SEARCH_CACHE_TTL = 600  # seconds
_SEARCH_CACHE_MAX = 256
_search_cache: dict[tuple[str, int], tuple[float, list[dict]]] = {}
_search_lock = Lock()


# ----------------------------- document loading -----------------------------
def load_documents() -> list[dict]:
    """Load all markdown files as {text, source_file, category, title} dicts."""
    docs = []
    if not KB_DIR.exists():
        return docs
    for path in KB_DIR.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        docs.append({
            "text": text,
            "source_file": str(path.relative_to(KB_DIR)),
            "category": path.parent.name,
            "title": path.stem.replace("_", " ").title(),
        })
    return docs


# ----------------------------- vector store --------------------------------
@lru_cache
def get_embeddings():
    from rag.embeddings import get_embeddings as _get
    return _get()


@lru_cache
def get_chroma_client():
    """Return a Chroma Cloud client when configured, else None (local mode)."""
    if settings.chroma_mode == "cloud" and settings.has_chroma_cloud:
        import chromadb
        return chromadb.CloudClient(
            api_key=settings.chroma_api_key,
            tenant=settings.chroma_tenant,
            database=settings.chroma_database,
        )
    return None


@lru_cache
def get_vectorstore():
    """Return the Chroma vector store (cloud or local persistent)."""
    from langchain_chroma import Chroma
    client = get_chroma_client()
    if client is not None:
        return Chroma(
            collection_name=COLLECTION,
            embedding_function=get_embeddings(),
            client=client,
        )
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


# ----------------------------- public API -----------------------------------
def search_kb(query: str, k: int = 5) -> list[dict]:
    """MMR vector search over the SBI knowledge base (TTL-cached)."""
    key = (query, k)
    now = time.time()
    with _search_lock:
        hit = _search_cache.get(key)
        if hit and now - hit[0] < _SEARCH_CACHE_TTL:
            return hit[1]

    store = get_vectorstore()
    results = store.max_marginal_relevance_search(query, k=k, fetch_k=20, lambda_mult=0.7)
    out = []
    for r in results:
        meta = r.metadata or {}
        out.append({
            "title": meta.get("title", meta.get("source_file", "SBI Knowledge")),
            "snippet": r.page_content.strip(),
            "source_file": meta.get("source_file"),
            "category": meta.get("category"),
        })

    with _search_lock:
        _search_cache[key] = (now, out)
        # bounded LRU-by-insertion: drop oldest entries if oversize
        if len(_search_cache) > _SEARCH_CACHE_MAX:
            for stale_key in list(_search_cache.keys())[:len(_search_cache) - _SEARCH_CACHE_MAX]:
                _search_cache.pop(stale_key, None)
    return out


def answer_with_context(question: str, k: int = 5) -> tuple[str, list[dict]]:
    """Return (context_text, sources) for a question."""
    sources = search_kb(question, k)
    context = "\n\n".join(f"[{s['title']}]\n{s['snippet']}" for s in sources)
    return context, sources
