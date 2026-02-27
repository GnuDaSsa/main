# Design: 아이디어 제안소 (Idea Suggestion Box)

**Feature ID**: idea-suggestion
**Created**: 2026-02-27
**Phase**: Design
**Reference Plan**: `docs/01-plan/features/idea-suggestion.plan.md`

---

## 1. 아키텍처 개요

```
app.py (수정)
  ├── 상수: IDEA = "아이디어 제안소"
  ├── 사이드바 Community 섹션에 버튼 추가
  └── page_to_run_map: IDEA → "page10.py"

page10.py (신규)
  ├── run()
  │   ├── [공통] MongoDB 연결 확인
  │   ├── [공통] 제안 폼 (누구나)
  │   ├── [관리자] Admin 로그인/로그아웃
  │   └── [관리자] 아이디어 목록 + 상태관리 + 삭제
  └── _check_admin() — page8.py와 동일 패턴

MongoDB (기존 연결 재사용)
  └── DB: dlc / Collection: ideas
```

---

## 2. 파일별 변경 명세

### 2-1. `app.py` 수정

#### 추가할 상수 (라인 232 다음)
```python
IDEA = "아이디어 제안소"
```

#### 사이드바 Community 섹션 (라인 255 다음에 버튼 추가)
```python
if st.button(IDEA, use_container_width=True):
    st.session_state.page = IDEA
```

#### page_to_run_map 추가 (LAW 항목 다음)
```python
IDEA: "page10.py",
```

---

### 2-2. `page10.py` 전체 설계

#### 임포트
```python
from datetime import datetime, timezone
import streamlit as st
from mongo_env import get_mongo_uri, get_mongo_db, get_setting, get_collection as _mongo_get_collection
```

#### 상수
```python
STATUSES = ["제안됨", "검토중", "채택", "보류"]
STATUS_COLORS = {
    "제안됨": "🔵",
    "검토중": "🟡",
    "채택": "🟢",
    "보류": "🔴",
}
CONTENT_MIN = 10   # 최소 글자 수
CONTENT_MAX = 500  # 최대 글자 수
TITLE_MAX   = 100
```

#### 함수 구조

```
run()
 ├── 1. MongoDB 연결 (get_mongo_uri / get_collection)
 │      실패 시: st.error + st.info + return
 ├── 2. 인덱스 생성 (created_at: -1)
 ├── 3. 헤더: st.title + st.caption
 ├── 4. 제안 폼 섹션 ──────────────────────────────
 │      st.subheader("💡 아이디어 제안하기")
 │      with st.form("idea_form", clear_on_submit=True):
 │        title   = st.text_input(
 │                    "제목 (선택)",
 │                    placeholder="예: AI 회의록 자동 요약 도구",
 │                    max_chars=TITLE_MAX)
 │        content = st.text_area(
 │                    "아이디어 내용 *",
 │                    height=140,
 │                    placeholder="예: 회의 중 녹음을 AI가 요약해주는 기능이 있으면 좋겠어요.\n"
 │                                "카카오톡으로 공유도 되면 더 좋을 것 같습니다!",
 │                    max_chars=CONTENT_MAX)
 │        submitted = st.form_submit_button("제안하기", type="primary")
 │      if submitted:
 │        → 유효성 검사 (content 길이 >= CONTENT_MIN)
 │        → MongoDB insert: {title, content, created_at, status:"제안됨"}
 │        → st.success("제안이 등록되었습니다! 감사합니다.")
 ├── 5. 구분선: st.divider()
 ├── 6. 관리자 영역 ────────────────────────────────
 │    ├── 6-1. Admin 로그인 (비인증 시 expander)
 │    │         pw_input → ADMIN_PASSWORD 비교
 │    │         성공 → session_state.admin_authenticated = True + rerun
 │    ├── 6-2. Admin 로그아웃 버튼 (인증 시)
 │    └── 6-3. 아이디어 목록 (관리자 전용)
 │              if is_admin:
 │                st.subheader(f"전체 아이디어 ({총건수})")
 │                상태 필터 selectbox (All + STATUSES)
 │                for doc in docs:
 │                  with st.expander(제목 또는 내용 앞 30자):
 │                    st.caption(날짜 + 상태 배지)
 │                    st.write(content)
 │                    col1, col2 = st.columns([3, 1])
 │                    col1: 상태 변경 selectbox + "변경" 버튼
 │                    col2: "삭제" 버튼 → 확인 후 delete_one
 └── 7. 일반 사용자 채택 아이디어 공개 (선택적)
          st.subheader("채택된 아이디어")
          status="채택"인 문서만 조회
          각 아이디어 제목/내용 표시 (읽기 전용)
```

