from __future__ import annotations

from typing import Any, Protocol


class LawStore(Protocol):
    def upsert_raw_document(self, doc: dict[str, Any]) -> None:
        ...

    def replace_chunks(self, doc_id: str, chunks: list[dict[str, Any]]) -> None:
        ...

    def log_ingestion(self, payload: dict[str, Any]) -> None:
        ...

    def list_chunks(self, limit: int = 300) -> list[dict[str, Any]]:
        ...
