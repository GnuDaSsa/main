from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import requests


class SupabaseStore:
    def __init__(
        self,
        supabase_url: str,
        service_role_key: str,
        raw_table: str,
        chunk_table: str,
        log_table: str,
        schema: str = "public",
        timeout: int = 30,
    ):
        if not supabase_url:
            raise RuntimeError("SUPABASE_URL is required.")
        if not service_role_key:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is required.")
        self.base = supabase_url.rstrip("/") + "/rest/v1"
        self.timeout = timeout
        self.raw_table = raw_table
        self.chunk_table = chunk_table
        self.log_table = log_table
        self.headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Profile": schema,
            "Content-Profile": schema,
        }

    def _endpoint(self, table: str) -> str:
        return f"{self.base}/{table}"

    def _request(
        self,
        method: str,
        table: str,
        *,
        params: dict[str, Any] | None = None,
        payload: Any | None = None,
        prefer: str | None = None,
    ) -> requests.Response:
        headers = dict(self.headers)
        if prefer:
            headers["Prefer"] = prefer
        response = requests.request(
            method,
            self._endpoint(table),
            params=params,
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response

    def upsert_raw_document(self, doc: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        payload = [{**doc, "updated_at": now, "created_at": now}]
        self._request(
            "POST",
            self.raw_table,
            params={"on_conflict": "doc_id"},
            payload=payload,
            prefer="resolution=merge-duplicates,return=minimal",
        )

    def replace_chunks(self, doc_id: str, chunks: list[dict[str, Any]]) -> None:
        self._request("DELETE", self.chunk_table, params={"doc_id": f"eq.{doc_id}"}, prefer="return=minimal")
        if not chunks:
            return
        now = datetime.now(timezone.utc).isoformat()
        payload: list[dict[str, Any]] = []
        for row in chunks:
            vector = row.get("vector") or []
            vector_text = "[" + ",".join(str(float(x)) for x in vector) + "]"
            payload.append({**row, "vector": vector_text, "updated_at": now, "created_at": now})
        self._request("POST", self.chunk_table, payload=payload, prefer="return=minimal")

    def log_ingestion(self, payload: dict[str, Any]) -> None:
        row = [{**payload, "run_at": datetime.now(timezone.utc).isoformat()}]
        self._request("POST", self.log_table, payload=row, prefer="return=minimal")

    def list_chunks(self, limit: int = 300) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            self.chunk_table,
            params={
                "select": "doc_id,law_name,text,vector,source_url,enforcement_date",
                "limit": str(limit),
            },
        )
        items = response.json() or []
        rows: list[dict[str, Any]] = []
        for item in items:
            rows.append(
                {
                    "doc_id": item.get("doc_id", ""),
                    "law_name": item.get("law_name", ""),
                    "text": item.get("text", ""),
                    "source_url": item.get("source_url", ""),
                    "enforcement_date": item.get("enforcement_date", ""),
                    "vector": _parse_vector(item.get("vector")),
                }
            )
        return rows


def _parse_vector(value: Any) -> list[float]:
    if isinstance(value, list):
        return [float(x) for x in value]
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("[") and text.endswith("]"):
            try:
                return [float(x) for x in json.loads(text)]
            except Exception:
                return []
    return []
