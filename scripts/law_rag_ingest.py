from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from law_rag.config import load_config
from law_rag.embeddings import HashEmbeddingProvider, OpenAIEmbeddingProvider
from law_rag.ingest import LawRagIngestor
from law_rag.law_api_client import LawApiClient
from law_rag.store_factory import build_store


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Korean law data into Supabase/Mongo for RAG.")
    parser.add_argument("--queries", nargs="+", required=True, help="Search queries for bootstrap ingestion.")
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--page-size", type=int, default=100)
    args = parser.parse_args()

    cfg = load_config()
    try:
        store = build_store(cfg)
        embedder = (
            OpenAIEmbeddingProvider(api_key=cfg.openai_api_key, model=cfg.embedding_model)
            if cfg.openai_api_key
            else HashEmbeddingProvider()
        )
        ingestor = LawRagIngestor(api=LawApiClient(cfg.law_api_oc), store=store, embedder=embedder)
        stats = ingestor.run(args.queries, max_pages=args.max_pages, page_size=args.page_size)
        print(
            json.dumps(
                {
                    "ok": True,
                    "store": cfg.store_backend,
                    "query_count": stats.query_count,
                    "fetched_count": stats.fetched_count,
                    "upserted_count": stats.upserted_count,
                    "chunk_count": stats.chunk_count,
                },
                ensure_ascii=False,
            )
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "store": cfg.store_backend, "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)


if __name__ == "__main__":
    main()
