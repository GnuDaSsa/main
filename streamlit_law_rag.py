from __future__ import annotations

import streamlit as st

from law_rag.assistant import citations_text, generate_answer
from law_rag.config import load_config
from law_rag.embeddings import HashEmbeddingProvider, OpenAIEmbeddingProvider
from law_rag.ingest import LawRagIngestor
from law_rag.law_api_client import LawApiClient
from law_rag.retriever import LawRetriever
from law_rag.store_factory import build_store


DEFAULT_BOOTSTRAP_QUERIES = [
    "근로기준법",
    "민법",
    "상법",
    "개인정보보호법",
    "형법",
    "행정절차법",
]


def _build_embedder(cfg):
    if cfg.openai_api_key:
        return OpenAIEmbeddingProvider(api_key=cfg.openai_api_key, model=cfg.embedding_model), "openai"
    return HashEmbeddingProvider(), "hash-fallback"


def run():
    st.set_page_config(page_title="Law RAG Assistant", layout="wide")
    st.title("Law RAG Assistant (Supabase/Mongo + 법제처 API)")
    st.caption("초기 풀로드 후 증분 동기화를 전제로 한 MVP")

    cfg = load_config()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Store", cfg.store_backend)
    c2.metric("Embedding", cfg.embedding_model)
    c3.metric("Top K", str(cfg.top_k))
    c4.metric("Raw Table", cfg.raw_collection)

    if not cfg.law_api_oc:
        st.error("LAW_API_OC 설정이 필요합니다.")
        st.stop()

    try:
        store = build_store(cfg)
    except Exception as exc:
        st.error(f"저장소 연결 실패: {exc}")
        st.info("SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY 또는 MONGODB_URI 설정을 확인해 주세요.")
        st.stop()

    embedder, embedder_mode = _build_embedder(cfg)

    tab_ingest, tab_search = st.tabs(["Ingest", "Search"])

    with tab_ingest:
        st.subheader("법령 데이터 수집")
        st.info(f"현재 임베딩 모드: {embedder_mode}")
        q_text = st.text_area(
            "초기 수집 키워드 (줄바꿈 구분)",
            value="\n".join(DEFAULT_BOOTSTRAP_QUERIES),
            height=160,
        )
        max_pages = st.number_input("쿼리당 최대 페이지", min_value=1, max_value=20, value=2, step=1)
        page_size = st.number_input("페이지 크기", min_value=10, max_value=100, value=100, step=10)
        if st.button("수집 실행", type="primary"):
            queries = [x.strip() for x in q_text.splitlines() if x.strip()]
            if not queries:
                st.warning("최소 1개 키워드가 필요합니다.")
            else:
                with st.spinner("법제처 API 수집/저장 중..."):
                    ingestor = LawRagIngestor(api=LawApiClient(cfg.law_api_oc), store=store, embedder=embedder)
                    stats = ingestor.run(queries=queries, max_pages=int(max_pages), page_size=int(page_size))
                st.success("수집 완료")
                st.write(
                    {
                        "query_count": stats.query_count,
                        "fetched_count": stats.fetched_count,
                        "upserted_count": stats.upserted_count,
                        "chunk_count": stats.chunk_count,
                    }
                )

    with tab_search:
        st.subheader("RAG 검색 및 답변")
        question = st.text_area("질문", placeholder="예: 근로계약 갱신 거절 시 유의할 점은?", height=120)
        if st.button("검색 + 답변 생성", type="primary"):
            if not question.strip():
                st.warning("질문을 입력해 주세요.")
            else:
                retriever = LawRetriever(store=store, embedder=embedder)
                results = retriever.search(question, top_k=cfg.top_k)
                if not results:
                    st.warning("검색 결과가 없습니다. 먼저 Ingest를 실행해 주세요.")
                else:
                    context = retriever.to_context(results)
                    answer = generate_answer(
                        api_key=cfg.openai_api_key,
                        model=cfg.answer_model,
                        question=question,
                        context=context,
                    )
                    st.markdown("### 답변")
                    st.write(answer)
                    st.markdown("### 참고출처")
                    st.code(citations_text(results))
                    with st.expander("검색된 원문 청크"):
                        for idx, item in enumerate(results, start=1):
                            st.markdown(f"**[{idx}] {item.law_name}** (score={item.score:.4f})")
                            st.write(item.text)


if __name__ == "__main__":
    run()
