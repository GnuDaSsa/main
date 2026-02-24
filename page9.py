import json
import os
from datetime import datetime, timezone

import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from mongo_env import get_setting, get_collection

# HTTPS 필수 (HTTP는 프록시에서 차단됨)
LAW_API_BASE = "https://www.law.go.kr/DRF/lawSearch.do"
MAX_LAW_RESULTS = 5
MAX_PREC_RESULTS = 5

RECOMMENDED_QUESTIONS = [
    "임대차 계약 갱신 요구권은 몇 년까지 행사할 수 있나요?",
    "부당해고를 당했을 때 어떤 법적 조치를 취할 수 있나요?",
    "층간소음 피해에 대한 민사상 손해배상 청구가 가능한가요?",
    "온라인 쇼핑몰에서 환불 거부 시 소비자 보호 권리는?",
    "교통사고 후 보험사와 합의 시 주의해야 할 법적 사항은?",
    "개인정보 유출 피해 신고 방법과 손해배상 청구 방법은?",
]


def _get_oc():
    return get_setting("LAW_API_OC") or ""


def _is_html_response(text: str) -> bool:
    """응답이 JSON이 아닌 HTML 에러 페이지인지 확인."""
    stripped = text.strip()
    return stripped.startswith("<!DOCTYPE") or stripped.startswith("<html")


def _check_api_status(oc: str) -> tuple[bool, str]:
    """API 연결 상태를 확인. (ok, message) 반환."""
    try:
        resp = requests.get(
            LAW_API_BASE,
            params={"OC": oc, "target": "law", "type": "JSON", "query": "민법", "display": 1},
            timeout=8,
        )
        if _is_html_response(resp.text):
            return False, "OC 값이 유효하지 않거나 API 서버 오류입니다. (법제처에 OC 등록 필요)"
        resp.json()  # JSON 파싱 검증
        return True, "API 정상 연결"
    except requests.exceptions.ConnectionError:
        return False, "법제처 서버 연결 실패 (네트워크 오류)"
    except requests.exceptions.Timeout:
        return False, "법제처 API 응답 시간 초과"
    except ValueError:
        return False, "API 응답이 JSON 형식이 아닙니다."
    except Exception as e:
        return False, f"알 수 없는 오류: {e}"


def _search_laws(oc: str, query: str) -> tuple[list[dict], str | None]:
    """(결과 목록, 에러메시지) 반환."""
    try:
        resp = requests.get(
            LAW_API_BASE,
            params={
                "OC": oc,
                "target": "law",
                "type": "JSON",
                "query": query,
                "display": MAX_LAW_RESULTS,
            },
            timeout=10,
        )
        if _is_html_response(resp.text):
            return [], "법제처 API가 HTML 오류 페이지를 반환했습니다. OC 값을 확인하세요."
        data = resp.json()
        laws = data.get("LawSearch", {}).get("law", [])
        if isinstance(laws, dict):
            laws = [laws]
        return laws, None
    except requests.exceptions.Timeout:
        return [], "법제처 API 응답 시간 초과"
    except ValueError:
        return [], "API 응답 파싱 실패 (JSON 형식 아님)"
    except Exception as e:
        return [], f"법령 검색 오류: {e}"


def _search_precedents(oc: str, query: str) -> tuple[list[dict], str | None]:
    """(결과 목록, 에러메시지) 반환."""
    try:
        resp = requests.get(
            LAW_API_BASE,
            params={
                "OC": oc,
                "target": "prec",
                "type": "JSON",
                "query": query,
                "display": MAX_PREC_RESULTS,
            },
            timeout=10,
        )
        if _is_html_response(resp.text):
            return [], "법제처 API가 HTML 오류 페이지를 반환했습니다. OC 값을 확인하세요."
        data = resp.json()
        precs = data.get("PrecSearch", {}).get("prec", [])
        if isinstance(precs, dict):
            precs = [precs]
        return precs, None
    except requests.exceptions.Timeout:
        return [], "법제처 API 응답 시간 초과"
    except ValueError:
        return [], "API 응답 파싱 실패 (JSON 형식 아님)"
    except Exception as e:
        return [], f"판례 검색 오류: {e}"


def _extract_keywords(client: OpenAI, question: str) -> list[str]:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "사용자의 법률 관련 질문에서 법제처 법령 검색에 적합한 핵심 키워드를 "
                        "1~3개 추출하세요. JSON 형식으로 {\"keywords\": [\"키워드1\", \"키워드2\"]} 반환."
                    ),
                },
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


