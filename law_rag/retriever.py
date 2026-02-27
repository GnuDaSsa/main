from __future__ import annotations

from dataclasses import dataclass

from law_rag.embeddings import EmbeddingProvider, cosine_similarity
from law_rag.store import LawStore


@dataclass
class RetrievedChunk:
    doc_id: str
    law_name: str
    text: str
    source_url: str
    enforcement_date: str
    score: float


def _lexical_score(query: str, text: str) -> float:
    q_tokens = {x for x in query.lower().split() if x}
    t_tokens = {x for x in text.lower().split() if x}
    if not q_tokens or not t_tokens:
        return 0.0
    overlap = len(q_tokens.intersection(t_tokens))
    return overlap / max(1, len(q_tokens))


class LawRetriever:
    def __init__(self, store: LawStore, embedder: EmbeddingProvider):
        self.store = store
        self.embedder = embedder

    def search(self, query: str, top_k: int = 6, candidate_limit: int = 300) -> list[RetrievedChunk]:
        if not query.strip():
            return []

        vector = self.embedder.embed([query])[0]
        rows = self.store.list_chunks(limit=candidate_limit)

        scored: list[RetrievedChunk] = []
        for row in rows:
            text = str(row.get("text") or "")
            v = row.get("vector") or []
            semantic = cosine_similarity(vector, v)
            lexical = _lexical_score(query, text)
            final_score = 0.75 * semantic + 0.25 * lexical
            scored.append(
                RetrievedChunk(
                    doc_id=str(row.get("doc_id") or ""),
                    law_name=str(row.get("law_name") or ""),
                    text=text,
                    source_url=str(row.get("source_url") or ""),
                    enforcement_date=str(row.get("enforcement_date") or ""),
                    score=final_score,
                )
            )

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]

    @staticmethod
    def to_context(results: list[RetrievedChunk], max_chars: int = 6000) -> str:
        parts: list[str] = []
        for i, item in enumerate(results, start=1):
            parts.append(
                f"[{i}] law_name: {item.law_name}\n"
                f"doc_id: {item.doc_id}\n"
                f"enforcement_date: {item.enforcement_date}\n"
                f"source_url: {item.source_url}\n"
                f"text: {item.text}"
            )
        text = "\n\n".join(parts)
        return text[:max_chars]
