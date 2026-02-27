# Between Us Web (Vercel)

## Local run
```bash
npm install
npm run dev
```

## Environment Variables
- `MONGODB_URI`
- `MONGODB_DB` (optional, default: `dlc`)
- `LAW_API_OC`
- `OPENAI_API_KEY` (optional)
- `INGEST_SECRET`

## API
- `POST /api/recommend`
- `GET /api/health`
- `POST /api/jobs/ingest` (requires `x-ingest-secret`)

## Vercel
1. Import repo in Vercel
2. Set Root Directory = `web`
3. Add env vars
4. Deploy

## Fast env sync (from repo `.env`)
If you already keep values in `../.env`, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\push-vercel-env.ps1
```

This script:
- links the Vercel project
- uploads non-empty values for `development/preview/production`
- keys: `MONGODB_URI`, `MONGODB_DB`, `LAW_API_OC`, `OPENAI_API_KEY`, `INGEST_SECRET`
