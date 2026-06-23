# Łódź Rental Finder

A rental-search app for Łódź, Poland. Describe what you're looking for in plain English, and it scrapes live listings from OLX.pl, Otodom.pl, and Rentola.pl, dedupes cross-posted flats, and scores/ranks them against your brief (budget, rooms, district, renovation preference).

No landlord chat, no accounts, no PII storage — just on-demand scraping and ranking.

## Stack

- **Backend:** Python, FastAPI, httpx (async scraping), Pydantic
- **Frontend:** Next.js, React, Tailwind CSS

## How it works

1. You type a brief like `"2 rooms, budget 2500 PLN, Bałuty or Polesie"`.
2. The backend parses it into budget/rooms/district/renovation filters, kicks off a background job, and scrapes all three sources in parallel.
3. Listings are deduped (same flat cross-posted under different titles), filtered against your budget/district, and scored on a 0–10 scale across four weighted factors: budget fit, room fit, district fit, renovation fit.
4. The frontend polls the job until it's done and renders a ranked grid of results.

## Local development

**Backend**

```bash
cd backend
python -m venv venv
./venv/Scripts/activate   # or source venv/bin/activate on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8080` by default — set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` to point elsewhere.

## API

- `GET /health` → `{"ok": true}`
- `POST /api/scan` with `{"brief": "..."}` → `{"jobId": "..."}`
- `GET /api/scan/{jobId}` → job status, scan log, funnel stats, and ranked results

## Deployment

See [DEPLOY.md](DEPLOY.md) — Railway for the backend, Vercel for the frontend.
