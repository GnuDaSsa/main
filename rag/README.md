# RAG 운영 가이드 (MongoDB)

## 목적
- 법제처 API 자료를 MongoDB에 수집/관리하고 RAG 검색 기반을 유지한다.

## 준비
- `.env`에 아래 값 설정
  - `LAW_RAG_STORE=mongo`
  - `MONGODB_URI=...`
  - `LAW_API_OC=...`
  - `OPENAI_API_KEY=...` (선택)

## 수집 실행
```powershell
powershell -ExecutionPolicy Bypass -File .\rag\run_ingest_mongo.ps1
```

또는 직접 실행:
```powershell
python scripts/law_rag_ingest.py --queries 근로기준법 민법 상법 --max-pages 2 --page-size 100
```

## 검색 UI 실행
```powershell
streamlit run streamlit_law_rag.py --server.port 8512
```

## 기본 컬렉션
- `law_raw_documents`
- `law_chunks`
- `law_ingestion_logs`