---

## 3. MongoDB 도큐먼트 스키마

```json
{
  "_id":        "ObjectId (자동생성)",
  "title":      "string | null  (선택, max 100자)",
  "content":    "string         (필수, min 10자, max 500자)",
  "created_at": "datetime (UTC)",
  "status":     "string         (제안됨 | 검토중 | 채택 | 보류)"
}
```

**인덱스**
- `created_at: -1` (최신순 정렬)
- `status: 1` (상태 필터 성능)

---

## 4. 컴포넌트 상세

### 4-1. 제안 폼

| 필드 | 타입 | 필수 | 제약 | Placeholder |
|------|------|------|------|-------------|
| 제목 | text_input | 아니오 | max 100자 | `예: AI 회의록 자동 요약 도구` |
| 내용 | text_area | 예 | min 10자, max 500자 | `예: 회의 중 녹음을 AI가 요약해주는 기능이 있으면 좋겠어요.\n카카오톡으로 공유도 되면 더 좋을 것 같습니다!` |

> Streamlit `placeholder` 파라미터 → 흐린 색으로 예시 표시, 클릭(포커스) 시 자동 사라짐

### 4-2. 유효성 검사

```python
content = content.strip()
if len(content) < CONTENT_MIN:
    st.warning(f"내용을 {CONTENT_MIN}자 이상 입력해주세요.")
    # return (폼 제출 중단)
```

### 4-3. 상태 배지 표시

```python
badge = STATUS_COLORS.get(status, "⚪")
st.caption(f"{badge} {status}  |  {created_at:%Y-%m-%d %H:%M}")
```

### 4-4. 관리자 상태 변경

```python
new_status = st.selectbox("상태 변경", STATUSES, index=STATUSES.index(current_status),
                           key=f"status_{doc_id}")
if st.button("변경", key=f"change_{doc_id}"):
    col.update_one({"_id": doc["_id"]}, {"$set": {"status": new_status}})
    st.rerun()
```

---

## 5. 오류 처리

| 상황 | 처리 |
|------|------|
| MongoDB URI 없음 | `st.error` + 설정 방법 안내 + `return` |
| DB 연결 실패 | `st.error("DB 연결에 실패했습니다.")` + `return` |
| 내용 미입력 / 너무 짧음 | `st.warning` (폼 유지) |
| insert 예외 | `try/except` → `st.error("저장 중 오류가 발생했습니다.")` |

---

## 6. 구현 순서 (Do Phase 체크리스트)

```
[ ] 1. page10.py 파일 생성
[ ] 2. run() 함수 — MongoDB 연결부
[ ] 3. run() 함수 — 제안 폼 (placeholder 포함)
[ ] 4. run() 함수 — 관리자 로그인/로그아웃
[ ] 5. run() 함수 — 관리자 아이디어 목록 + 상태변경 + 삭제
[ ] 6. run() 함수 — 채택 아이디어 공개 섹션
[ ] 7. app.py 수정 — IDEA 상수 추가
[ ] 8. app.py 수정 — 사이드바 버튼 추가
[ ] 9. app.py 수정 — page_to_run_map 추가
```

---

## 7. 완료 기준 (DoD)

- [ ] `page10.py` 생성, `run()` 함수 정상 동작
- [ ] `app.py` Community 섹션에 "아이디어 제안소" 버튼 표시
- [ ] placeholder 클릭 시 사라지는 동작 확인
- [ ] 아이디어 제출 → MongoDB 저장 확인
- [ ] 관리자 상태 변경 + 삭제 동작 확인
- [ ] 채택된 아이디어 일반 사용자에게 표시 확인
