from __future__ import annotations

from law_rag.config import LawRagConfig
from law_rag.mongo_store import MongoStore
from law_rag.supabase_store import SupabaseStore


def build_store(cfg: LawRagConfig):
    backend = (cfg.store_backend or "supabase").lower()
    if backend == "mongo":
        return MongoStore(
            db_name=cfg.mongo_db,
            raw_collection=cfg.raw_collection,
            chunk_collection=cfg.chunk_collection,
            log_collection=cfg.log_collection,
        )
    if backend == "supabase":
        return SupabaseStore(
            supabase_url=cfg.supabase_url,
            service_role_key=cfg.supabase_service_role_key,
            raw_table=cfg.raw_collection,
            chunk_table=cfg.chunk_collection,
            log_table=cfg.log_collection,
            schema=cfg.supabase_schema,
        )
    raise RuntimeError(f"Unsupported LAW_RAG_STORE: {cfg.store_backend}")
