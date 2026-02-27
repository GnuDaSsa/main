from __future__ import annotations

from typing import Any

import requests

LAW_API_BASE = "https://www.law.go.kr/DRF/lawSearch.do"


def _to_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    return []


def _pick(d: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = d.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


class LawApiClient:
    def __init__(self, oc: str, timeout: int = 20):
        if not oc:
            raise ValueError("LAW_API_OC is required.")
        self.oc = oc
        self.timeout = timeout

    def search_laws(self, query: str, page: int = 1, display: int = 100) -> list[dict[str, Any]]:
        params = {
            "OC": self.oc,
            "target": "law",
            "type": "JSON",
            "query": query,
            "display": display,
            "page": page,
        }
        response = requests.get(LAW_API_BASE, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return _to_list(data.get("LawSearch", {}).get("law"))

    @staticmethod
    def normalize(raw_item: dict[str, Any]) -> dict[str, Any]:
        doc_id = _pick(raw_item, "법령ID", "법령일련번호", "MST", "ID")
        law_name = _pick(raw_item, "법령명한글", "법령명", "법령명한자")
        promulgation_no = _pick(raw_item, "공포번호")
        enforcement_date = _pick(raw_item, "시행일자")
        amendment_date = _pick(raw_item, "공포일자", "개정일자")
        law_class = _pick(raw_item, "법종구분", "법령구분명")

        # Many search responses do not include full article body.
        # Keep all source fields and build best-effort text for retrieval.
        searchable_text_parts = [law_name, _pick(raw_item, "제개정구분명"), _pick(raw_item, "소관부처명"), _pick(raw_item, "법령상세링크")]
        searchable_text = " ".join([x for x in searchable_text_parts if x]).strip()

        return {
            "doc_id": doc_id or law_name,
            "law_name": law_name,
            "promulgation_no": promulgation_no,
            "enforcement_date": enforcement_date,
            "amendment_date": amendment_date,
            "law_class": law_class,
            "source_url": _pick(raw_item, "법령상세링크"),
            "text": searchable_text,
            "raw": raw_item,
        }

