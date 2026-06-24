
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings  # noqa: E402
from rag.pipeline import COLLECTION, get_chroma_client, get_embeddings, load_documents  # noqa: E402


def ingest() -> None:
    if not settings.embeddings_ready:
        raise RuntimeError(
            f"Embedding provider '{settings.embedding_provider}' is not configured. "
            "Set HF_TOKEN (huggingface)" )

    start = time.time()
    docs = load_documents()
    print(f"Loaded {len(docs)} knowledge base documents.")

    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " "],
    )

    lc_docs: list[Document] = []
    for d in docs:
        for chunk in splitter.split_text(d["text"]):
            lc_docs.append(Document(
                page_content=chunk,
                metadata={"source_file": d["source_file"], "category": d["category"],
                          "title": d["title"], "last_updated": "2026-06"},
            ))

    model_name = settings.hf_embedding_model
    print(f"Created {len(lc_docs)} chunks. Embedding with HuggingFace ({model_name}) ...")

    embeddings = get_embeddings()
    client = get_chroma_client()

    if client is not None:
        print(f"Target: Chroma Cloud (database='{settings.chroma_database}', collection='{COLLECTION}')")
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass
        Chroma.from_documents(
            lc_docs, embedding=embeddings, collection_name=COLLECTION, client=client)
        target = f"Chroma Cloud / {settings.chroma_database}"
    else:
        print(f"Target: local ChromaDB at {settings.chroma_persist_dir}")
        store = Chroma(collection_name=COLLECTION, embedding_function=embeddings,
                       persist_directory=settings.chroma_persist_dir)
        try:
            store.delete_collection()
        except Exception:
            pass
        Chroma.from_documents(
            lc_docs, embedding=embeddings, collection_name=COLLECTION,
            persist_directory=settings.chroma_persist_dir)
        target = settings.chroma_persist_dir

    print(f"Ingested {len(lc_docs)} chunks into {target}")
    print(f"Done in {time.time() - start:.1f}s")


if __name__ == "__main__":
    ingest()
