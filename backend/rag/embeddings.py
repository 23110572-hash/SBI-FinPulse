"""RAG embeddings — Hugging Face Inference API only.

Model: sentence-transformers/all-MiniLM-L6-v2 (configurable via HF_EMBEDDING_MODEL).
Includes retry logic for transient connection errors and an in-process cache
so repeated identical queries (very common across the crew + chat) skip the
network round-trip entirely.
"""
from __future__ import annotations

import time
from collections import OrderedDict
from threading import Lock

from langchain_core.embeddings import Embeddings

from config import settings

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# small thread-safe LRU; queries (~50-200 tokens) are tiny so 512 entries
# cost <1 MB of RAM but eliminate all repeat embed calls.
_QUERY_CACHE_SIZE = 512
_query_cache: "OrderedDict[tuple[str, str], list[float]]" = OrderedDict()
_cache_lock = Lock()


def _cache_get(key: tuple[str, str]) -> list[float] | None:
    with _cache_lock:
        v = _query_cache.get(key)
        if v is not None:
            _query_cache.move_to_end(key)
        return v


def _cache_put(key: tuple[str, str], value: list[float]) -> None:
    with _cache_lock:
        _query_cache[key] = value
        _query_cache.move_to_end(key)
        while len(_query_cache) > _QUERY_CACHE_SIZE:
            _query_cache.popitem(last=False)


class HuggingFaceInferenceEmbeddings(Embeddings):
    """LangChain Embeddings backed by huggingface_hub InferenceClient."""

    def __init__(self, model: str | None = None, token: str | None = None,
                 provider: str | None = None):
        from huggingface_hub import InferenceClient
        self.model = model or settings.hf_embedding_model
        self._client = InferenceClient(
            provider=provider or settings.hf_inference_provider,
            api_key=token or settings.hf_token,
        )

    def _embed_one(self, text: str) -> list[float]:
        import numpy as np
        for attempt in range(MAX_RETRIES):
            try:
                result = self._client.feature_extraction(text, model=self.model)
                arr = np.array(result, dtype="float32")
                if arr.ndim == 2:
                    arr = arr.mean(axis=0)
                elif arr.ndim > 2:
                    arr = arr.reshape(-1, arr.shape[-1]).mean(axis=0)
                return arr.astype("float32").tolist()
            except Exception as e:
                if attempt < MAX_RETRIES - 1 and ("ConnectError" in type(e).__name__ or "10054" in str(e)):
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                raise

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # ingest path; cache here too in case the same chunk is re-ingested.
        out: list[list[float]] = []
        for t in texts:
            key = (self.model, t)
            cached = _cache_get(key)
            if cached is not None:
                out.append(cached)
                continue
            v = self._embed_one(t)
            _cache_put(key, v)
            out.append(v)
        return out

    def embed_query(self, text: str) -> list[float]:
        key = (self.model, text)
        cached = _cache_get(key)
        if cached is not None:
            return cached
        v = self._embed_one(text)
        _cache_put(key, v)
        return v


def get_embeddings() -> Embeddings:
    """Return the HuggingFace embeddings provider."""
    if not settings.has_hf:
        raise RuntimeError("HF_TOKEN is required for embeddings. Set it in backend/.env")
    return HuggingFaceInferenceEmbeddings()
