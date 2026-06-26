# 🚀 Deploying SBI FinPulse — Render (backend) + Vercel (frontend)

> **Live deployment**
> - Frontend (Vercel): https://sbi-fin-pulse-dn42ayt9i-krishna-s-projects07.vercel.app/
> - Backend (Render): https://sbi-finpulse-api.onrender.com
> - Health check: https://sbi-finpulse-api.onrender.com/api/health

This guide covers a production-style split deploy:

- **Backend (FastAPI)** → **Render** (web service, reads `render.yaml`)
- **Frontend (Next.js 14)** → **Vercel**
- **Database** → **Neon Postgres** (managed, already used in dev)
- **Vector store** → **Chroma Cloud** (managed — required because Render's disk is ephemeral)

---

## 0. Cloud-first source of truth

GitHub is the source of truth for application code and deployment configuration:

- Render builds the backend from `backend/requirements.txt` and `render.yaml`.
- Vercel builds the frontend from `frontend/package-lock.json`.
- Neon Postgres and Chroma Cloud hold persistent managed data.
- Local dependency folders, build output, CLI state, caches, and `.env` files are never deployed or committed.

The scripts in `backend/database/seed.py` and `backend/rag/ingest.py` are administrative maintenance tools. They are not part of routine deployment. Database seeding is destructive and must only be run intentionally against the correct Neon database.

---

## 1. ⚠️ Rotate your secrets first (important)

Your local `backend/.env` contains **live** credentials (Groq keys, HF token, Neon password, Chroma key, Gmail app password). `.env` is gitignored so it won't be pushed — good. But because these have been shared/handled in plaintext, **rotate them before going public**:

- Groq keys → https://console.groq.com/keys
- Hugging Face token → https://huggingface.co/settings/tokens
- Neon password → Neon console → reset role password
- Chroma Cloud key → Chroma Cloud dashboard
- Gmail app password → Google Account → Security → App passwords

Then set the **new** values as environment variables in Render (never commit them).

---

## 2. Backend → Render

1. Push this repo to GitHub.
2. In Render: **New + → Blueprint**, select the repo. Render detects `render.yaml` at the repo root.
3. When prompted, fill the `sync: false` env vars:

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | your Neon URL (`postgresql://...sslmode=require`) |
   | `GROQ_API_KEY`, `GROQ_API_KEY_2`, `GROQ_API_KEY_3` | your Groq keys |
   | `HF_TOKEN` | your Hugging Face token |
   | `CHROMA_API_KEY`, `CHROMA_TENANT` | Chroma Cloud creds (`CHROMA_DATABASE` defaults to `SBI`) |
   | `CORS_ORIGINS` | your Vercel URL, e.g. `https://sbi-fin-pulse-dn42ayt9i-krishna-s-projects07.vercel.app` |
   | `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Gmail address + app password + display from |
   | `STAFF_API_TOKEN` | optional — set to lock the staff console |

4. Deploy. Render runs `pip install -r requirements.txt` then `uvicorn main:app --host 0.0.0.0 --port $PORT`.
5. Verify: open `https://sbi-finpulse-api.onrender.com/api/health` — channels/data provider should report ready.

> **Free-tier note:** Render free web services spin down after ~15 min idle and cold-start on the next request (first call may take ~30s). The daily 22:00 scheduler only fires while the instance is awake — fine for a demo, upgrade to a paid instance or a Render Cron Job for guaranteed proactive sweeps.

---

## 3. Frontend → Vercel

1. In Vercel: **Add New → Project**, import the same GitHub repo.
2. **Set Root Directory to `frontend`** (Project Settings → General → Root Directory). This is essential — the repo root holds both `backend/` and `frontend/`.
3. Framework preset auto-detects **Next.js** (also pinned in `frontend/vercel.json`).
4. Add an environment variable:

   | Variable | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | your Render backend URL, e.g. `https://sbi-finpulse-api.onrender.com` |

   > `NEXT_PUBLIC_*` vars are baked in at **build time**, so set this **before** the first build (or redeploy after adding it).

5. Deploy. Visit the Vercel URL → landing page → Customer / Staff.

---

## 4. Wire the two together (CORS)

After both are live, make sure the backend allows the frontend origin:

- In Render, `CORS_ORIGINS` must equal your exact Vercel URL (scheme + host, no trailing slash). For multiple origins, comma-separate: `https://app.vercel.app,https://app-git-main.vercel.app`.
- Redeploy the Render service after changing it (env changes trigger a restart).

---

## 5. Post-deploy smoke test

1. `GET https://<render>/api/health` → `200`, channels report.
2. Open the Vercel app → **Customer** → analysis auto-runs (5 agents stream).
3. **Staff → Analytics** → 4 charts populate (score distribution, nudges by category, life events, frames).
4. **Staff → Nudges** → Review Queue + Engagement Log load; Approve/Reject/Send work.
5. Browser devtools → Network: no CORS errors against the Render origin.

---

## 6. What was verified / fixed for deploy

- ✅ Added **`psycopg2-binary`** to `requirements.txt` — it was missing and the Neon `postgresql://` connection would have failed on Render.
- ✅ **Pinned** all dependencies to the known-working versions (reproducible builds).
- ✅ Added **`render.yaml`** (start command binds `$PORT`, health check, env scaffold).
- ✅ Added **`frontend/vercel.json`** + documented the Root Directory + `NEXT_PUBLIC_API_URL` requirement.
- ✅ Frontend production build passes (`next build`, 12 routes).
- ✅ Confirmed no required API key is missing for the running paths (Groq + HF + SMTP + Neon + Chroma are all present; `GEMINI_API_KEY` is unused — Groq powers all 5 agents and chat).
- ✅ Cleaned unused imports in the analytics + nudges pages and fixed an outdated README line.
