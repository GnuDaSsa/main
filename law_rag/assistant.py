from __future__ import annotations

from openai import OpenAI

from law_rag.retriever import RetrievedChunk


def build_prompt(question: str, context: str) -> list[dict[str, str]]:
    system = (
        "You are a legal information assistant for Korean law. "
        "Answer only from the provided context. "
        "If context is insufficient, say what is missing. "
        "Always include citations by item number like [1], [2]. "
        "End with a short disclaimer that this is not legal advice."
    )
    user = (
        f"Question:\n{question}\n\n"
        f"Context:\n{context}\n\n"
        "Return concise Korean answer with: 요약, 근거, 참고출처."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def generate_answer(api_key: str, model: str, question: str, context: str) -> str:
    if not api_key:
        return "OPENAI_API_KEY가 없어 생성 답변을 만들 수 없습니다. 검색 근거만 확인해 주세요."
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(model=model, messages=build_prompt(question, context), temperature=0.1)
    return resp.choices[0].message.content or ""


def citations_text(items: list[RetrievedChunk]) -> str:
    lines: list[str] = []
    for idx, item in enumerate(items, start=1):
        lines.append(f"[{idx}] {item.law_name} | 시행일: {item.enforcement_date} | {item.source_url}")
    return "\n".join(lines)

