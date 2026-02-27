from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    value = (text or "").strip()
    if not value:
        return []
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap.")

    chunks: list[str] = []
    start = 0
    end = len(value)
    while start < end:
        stop = min(start + chunk_size, end)
        chunks.append(value[start:stop].strip())
        if stop >= end:
            break
        start = stop - overlap
    return [c for c in chunks if c]

