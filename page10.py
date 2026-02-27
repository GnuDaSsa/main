from datetime import datetime, timezone

import streamlit as st

from mongo_env import get_mongo_uri, get_setting, get_collection as _mongo_get_collection

STATUSES = ["제안됨", "검토중", "채택", "보류"]
STATUS_COLORS = {
    "제안됨": "🔵",
    "검토중": "🟡",
    "채택": "🟢",
    "보류": "🔴",
}
CONTENT_MIN = 10
CONTENT_MAX = 500
TITLE_MAX = 100


def _check_admin() -> bool:
    admin_pw = get_setting("ADMIN_PASSWORD")
    if not admin_pw:
        return False
    return st.session_state.get("admin_authenticated", False)


def run():
    st.title("💡 아이디어 제안소")
    st.caption("클럽 활동에 대한 아이디어를 자유롭게 제안해주세요. 누구나 작성할 수 있습니다.")

    uri = get_mongo_uri()
    if not uri:
        st.error("MongoDB 연결 정보(MONGODB_URI)가 설정되지 않았습니다.")
        st.info(
            "로컬: `.env`로 설정하거나 OS 환경변수로 설정하세요.\n"
            "배포: Streamlit Secrets에 MONGODB_URI를 추가하세요."
        )
        return

    col = _mongo_get_collection("dlc", "ideas", col_key="IDEAS_COLLECTION")
    if col is None:
        st.error("DB 연결에 실패했습니다.")
        st.info("MONGODB_URI / 네트워크 접근 설정을 확인하세요.")
        return

    try:
        col.create_index([("created_at", -1)])
        col.create_index([("status", 1)])
    except Exception:
        pass

    # ── 제안 폼 (누구나) ──────────────────────────────────────────
    st.subheader("새 아이디어 제안하기")
    with st.form("idea_form", clear_on_submit=True):
        title = st.text_input(
            "제목 (선택)",
            placeholder="예: AI 회의록 자동 요약 도구",
            max_chars=TITLE_MAX,
        )
        content = st.text_area(
            "아이디어 내용 *",
            height=140,
            placeholder=(
                "예: 회의 중 녹음을 AI가 요약해주는 기능이 있으면 좋겠어요.\n"
                "카카오톡으로 공유도 되면 더 좋을 것 같습니다!"
            ),
            max_chars=CONTENT_MAX,
        )
        submitted = st.form_submit_button("제안하기", type="primary")

    if submitted:
        content_stripped = content.strip()
        if len(content_stripped) < CONTENT_MIN:
            st.warning(f"내용을 {CONTENT_MIN}자 이상 입력해주세요.")
        else:
            doc = {
                "title": title.strip() or None,
                "content": content_stripped,
                "created_at": datetime.now(timezone.utc),
                "status": "제안됨",
            }
            try:
                col.insert_one(doc)
                st.success("제안이 등록되었습니다! 감사합니다. 🎉")
            except Exception:
                st.error("저장 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

    st.divider()

    # ── 채택된 아이디어 공개 (일반 사용자) ───────────────────────
    adopted = list(col.find({"status": "채택"}).sort("created_at", -1).limit(20))
    if adopted:
        st.subheader(f"🟢 채택된 아이디어 ({len(adopted)})")
        for d in adopted:
            label = d.get("title") or (d.get("content", "")[:30] + "…")
            with st.expander(label, expanded=False):
                st.write(d.get("content", ""))
                st.caption(f"등록일: {d['created_at'].strftime('%Y-%m-%d') if d.get('created_at') else '-'}")

    # ── 관리자 영역 ──────────────────────────────────────────────
    is_admin = _check_admin()
    admin_pw = get_setting("ADMIN_PASSWORD")

    if not is_admin:
        with st.expander("관리자 로그인", expanded=False):
            pw_input = st.text_input("비밀번호", type="password", key="idea_admin_pw_input")
            if st.button("로그인", key="idea_admin_login_btn"):
                if admin_pw and pw_input == admin_pw:
                    st.session_state.admin_authenticated = True
                    st.success("관리자 인증 완료")
                    st.rerun()
                else:
                    st.error("비밀번호가 틀렸습니다.")

    if is_admin:
        st.success("관리자 모드")
        if st.button("로그아웃", key="idea_admin_logout"):
            st.session_state.admin_authenticated = False
            st.rerun()

        st.subheader("전체 아이디어 관리")

        filter_status = st.selectbox(
            "상태 필터",
            ["전체"] + STATUSES,
            key="idea_filter_status",
        )

        query = {} if filter_status == "전체" else {"status": filter_status}
        docs = list(col.find(query).sort("created_at", -1).limit(200))

        st.caption(f"총 {len(docs)}건")

        if not docs:
            st.info("해당 조건의 아이디어가 없습니다.")
        else:
            for d in docs:
                doc_id = str(d["_id"])
                current_status = d.get("status", "제안됨")
                badge = STATUS_COLORS.get(current_status, "⚪")
                label = d.get("title") or (d.get("content", "")[:30] + "…")
                created = d["created_at"].strftime("%Y-%m-%d %H:%M") if d.get("created_at") else "-"

                with st.expander(f"{badge} {label}", expanded=False):
                    st.caption(f"상태: {current_status}  |  등록일: {created}")
                    st.write(d.get("content", ""))

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        new_status = st.selectbox(
                            "상태 변경",
                            STATUSES,
                            index=STATUSES.index(current_status) if current_status in STATUSES else 0,
                            key=f"idea_status_sel_{doc_id}",
                        )
                        if st.button("변경", key=f"idea_change_{doc_id}"):
                            col.update_one({"_id": d["_id"]}, {"$set": {"status": new_status}})
                            st.rerun()
                    with col2:
                        if st.button("삭제", key=f"idea_del_{doc_id}", type="secondary"):
                            st.session_state[f"idea_confirm_del_{doc_id}"] = True

                    if st.session_state.get(f"idea_confirm_del_{doc_id}", False):
                        st.warning("정말 삭제하시겠습니까?")
                        c1, c2 = st.columns(2)
                        if c1.button("예, 삭제", key=f"idea_yes_{doc_id}", type="primary"):
                            col.delete_one({"_id": d["_id"]})
                            st.session_state.pop(f"idea_confirm_del_{doc_id}", None)
                            st.success("삭제 완료")
                            st.rerun()
                        if c2.button("취소", key=f"idea_no_{doc_id}"):
                            st.session_state.pop(f"idea_confirm_del_{doc_id}", None)
                            st.rerun()


if __name__ == "__main__":
    run()
