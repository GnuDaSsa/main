import os
from datetime import datetime, timezone

import streamlit as st

from mongo_env import get_mongo_uri, get_mongo_db, get_setting, get_collection as _mongo_get_collection


def run():
    st.title("AI 꿀팁 공유")
    st.caption("DB에 저장되어, 배포/코드 수정 후에도 꿀팁이 유지됩니다.")

    uri = get_mongo_uri()
    if not uri:
        st.error("MongoDB 연결 정보(MONGODB_URI)가 설정되지 않았습니다.")
        st.info(
            "로컬: `.env`로 설정하거나 OS 환경변수로 설정하세요.\n"
            "배포: Streamlit Secrets에 MONGODB_URI를 추가하세요."
        )
        return

    db_name = get_mongo_db("dlc")
    col_name = get_setting("TIPS_COLLECTION", default="tips") or "tips"

    col = _mongo_get_collection(db_name, "tips", col_key="TIPS_COLLECTION")
    if col is not None:
        try:
            col.create_index([("created_at", -1)])
            col.create_index([("tags", 1)])
        except Exception:
            pass
    if col is None:
        st.error("DB 연결에 실패했습니다.")
        st.info("MONGODB_URI / 네트워크 접근 설정을 확인하세요.")
        return

    with st.expander("새 꿀팁 등록", expanded=True):
        with st.form("tip_form", clear_on_submit=True):
            title = st.text_input("제목", placeholder="예: 프롬프트를 짧게 유지하는 법")
            category = st.selectbox(
                "분류",
                ["Prompt", "Automation", "Coding", "Content", "Tools", "Work", "Other"],
                index=0,
            )
            body = st.text_area("내용", height=160, placeholder="핵심 팁을 짧고 명확하게 적어주세요.")
            tags_raw = st.text_input("태그(쉼표로 구분)", placeholder="예: streamlit, prompt, 업무")
            link = st.text_input("참고 링크(선택)", placeholder="https://...")
            submitted = st.form_submit_button("등록", type="primary")

        if submitted:
            title = title.strip()
            body = body.strip()
            if not title or not body:
                st.warning("제목과 내용을 입력하세요.")
            else:
                tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
                doc = {
                    "title": title,
                    "category": category,
                    "body": body,
                    "tags": tags,
                    "link": link.strip() or None,
                    "created_at": datetime.now(timezone.utc),
                }
                col.insert_one(doc)
                st.success("등록 완료")

    st.divider()

    q = st.text_input("검색", placeholder="제목/내용/태그 검색")
    cat = st.selectbox("분류 필터", ["All", "Prompt", "Automation", "Coding", "Content", "Tools", "Work", "Other"])

    query = {}
    if cat != "All":
        query["category"] = cat
    if q.strip():
        q2 = q.strip()
        query["$or"] = [
            {"title": {"$regex": q2, "$options": "i"}},
            {"body": {"$regex": q2, "$options": "i"}},
            {"tags": {"$regex": q2, "$options": "i"}},
        ]

    docs = list(col.find(query).sort("created_at", -1).limit(200))

    st.subheader(f"등록된 꿀팁 ({len(docs)})")
    if not docs:
        st.info("아직 등록된 꿀팁이 없습니다.")
        return

    for d in docs:
        header = f"[{d.get('category','Other')}] {d.get('title','(no title)')}"
        with st.expander(header, expanded=False):
            tags = d.get("tags") or []
            if tags:
                st.caption("tags: " + ", ".join(tags))
            st.write(d.get("body", ""))
            if d.get("link"):
                st.write(d["link"])


if __name__ == "__main__":
    run()