def _generate_answer(client: OpenAI, question: str, context: str, api_ok: bool):
    if api_ok and context:
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
    else:
        system_prompt = (
            "당신은 대한민국 법률 전문 AI 어시스턴트입니다. "
            "법제처 API 연동이 현재 불가하여 실시간 법령/판례 데이터를 제공하지 못합니다. "
            "학습된 법률 지식을 바탕으로 최선을 다해 답변하되, 반드시 다음을 포함하세요:\n"
            "1. 관련된 주요 법률 명칭과 개괄적인 내용\n"
            "2. 법률적 해석과 실무적 조언\n"
            "3. 답변 마지막에 '⚠️ 주의: 실시간 법령 데이터 연동 불가 - 학습 데이터 기반 답변' 안내\n"
            "4. 정확한 법률 판단을 위해 전문가 상담 권유"
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
            col.insert_one(
                {
                    "question": question,
                    "keywords": keywords,
                    "laws_found": laws_count,
                    "precs_found": precs_count,
                    "answer_preview": answer_text[:500],
                    "created_at": datetime.now(timezone.utc),
                }
            )
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

    # ── API 상태 진단 (세션당 1회) ──────────────────────────────────────────
    if "api_status_checked" not in st.session_state:
        with st.spinner("법제처 API 연결 상태 확인 중..."):
            ok, msg = _check_api_status(oc)
        st.session_state.api_status_ok = ok
        st.session_state.api_status_msg = msg
        st.session_state.api_status_checked = True

    api_ok = st.session_state.api_status_ok
    if api_ok:
        st.success(f"✅ 법제처 API 연결 정상")
    else:
        st.warning(f"⚠️ 법제처 API 연결 불가: {st.session_state.api_status_msg}")
        st.info("API 미연결 상태에서는 AI 학습 데이터 기반으로 답변합니다.")

    if st.button("🔄 API 상태 재확인", help="법제처 API 연결을 다시 테스트합니다."):
        st.session_state.pop("api_status_checked", None)
        st.rerun()

    st.divider()

    if "law_answer" not in st.session_state:
        st.session_state.law_answer = None
    if "preset_question" not in st.session_state:
        st.session_state.preset_question = ""

    # ── 추천 질문 ──────────────────────────────────────────────────────────
    st.markdown("**💡 추천 질문**")
    cols = st.columns(3)
    for i, q in enumerate(RECOMMENDED_QUESTIONS):
        col = cols[i % 3]
        label = q if len(q) <= 22 else q[:21] + "…"
        if col.button(label, key=f"preset_{i}", use_container_width=True, help=q):
            st.session_state.preset_question = q
            st.rerun()

    st.markdown("")

    # ── 질문 입력 ──────────────────────────────────────────────────────────
    question = st.text_area(
        "법률 관련 질문을 입력하세요",
        value=st.session_state.preset_question,
        height=120,
        placeholder="예: 임대차 계약 갱신 요구권은 몇 년까지 행사할 수 있나요?",
    )

    search_clicked = st.button("검색 및 답변 생성", type="primary", use_container_width=True)

    if search_clicked and question.strip():
        # 추천 질문으로 채운 뒤 검색하면 초기화
        st.session_state.preset_question = ""

        with st.spinner("키워드 추출 중..."):
            keywords = _extract_keywords(client, question)
        st.info(f"🔍 검색 키워드: **{', '.join(keywords)}**")

        all_laws: list[dict] = []
        all_precs: list[dict] = []
        api_errors: list[str] = []

        if api_ok:
            with st.spinner("법제처 API 검색 중..."):
                seen_law_ids: set = set()
                seen_prec_ids: set = set()
                for kw in keywords:
                    laws, err = _search_laws(oc, kw)
                    if err:
                        api_errors.append(err)
                    for law in laws:
                        lid = law.get("법령ID", law.get("법령명한글", str(law)))
                        if lid not in seen_law_ids:
                            seen_law_ids.add(lid)
                            all_laws.append(law)

                    precs, err = _search_precedents(oc, kw)
                    if err:
                        api_errors.append(err)
                    for prec in precs:
                        pid = prec.get("판례일련번호", prec.get("사건번호", str(prec)))
                        if pid not in seen_prec_ids:
                            seen_prec_ids.add(pid)
                            all_precs.append(prec)

            # API 오류 메시지 표시
            for err_msg in set(api_errors):
                st.error(f"⚠️ {err_msg}")

        # ── 검색 결과 요약 ──────────────────────────────────────────────────
        c1, c2 = st.columns(2)
        c1.metric("관련 법령", f"{len(all_laws)}건")
        c2.metric("관련 판례", f"{len(all_precs)}건")

        if all_laws:
            with st.expander(f"📜 검색된 법령 ({len(all_laws)}건)", expanded=False):
                for law in all_laws:
                    name = law.get("법령명한글", law.get("법령명", "알 수 없음"))
                    date = law.get("시행일자", "N/A")
                    law_id = law.get("법령ID", "")
                    if law_id:
                        link = f"https://www.law.go.kr/법령/{name}"
                        st.markdown(f"- **[{name}]({link})** (시행: {date})")
                    else:
                        st.markdown(f"- **{name}** (시행: {date})")

        if all_precs:
            with st.expander(f"⚖️ 검색된 판례 ({len(all_precs)}건)", expanded=False):
                for p in all_precs:
                    name = p.get("사건명", "알 수 없음")
                    num = p.get("사건번호", "N/A")
                    date = p.get("선고일자", "N/A")
                    st.markdown(f"- **{name}** `{num}` (선고: {date})")

        if api_ok and not all_laws and not all_precs and not api_errors:
            st.info("관련 법령/판례를 찾지 못했습니다. AI 학습 데이터 기반으로 답변합니다.")

        # ── AI 답변 생성 ────────────────────────────────────────────────────
        context = _build_context(all_laws, all_precs)
        source_label = "법제처 데이터 + AI" if (all_laws or all_precs) else "AI 학습 데이터"
        st.subheader(f"AI 답변 ({source_label})")

        answer_placeholder = st.empty()
        full_text = ""
        completion = _generate_answer(client, question, context, api_ok and bool(context))
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
