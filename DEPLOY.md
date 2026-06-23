# Deploying Łódź Rental Finder

Two pieces: the FastAPI backend on **Railway**, the Next.js frontend on **Vercel**. Both have free tiers that don't sleep your app (unlike Streamlit Cloud / Render free tier).

## 1. Backend → Railway

```bash
npm install -g @railway/cli
railway login
cd backend
railway init          # creates a new Railway project, pick "Empty Project"
railway up            # deploys the current backend/ folder
```

Railway's Nixpacks builder auto-detects Python from `requirements.txt` and runs `pip install -r requirements.txt`. Unlike Node, Nixpacks has no standard "start command" convention for Python, so add a `railway.json` (already included in `backend/`) that tells it how to run the app:

```json
{
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

Railway injects `PORT` automatically; `backend/app/main.py` already reads `os.environ.get("PORT", 8080)` for local fallback, so no env var setup is required for the backend itself.

After deploy:

```bash
railway domain        # generates a public *.up.railway.app URL, or attach a custom domain
```

Copy that URL — you'll need it for the frontend's `NEXT_PUBLIC_API_URL`.

**Ongoing deploys:** either keep running `railway up` from `backend/`, or connect the Railway project to a GitHub repo (Railway dashboard → Settings → Connect Repo) so every push to `main` auto-deploys.

**Cost:** Railway's free trial gives $5/month credit; this app idles near-zero CPU between scans and a single Hobby plan instance (~$5/mo if you exceed the trial) comfortably covers it. It does not sleep.

## 2. Frontend → Vercel

```bash
npm install -g vercel
cd frontend
vercel link            # first time: creates/links a Vercel project
vercel env add NEXT_PUBLIC_API_URL production
# paste your Railway URL, e.g. https://your-app.up.railway.app
vercel --prod
```

Vercel auto-detects Next.js (Turbopack build works out of the box). Add the same env var for the `preview` and `development` environments too if you want PR previews to hit the live backend:

```bash
vercel env add NEXT_PUBLIC_API_URL preview
vercel env add NEXT_PUBLIC_API_URL development
```

**Cost:** Vercel's Hobby tier is free for this kind of app (single small Next.js site, low traffic) and does not sleep.

## 3. Verify the deployed pair

```bash
curl https://your-app.up.railway.app/health
# → {"ok": true}
```

Then open the Vercel URL in a browser, submit a brief, and confirm a scan completes — the frontend calls `NEXT_PUBLIC_API_URL` directly from the browser, so CORS must allow it. The backend currently allows all origins (`allow_origins=["*"]` in `app/main.py`), which is fine for v1 but worth tightening to the exact Vercel domain once the URL is stable:

```python
# backend/app/main.py
app.add_middleware(CORSMiddleware, allow_origins=["https://your-app.vercel.app"], allow_methods=["*"], allow_headers=["*"])
```

## Notes

- No database, no secrets, no PII storage — there's nothing to put in a `.env` on the backend side beyond what Railway already injects.
- Both platforms redeploy in under ~2 minutes for this size of app.
- If you outgrow Railway's trial credit, Fly.io's free allowance is a similar non-sleeping alternative for the backend with almost the same CLI flow (`fly launch`, `fly deploy`).
