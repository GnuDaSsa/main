# Dating Course Tech Spec (Next.js + Vercel)

## 1. Directory Layout
- `web/app/page.tsx`: 입력/결과 UI
- `web/app/api/recommend/route.ts`: 코스 추천 API
- `web/app/api/jobs/ingest/route.ts`: 수집 배치 API
- `web/app/api/health/route.ts`: 헬스체크
- `web/lib/mongodb.ts`: Mongo 커넥션
- `web/lib/recommender.ts`: 점수 계산/코스 생성
- `web/lib/ingest.ts`: 법제처 데이터 수집 로직

## 2. API Contracts
- `POST /api/recommend`
  - 입력: 남/여 역, 시간, 예산, 이동수단
  - 출력: 코스 3개 + 근거 + 주차 상태
- `POST /api/jobs/ingest`
  - 헤더 `x-ingest-secret` 필수
  - 입력: 쿼리 목록, 페이지 옵션
  - 출력: 수집 통계

## 3. Mongo Collections
- `law_raw_documents`
- `law_chunks`
- `law_ingestion_logs`

## 4. Scoring v1
- `0.35 review + 0.20 neutral_mood + 0.15 realtime + 0.15 fairness + 0.10 access + 0.05 parking`

## 5. Client UX
1. 역 입력
2. 추천 요청
3. 코스 카드 3개 노출
4. 코스별 설명/주차/이동격차 확인

## 6. Future Upgrades
- 후기 신호 고도화(LLM 분류 + 신뢰도 랭킹)
- 실시간 혼잡 지표 확장
- 사용자 피드백 기반 개인화
