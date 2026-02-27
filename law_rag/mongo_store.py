from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING

from mongo_env import get_client


class MongoStore:
    def __init__(self, db_name: str, raw_collection: str, chunk_collection: str, log_collection: str):
        client = get_client()
        if client is None:
            raise RuntimeError("MongoDB connection is not available. Set MONGODB_URI first.")
        self.db = client[db_name]
        self.raw = self.db[raw_collection]
        self.chunks = self.db[chunk_collection]
        self.logs = self.db[log_collection]
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        self.raw.create_index([("doc_id", ASCENDING)], unique=True)
        self.raw.create_index([("updated_at", ASCENDING)])
        self.chunks.create_index([("doc_id", ASCENDING), ("chunk_index", ASCENDING)], unique=True)
        self.chunks.create_index([("updated_at", ASCENDING)])
        self.logs.create_index([("run_at", ASCENDING)])

    def upsert_raw_document(self, doc: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc)
        payload = {**doc, "updated_at": now}
        self.raw.update_one({"doc_id": doc["doc_id"]}, {"$set": payload, "$setOnInsert": {"created_at": now}}, upsert=True)

    def replace_chunks(self, doc_id: str, chunks: list[dict[str, Any]]) -> None:
        self.chunks.delete_many({"doc_id": doc_id})
        if not chunks:
            return
        now = datetime.now(timezone.utc)
        for item in chunks:
            item["updated_at"] = now
            item.setdefault("created_at", now)
        self.chunks.insert_many(chunks)

    def log_ingestion(self, payload: dict[str, Any]) -> None:
        entry = {**payload, "run_at": datetime.now(timezone.utc)}
        self.logs.insert_one(entry)

    def list_chunks(self, limit: int = 300) -> list[dict[str, Any]]:
        cursor = self.chunks.find(
            {},
            {"doc_id": 1, "law_name": 1, "text": 1, "vector": 1, "source_url": 1, "enforcement_date": 1},
        ).limit(limit)
        return list(cursor)
