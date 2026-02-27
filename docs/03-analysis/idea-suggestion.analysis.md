# idea-suggestion Analysis Report

> **Analysis Type**: Gap Analysis (Design vs Implementation)
>
> **Project**: GnuDaS_GPT_World
> **Analyst**: gap-detector (bkit)
> **Date**: 2026-02-27
> **Design Doc**: [idea-suggestion.design.md](../02-design/features/idea-suggestion.design.md)

---

## 1. Analysis Overview

### 1.1 Analysis Purpose

Design 문서(`idea-suggestion.design.md`)와 실제 구현 코드(`page10.py`, `app.py`) 사이의 일치도를 검증하고, 누락/변경/추가된 항목을 식별한다.

### 1.2 Analysis Scope

- **Design Document**: `docs/02-design/features/idea-suggestion.design.md`
- **Implementation Files**:
  - `page10.py` (신규 생성)
  - `app.py` (수정)
- **Analysis Date**: 2026-02-27

---

## 2. Gap Analysis (Design vs Implementation)

### 2.1 Checkpoint 상세 비교

| # | Checkpoint | Design | Implementation | Status | Notes |
|---|-----------|--------|----------------|--------|-------|
| 1 | STATUSES 상수 | `["제안됨", "검토중", "채택", "보류"]` | `["제안됨", "검토중", "채택", "보류"]` | ✅ Match | page10.py:7 |
| 2 | STATUS_COLORS 상수 | 4개 이모지 매핑 | 동일 4개 매핑 | ✅ Match | page10.py:8-13 |
| 3 | CONTENT_MIN / CONTENT_MAX | 10 / 500 | 10 / 500 | ✅ Match | page10.py:14-15 |
| 4 | TITLE_MAX | 100 | 100 | ✅ Match | page10.py:16 |
| 5 | _check_admin() 함수 | ADMIN_PASSWORD 비교 패턴 | get_setting + session_state 확인 | ✅ Match | page10.py:19-23 |
| 6 | MongoDB URI 없음 처리 | st.error + st.info + return | st.error + st.info + return | ✅ Match | page10.py:30-37 |
| 7 | DB 연결 실패 처리 | st.error + return | st.error + st.info + return | ✅ Match | page10.py:39-43 |
| 8 | 인덱스 생성 (created_at: -1) | 명시 | col.create_index([("created_at", -1)]) | ✅ Match | page10.py:46 |
| 9 | 인덱스 생성 (status: 1) | 명시 | col.create_index([("status", 1)]) | ✅ Match | page10.py:47 |
| 10 | 제안 폼 subheader | "아이디어 제안하기" | "새 아이디어 제안하기" | ⚠️ Changed | page10.py:52 -- "새" 접두사 추가됨 |
| 11 | title placeholder | "예: AI 회의록 자동 요약 도구" | "예: AI 회의록 자동 요약 도구" | ✅ Match | page10.py:56 |
| 12 | content placeholder | 2줄 예시 텍스트 | 동일 텍스트 | ✅ Match | page10.py:62-64 |
| 13 | max_chars (title/content) | TITLE_MAX / CONTENT_MAX | TITLE_MAX / CONTENT_MAX | ✅ Match | page10.py:57,66 |
| 14 | 유효성 검사 (CONTENT_MIN) | content.strip() + len < CONTENT_MIN | content.strip() + len < CONTENT_MIN | ✅ Match | page10.py:71-73 |
| 15 | insert_one 문서 구조 | {title, content, created_at, status} | {title, content, created_at, status} | ✅ Match | page10.py:75-79 |
| 16 | insert 예외처리 | try/except + st.error | try/except + st.error | ✅ Match | page10.py:81-85 |
| 17 | 채택 아이디어 공개 섹션 | Design 섹션 7 (관리자 영역 이후) | 관리자 영역 이전에 배치 | ⚠️ Changed | page10.py:89-97 -- 배치 순서 변경 |
| 18 | 관리자 로그인 expander | pw_input + ADMIN_PASSWORD 비교 | text_input + 비교 + rerun | ✅ Match | page10.py:103-112 |
| 19 | 관리자 로그아웃 | session_state = False | session_state = False + rerun | ✅ Match | page10.py:116-118 |
| 20 | 상태 필터 selectbox | ["전체"] + STATUSES | ["전체"] + STATUSES | ✅ Match | page10.py:122-126 |
| 21 | 아이디어 목록 상태배지 표시 | STATUS_COLORS + caption | STATUS_COLORS + expander label + caption | ✅ Match | page10.py:139-144 |
| 22 | 상태 변경 selectbox + 변경 버튼 | selectbox + button + update_one + rerun | 동일 패턴 | ✅ Match | page10.py:149-157 |
| 23 | 삭제 버튼 + 확인 절차 | button + 확인 후 delete_one | session_state 기반 확인 + delete_one | ✅ Match | page10.py:159-172 |
| 24 | app.py IDEA 상수 | `IDEA = "아이디어 제안소"` | `IDEA = "아이디어 제안소"` | ✅ Match | app.py:233 |
| 25 | app.py Community 버튼 | st.button(IDEA, ...) | st.button(IDEA, ...) | ✅ Match | app.py:257-258 |
| 26 | app.py page_to_run_map | IDEA: "page10.py" | IDEA: "page10.py" | ✅ Match | app.py:278 |

