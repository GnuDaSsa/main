import base64
import io
from datetime import datetime, timezone

from PIL import Image
import streamlit as st

from mongo_env import get_mongo_uri, get_mongo_db, get_setting, get_collection as _mongo_get_collection

MAX_IMAGE_MB = 10
MAX_IMAGE_BYTES = MAX_IMAGE_MB * 1024 * 1024
TARGET_B64_BYTES = 12 * 1024 * 1024  # Base64 결과 12MB 이하 (MongoDB 16MB 문서 여유)
MAX_DIMENSION = 1920


def _compress_image(file_bytes: bytes, filename: str) -> str | None:
    """이미지를 리사이즈/압축하여 data URI로 반환."""
    try:
        img = Image.open(io.BytesIO(file_bytes))
    except Exception:
        return None

    # RGBA → RGB (JPEG 저장용)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # 큰 이미지 리사이즈
    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        ratio = MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    # 품질을 낮춰가며 목표 크기에 맞춤
    for quality in (85, 70, 50, 30):
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        if len(b64) <= TARGET_B64_BYTES:
            return f"data:image/jpeg;base64,{b64}"

    # 최소 품질로도 크면 추가 리사이즈
    for scale in (0.5, 0.25):
        small = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        small.save(buf, format="JPEG", quality=30, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        if len(b64) <= TARGET_B64_BYTES:
            return f"data:image/jpeg;base64,{b64}"

    return None


def _check_admin() -> bool:
    admin_pw = get_setting("ADMIN_PASSWORD")
    if not admin_pw:
        return False
    return st.session_state.get("admin_authenticated", False)


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

    # Admin login
    admin_pw = get_setting("ADMIN_PASSWORD")
    is_admin = _check_admin()

    if not is_admin:
        with st.expander("관리자 로그인", expanded=False):
            pw_input = st.text_input("비밀번호", type="password", key="admin_pw_input")
            if st.button("로그인", key="admin_login_btn"):
                if admin_pw and pw_input == admin_pw:
                    st.session_state.admin_authenticated = True
                    st.success("관리자 인증 완료")
                    st.rerun()
                else:
                    st.error("비밀번호가 틀렸습니다.")

    if is_admin:
        st.success("관리자 모드")
        if st.button("로그아웃", key="admin_logout"):
            st.session_state.admin_authenticated = False
            st.rerun()

        with st.expander("새 꿀팁 등록", expanded=True):
            with st.form("tip_form", clear_on_submit=True):
                title = st.text_input("제목", placeholder="예: 프롬프트를 짧게 유지하는 법")
                category = st.selectbox(
                    "분류",
                    ["Prompt", "Automation", "Coding", "Content", "Tools", "Work", "Other"],
                    index=0,
                )
                body = st.text_area("내용", height=160, placeholder="핵심 팁을 짧고 명확하게 적어주세요.")
                image_file = st.file_uploader(
                    f"이미지 첨부 (선택, 최대 {MAX_IMAGE_MB}MB)",
                    type=["png", "jpg", "jpeg", "gif", "webp"],
                )
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

                    img_ok = True
                    if image_file is not None:
                        if image_file.size > MAX_IMAGE_BYTES:
                            st.error(f"이미지 크기가 {MAX_IMAGE_MB}MB를 초과합니다.")
                            img_ok = False
                        else:
                            data_uri = _compress_image(image_file.read(), image_file.name)
                            if data_uri:
                                doc["image"] = data_uri
                            else:
                                st.error("이미지 처리에 실패했습니다.")
                                img_ok = False

                    if img_ok:
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
            if d.get("image"):
                st.image(d["image"], use_container_width=True)
            st.write(d.get("body", ""))
            if d.get("link"):
                st.write(d["link"])

            # Admin can delete
            if is_admin:
                doc_id = str(d["_id"])
                if st.button("삭제", key=f"del_{doc_id}", type="secondary"):
                    st.session_state[f"confirm_del_{doc_id}"] = True
                if st.session_state.get(f"confirm_del_{doc_id}", False):
                    st.warning("정말 삭제하시겠습니까?")
                    c1, c2 = st.columns(2)
                    if c1.button("예, 삭제", key=f"yes_{doc_id}", type="primary"):
                        col.delete_one({"_id": d["_id"]})
                        st.session_state.pop(f"confirm_del_{doc_id}", None)
                        st.success("삭제 완료")
                        st.rerun()
                    if c2.button("취소", key=f"no_{doc_id}"):
                        st.session_state.pop(f"confirm_del_{doc_id}", None)
                        st.rerun()


if __name__ == "__main__":
    run()
