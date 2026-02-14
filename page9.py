import json
import os
from datetime import datetime, timezone

import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from mongo_env import get_setting, get_collection

LAW_API_BASE = "http://www.law.go.kr/DRF/lawSearch.do"
MAX_LAW_RESULTS = 5
MAX_PREC_RESULTS = 5


def _get_oc():
    return get_setting("LAW_API_OC") or ""


def _search_laws(oc: str, query: str) -> list[dict]:
    try:
        resp = requests.get(LAW_API_BASE, params={
            "OC": oc,
            "target": "law",
            "type": "JSON",
            "query": query,
            "display": MAX_LAW_RESULTS,
        }, timeout=10)
        data = resp.json()
        laws = data.get("LawSearch", {}).get("law", [])
        if isinstance(laws, dict):
            laws = [laws]
        return laws
    except Exception:
        return []


def _search_precedents(oc: str, query: str) -> list[dict]:
    try:
        resp = requests.get(LAW_API_BASE, params={
            "OC": oc,
            "target": "prec",
            "type": "JSON",
            "query": query,
            "display": MAX_PREC_RESULTS,
        }, timeout=10)
        data = resp.json()
        precs = data.get("PrecSearch", {}).get("prec", [])
        if isinstance(precs, dict):
            precs = [precs]
        return precs
    except Exception:
        return []


def _extract_keywords(client: OpenAI, question: str) -> list[str]:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "사용자의 법률 관련 질문에서 법제처 법령 검색에 적합한 핵심 키워드를 "
                    "1~3개 추출하세요. JSON 형식으로 {\"keywords\": [\"키워드1\", \"키워드2\"]} 반환."
                )},
                {"role": "user", "content": question},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        parsed = json.loads(resp.choices[0].message.content)
        return parsed.get("keywords", [question])
    except Exception:
        return [question]


def _build_context(laws: list, precs: list) -> str:
    parts = []
    if laws:
        parts.append("=== 관련 법령 ===")
        for i, law in enumerate(laws, 1):
            name = law.get("법령명한글", law.get("법령명", ""))
            parts.append(f"[법령 {i}] {name} (시행: {law.get('시행일자', 'N/A')})")
    if precs:
        parts.append("\n=== 관련 판례 ===")
        for i, p in enumerate(precs, 1):
            parts.append(
                f"[판례 {i}] {p.get('사건명', '')} "
                f"(사건번호: {p.get('사건번호', 'N/A')}, "
                f"선고일: {p.get('선고일자', 'N/A')})"
            )
    text = "\n".join(parts)
    return text[:8000]


def _generate_answer(client: OpenAI, question: str, context: str):
    system_prompt = (
        "당신은 대한민국 법률 전문 AI 어시스턴트입니다. "
        "아래 제공된 법령 및 판례 자료를 참고하여 사용자의 질문에 종합적으로 답변하세요.\n"
        "답변 규칙:\n"
        "1. 관련 법령의 법령명과 조문 정보를 명시할 것\n"
        "2. 관련 판례의 사건번호와 판결요지를 인용할 것\n"
        "3. 법률적 해석과 실무적 조언을 구분하여 서술할 것\n"
        "4. 답변 마지막에 '참고 출처' 섹션을 만들어 인용한 법령명, 판례번호를 정리할 것\n"
        "5. 이 답변은 법률 자문이 아닌 정보 제공 목적임을 안내할 것\n\n"
        f"--- 참고 자료 ---\n{context}"
    )
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        stream=True,
    )


def _save_to_mongo(question, keywords, laws_count, precs_count, answer_text):
    try:
        col = get_collection("dlc", "law_queries", col_key="LAW_QUERIES_COLLECTION")
        if col is not None:
            col.insert_one({
                "question": question,
                "keywords": keywords,
                "laws_found": laws_count,
                "precs_found": precs_count,
                "answer_preview": answer_text[:500],
                "created_at": datetime.now(timezone.utc),
            })
    except Exception:
        pass


def run():
    load_dotenv()

    st.title("AI 법률 검색 어시스턴트")
    st.caption("법제처 공개 법령/판례 데이터 기반 | 법률 자문이 아닌 정보 제공 목적")

    oc = _get_oc()
    if not oc:
        st.error("법제처 API OC 값(LAW_API_OC)이 설정되지 않았습니다.")
        st.info("`.env` 파일 또는 Streamlit Secrets에 LAW_API_OC를 추가하세요.")
        return

    api_key = get_setting("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다.")
        return

    client = OpenAI(api_key=api_key)

    if "law_answer" not in st.session_state:
        st.session_state.law_answer = None

    question = st.text_area(
        "법률 관련 질문을 입력하세요",
        height=120,
        placeholder="예: 임대차 계약 갱신 요구권은 몇 년까지 행사할 수 있나요?",
    )

    search_clicked = st.button("검색 및 답변 생성", type="primary", use_container_width=True)

    if search_clicked and question.strip():
        with st.spinner("키워드 추출 중..."):
            keywords = _extract_keywords(client, question)
        st.info(f"검색 키워드: {', '.join(keywords)}")

        all_laws = []
        all_precs = []
        with st.spinner("법제처 API 검색 중..."):
            seen_law_ids = set()
            seen_prec_ids = set()
            for kw in keywords:
                for law in _search_laws(oc, kw):
                    lid = law.get("법령ID", law.get("법령명한글", str(law)))
                    if lid not in seen_law_ids:
                        seen_law_ids.add(lid)
                        all_laws.append(law)
                for prec in _search_precedents(oc, kw):
                    pid = prec.get("판례일련번호", prec.get("사건번호", str(prec)))
                    if pid not in seen_prec_ids:
                        seen_prec_ids.add(pid)
                        all_precs.append(prec)

        c1, c2 = st.columns(2)
        c1.metric("관련 법령", f"{len(all_laws)}건")
        c2.metric("관련 판례", f"{len(all_precs)}건")

        if all_laws:
            with st.expander(f"검색된 법령 ({len(all_laws)}건)", expanded=False):
                for law in all_laws:
                    name = law.get("법령명한글", law.get("법령명", "알 수 없음"))
                    date = law.get("시행일자", "N/A")
                    st.markdown(f"- **{name}** (시행: {date})")

        if all_precs:
            with st.expander(f"검색된 판례 ({len(all_precs)}건)", expanded=False):
                for p in all_precs:
                    name = p.get("사건명", "알 수 없음")
                    num = p.get("사건번호", "N/A")
                    st.markdown(f"- **{name}** ({num})")

        if not all_laws and not all_precs:
            st.warning("관련 법령/판례를 찾지 못했습니다. 일반 지식 기반으로 답변합니다.")

        context = _build_context(all_laws, all_precs)
        st.subheader("AI 답변")
        answer_placeholder = st.empty()
        full_text = ""
        completion = _generate_answer(client, question, context)
        for chunk in completion:
            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                full_text += delta.content
                answer_placeholder.markdown(full_text)

        st.session_state.law_answer = full_text

        st.divider()
        st.caption(
            "이 답변은 법제처 공개 데이터와 AI를 활용한 정보 제공 목적이며, "
            "정식 법률 자문을 대체하지 않습니다. 정확한 법률 판단은 변호사 등 "
            "전문가와 상담하시기 바랍니다."
        )

        _save_to_mongo(question, keywords, len(all_laws), len(all_precs), full_text)

    elif not search_clicked and st.session_state.get("law_answer"):
        st.subheader("AI 답변 (이전 검색 결과)")
        st.markdown(st.session_state.law_answer)


if __name__ == "__main__":
    run()
