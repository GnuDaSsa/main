# Vercel Deployment Plan (MVP)

## 1. Goal
- 배포 타겟을 Vercel로 고정하고, 수도권 데이트 코스 추천 MVP를 서버리스 구조로 배포한다.

## 2. Runtime Architecture
- Frontend: Next.js App Router
- Backend API: Next.js Route Handlers (`/api/*`)
- DB: MongoDB Atlas
- Scheduler: Vercel Cron (`/api/jobs/ingest`)

## 3. Required Environment Variables
- `MONGODB_URI`
- `MONGODB_DB` (default: `dlc`)
- `LAW_API_OC`
- `OPENAI_API_KEY` (optional)
- `INGEST_SECRET` (cron 보호용)

## 4. Deploy Steps
1. GitHub `main` 브랜치에 푸시
2. Vercel에서 리포 import
3. Root Directory를 `web`으로 설정
4. Environment Variables 등록
5. Production Deploy

## 5. Post-Deploy Checks
1. `/` 진입 가능
2. `/api/health` 200 응답
3. `/api/recommend` 샘플 요청 정상 응답
4. `/api/jobs/ingest`는 토큰 없으면 401

## 6. Risks and Mitigations
- 서버리스 타임아웃: 추천 로직 계산량 제한, 캐시 도입
- 외부 API 지연: 타임아웃/재시도/부분 결과 fallback
- Mongo 연결: 전역 커넥션 재사용 패턴 유지
