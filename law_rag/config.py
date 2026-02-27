from __future__ import annotations

from dataclasses import dataclass

from mongo_env import get_setting


@dataclass(frozen=True)
class LawRagConfig:
    law_api_oc: str
    openai_api_key: str
    store_backend: str
    mongo_db: str
    raw_collection: str
    chunk_collection: str
    log_collection: str
    supabase_url: str
    supabase_service_role_key: str
    supabase_schema: str
    embedding_model: str
    answer_model: str
    top_k: int


def load_config() -> LawRagConfig:
    return LawRagConfig(
        law_api_oc=(get_setting("LAW_API_OC") or "").strip(),
        openai_api_key=(get_setting("OPENAI_API_KEY") or "").strip(),
        store_backend=(get_setting("LAW_RAG_STORE", "mongo") or "mongo").strip().lower(),
        mongo_db=(get_setting("LAW_RAG_MONGODB_DB", "dlc") or "dlc").strip(),
        raw_collection=(get_setting("LAW_RAG_RAW_COLLECTION", "law_raw_documents") or "law_raw_documents").strip(),
        chunk_collection=(get_setting("LAW_RAG_CHUNK_COLLECTION", "law_chunks") or "law_chunks").strip(),
        log_collection=(get_setting("LAW_RAG_LOG_COLLECTION", "law_ingestion_logs") or "law_ingestion_logs").strip(),
        supabase_url=(get_setting("SUPABASE_URL") or "").strip(),
        supabase_service_role_key=(get_setting("SUPABASE_SERVICE_ROLE_KEY") or "").strip(),
        supabase_schema=(get_setting("LAW_RAG_SUPABASE_SCHEMA", "public") or "public").strip(),
        embedding_model=(get_setting("LAW_RAG_EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small").strip(),
        answer_model=(get_setting("LAW_RAG_ANSWER_MODEL", "gpt-4o-mini") or "gpt-4o-mini").strip(),
        top_k=int(get_setting("LAW_RAG_TOP_K", "6") or "6"),
    )
