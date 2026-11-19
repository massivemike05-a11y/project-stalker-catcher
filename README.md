# Link Logger

Consent-based visitor logger. Frontend on GitHub Pages, backend on Render (free tier) with PostgreSQL.

## Flow
1. Visitor opens your GitHub Pages link
2. Sees terms notice, clicks "I Accept"
3. Types their handle, submits
4. Backend saves handle + time + referrer (Instagram, etc.) to PostgreSQL
5. You view the full list at your Render `/admin?password=...`

## Files
- `backend/main.py` — FastAPI app
- `backend/requirements.txt` — Python deps
- `frontend/index.html` — consent page + handle form
- `backend/.env.example` — env vars template

## Deploy
1. Push this repo to GitHub
2. Render: create free PostgreSQL, note `DATABASE_URL`
3. Render: create Web Service from this repo, root dir `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Env: `ADMIN_PASSWORD`, `DATABASE_URL`
4. GitHub Pages: host `frontend/index.html`, set `BACKEND_URL` to your Render URL
