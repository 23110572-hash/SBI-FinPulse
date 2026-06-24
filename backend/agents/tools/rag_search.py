"""RAG search tool over the SBI knowledge base."""
from __future__ import annotations

from rag.pipeline import search_kb


def search_products(query: str, k: int = 5) -> list[dict]:
    return search_kb(query, k)


def get_crewai_tool():
    try:
        from crewai.tools import BaseTool
    except Exception:
        return None

    class RAGSearchTool(BaseTool):
        name: str = "SBI Knowledge Search"
        description: str = (
            "Search SBI product catalogue, RBI guidelines and DPDP rules. "
            "Input: a natural-language query. Returns the most relevant knowledge snippets."
        )

        def _run(self, query: str) -> str:
            import json
            return json.dumps(search_kb(query, k=5))

    return RAGSearchTool()