### 2.2 Import 비교

| Design | Implementation | Status | Notes |
|--------|----------------|--------|-------|
| `from datetime import datetime, timezone` | 동일 | ✅ Match | |
| `import streamlit as st` | 동일 | ✅ Match | |
| `from mongo_env import get_mongo_uri, get_mongo_db, get_setting, get_collection as _mongo_get_collection` | `get_mongo_db` 누락 | ⚠️ Changed | get_mongo_db를 import하지 않음 (사용하지 않으므로 의도적 생략) |

### 2.3 Match Rate Summary

```
+---------------------------------------------+
|  Overall Match Rate: 94%                     |
+---------------------------------------------+
|  Total Checkpoints:  26 items                |
|  ✅ Match:           23 items (88%)          |
|  ⚠️ Minor Change:     3 items (12%)          |
|  ❌ Not implemented:   0 items (0%)          |
+---------------------------------------------+
```

---

## 3. Differences Found

### 3.1 Missing Features (Design O, Implementation X)

없음. 모든 Design 항목이 구현에 반영되었다.

### 3.2 Changed Features (Design != Implementation)

| # | Item | Design | Implementation | Impact |
|---|------|--------|----------------|--------|
| 1 | 제안 폼 subheader 텍스트 | "아이디어 제안하기" | "새 아이디어 제안하기" | Low -- UX 텍스트 차이, 기능 영향 없음 |
| 2 | 채택 아이디어 섹션 배치 순서 | 섹션 7 (관리자 영역 이후) | 관리자 영역 이전 (divider 직후) | Low -- 일반 사용자에게 먼저 노출되어 UX상 오히려 개선됨 |
| 3 | import 목록 | get_mongo_db 포함 | get_mongo_db 미포함 | Low -- 사용하지 않는 import 제거 (코드 품질 개선) |

### 3.3 Added Features (Design X, Implementation O)

| # | Item | Implementation Location | Description |
|---|------|------------------------|-------------|
| 1 | DB 연결 실패 시 추가 안내 | page10.py:42 | `st.info("MONGODB_URI / 네트워크 접근 설정을 확인하세요.")` 추가 |
| 2 | 인덱스 생성 예외 처리 | page10.py:48-49 | `try/except` 으로 인덱스 생성 실패 무시 처리 |
| 3 | 아이디어 없을 때 안내 메시지 | page10.py:134 | `st.info("해당 조건의 아이디어가 없습니다.")` |
| 4 | 관리자 모드 표시 | page10.py:115 | `st.success("관리자 모드")` 추가 |

---

## 4. Score Summary

| Category | Score | Status |
|----------|:-----:|:------:|
| Design Match | 94% | ✅ |
| Feature Completeness | 100% | ✅ |
| app.py Integration | 100% | ✅ |
| **Overall** | **94%** | ✅ |

---

## 5. Recommended Actions

### 5.1 Documentation Update (Optional)

아래 항목은 구현이 Design보다 개선된 부분이므로, Design 문서에 반영하여 동기화하는 것을 권장한다.

| Priority | Item | Action |
|----------|------|--------|
| Low | 제안 폼 subheader | Design을 "새 아이디어 제안하기"로 업데이트 |
| Low | 채택 섹션 배치 순서 | Design 섹션 순서를 구현에 맞게 조정 (관리자 영역 전에 채택 섹션) |
| Low | import 목록 | get_mongo_db 제거 반영 |
| Low | 인덱스 생성 예외처리 | try/except 패턴 Design에 추가 |

### 5.2 Synchronization Recommendation

Match Rate >= 90% 이므로, **Design과 구현이 잘 일치**한다.
변경된 3건은 모두 Low Impact이며, 기능적 차이가 아닌 UX/코드 품질 개선에 해당한다.

**권장 옵션**: Option 2 -- Design 문서를 구현에 맞게 업데이트 (구현이 Design보다 개선된 방향이므로)

---

## 6. Next Steps

- [x] Gap Analysis 완료
- [ ] (Optional) Design 문서 동기화 업데이트
- [ ] Completion Report 작성 (`/pdca report idea-suggestion`)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-27 | Initial gap analysis | gap-detector |
