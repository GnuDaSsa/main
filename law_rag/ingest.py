from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from law_rag.chunking import chunk_text
from law_rag.embeddings import EmbeddingProvider
from law_rag.law_api_client import LawApiClient
from law_rag.store import LawStore


@dataclass
class IngestStats:
    query_count: int = 0
    fetched_count: int = 0
    upserted_count: int = 0
    chunk_count: int = 0


class LawRagIngestor:
    def __init__(self, api: LawApiClient, store: LawStore, embedder: EmbeddingProvider):
        self.api = api
        self.store = store
        self.embedder = embedder

    def run(self, queries: list[str], max_pages: int = 1, page_size: int = 100) -> IngestStats:
        stats = IngestStats(query_count=len(queries))
        seen_doc_ids: set[str] = set()

        for query in queries:
            for page in range(1, max_pages + 1):
                laws = self.api.search_laws(query=query, page=page, display=page_size)
                if not laws:
                    break
                stats.fetched_count += len(laws)
                normalized = [self.api.normalize(x) for x in laws]
                unique_docs = [d for d in normalized if d["doc_id"] and d["doc_id"] not in seen_doc_ids]
                for doc in unique_docs:
                    seen_doc_ids.add(doc["doc_id"])
                    self.store.upsert_raw_document(doc)
                    chunks = chunk_text(doc.get("text", ""))
                    embeddings = self.embedder.embed(chunks) if chunks else []
                    payload = []
                    for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                        payload.append({
                            "doc_id": doc["doc_id"],
                            "law_name": doc.get("law_name", ""),
                            "chunk_index": idx,
                            "text": chunk,
                            "vector": vector,
                            "source_url": doc.get("source_url", ""),
                            "enforcement_date": doc.get("enforcement_date", ""),
                        })
                    self.store.replace_chunks(doc["doc_id"], payload)
                    stats.upserted_count += 1
                    stats.chunk_count += len(payload)

        self.store.log_ingestion({
            "type": "bootstrap_or_incremental",
            "queries": queries,
            "max_pages": max_pages,
            "page_size": page_size,
            "query_count": stats.query_count,
            "fetched_count": stats.fetched_count,
            "upserted_count": stats.upserted_count,
            "chunk_count": stats.chunk_count,
            "finished_at": datetime.now(timezone.utc),
        })
        return stats
