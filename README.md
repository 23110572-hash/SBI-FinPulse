<div align="center">

# 🪙 SBI FinPulse
### Agentic AI for Proactive, Personalised, Consent-Native Digital Engagement

*A bank that reaches out at the right moment — with your permission — instead of waiting for you to log in.*

**Built for the SBI × Global Fintech Fest (GFF) 2026 Hackathon — AI & Emerging Tech track**
**🎯 Problem Statement 3 · Digital Engagement**

`5 AI Agents` · `CrewAI` · `LangGraph` · `Groq Llama 3.3 70B` · `ChromaDB RAG` · `FastAPI` · `Next.js 14` · `PostgreSQL (Neon)`

</div>

---

## 🌐 Live deployment

| Surface | URL |
|---|---|
| **🖥️ Frontend (Vercel)** | https://sbi-fin-pulse-dn42ayt9i-krishna-s-projects07.vercel.app/ |
| **⚙️ Backend API (Render)** | https://sbi-finpulse-api.onrender.com |
| **❤️ API health check** | https://sbi-finpulse-api.onrender.com/api/health |
| **📚 API docs (Swagger)** | https://sbi-finpulse-api.onrender.com/docs |
| **💾 Source (GitHub)** | https://github.com/23110572-hash/SBI-FinPulse |

> **Note on the backend:** it runs on Render's free tier, which spins down after ~15 min of inactivity. The first request after idle may take ~30–60s to cold-start — give it a moment, then it's fast.

---

## 📖 What you'll find in this document

I wrote this so that **anyone** — a judge, a banker, a developer, or a teammate seeing the project for the first time — can understand exactly what FinPulse is, why it matters, and how every piece works. No prior context needed. We'll go from the problem, to the solution, to the architecture, to how the five AI agents think, to how it stays safe and legal, and finally to the business impact in real numbers.

1. [The problem we set out to solve](#1-the-problem-we-set-out-to-solve)
2. [Our solution in one picture](#2-our-solution-in-one-picture)
3. [The 5 AI agents — explained like you're new to this](#3-the-5-ai-agents--explained-like-youre-new-to-this)
4. [How it actually works (the complete workflow)](#4-how-it-actually-works-the-complete-workflow)
5. [System architecture](#5-system-architecture)
6. [How we keep the numbers honest](#6-how-we-keep-the-numbers-honest)
7. [Privacy, security & regulatory readiness](#7-privacy-security--regulatory-readiness)
8. [Business impact — in actual numbers](#8-business-impact--in-actual-numbers)
9. [Technology stack](#9-technology-stack)
10. [Project structure](#10-project-structure)
11. [Cloud development workflow](#11-cloud-development-workflow)
12. [Deployment (Vercel + Render)](#12-deployment-vercel--render)
13. [Environment variables](#13-environment-variables)
14. [Key API endpoints](#14-key-api-endpoints)
15. [Demo script (including the live real-time test)](#15-demo-script-including-the-live-real-time-test)
16. [Why FinPulse wins — mapped to the judging criteria](#16-why-finpulse-wins--mapped-to-the-judging-criteria)

---

## 1. The problem we set out to solve

The hackathon's **Problem Statement 3 (Digital Engagement)** asks for:

> *AI-driven engagement models that proactively interact with customers based on their behaviours, financial patterns and life events.*

Here's the reality today. Banks hold a goldmine of information about how their customers earn, spend, and save — but they engage **reactively** and **generically**:

- A mass SMS blast that ignores what's actually happening in your life.
- A "personalised" offer that's really the same offer everyone got.
- A notification at the wrong time, about the wrong thing.

The result is **banner-blindness** (we ignore everything), **low trust**, and **missed moments that matter** — a salary hike that could become a savings habit, a new baby that means the family needs insurance, a rising rent that signals stress.

Doing the opposite — reaching out at *exactly* the right moment with something genuinely useful — is hard for four real reasons:

| The challenge | Why it's genuinely hard |
|---|---|
| **Proactivity at scale** | SBI has hundreds of millions of customers. No human team can hand-review every message — yet Indian law forbids fully-automated outreach for many products. |
| **Real relevance** | The message must reflect *this* customer's actual behaviour, not a segment average. |
| **Trust & compliance** | Every proactive touch must respect the DPDP Act 2023 (consent), RBI fair-practice rules, and IRDAI/SEBI advertising rules. No misselling. No "guaranteed returns." |
| **Explainability** | Staff and regulators must be able to *see and audit* why the AI sent each message. |

FinPulse is engineered to solve all four at once.

---

## 2. Our solution in one picture

FinPulse is an **agentic engagement layer** that sits on top of the bank's data. Instead of one AI model guessing an offer, a **team of five specialised AI agents** works like a real advisory desk — they study the customer, score their financial health, design a suggestion, compliance-check it, and write it in warm, human language.

A **proactive engine** runs that team automatically (a daily sweep plus real-time triggers), and a **consent + compliance + audit** layer decides whether anything actually reaches the customer.

The product has **two faces**:

| 👤 Customer App (`/customer`) | 🏢 Staff Console (`/staff`) |
|---|---|
| A clean, YONO-style experience: a **financial health score (0–100)**, AI **insights & detected life events**, quick actions, a **bilingual (English/हिंदी) chat** grounded in real SBI knowledge, and a **consent switch the customer fully owns**. Analysis starts automatically — nothing to hunt for. There's also a **Re-analyze** button to refresh on demand. | A control room: watch the five agents **reason live**, see proactive signals as they're detected, **approve or reject** the regulated nudges that need human sign-off, and audit **every** nudge ever sent — with its compliance verdict, delivery status, and timestamps. |

The one-line pitch: **proactive + personalised + consent-first + provably compliant + explainable**, delivered by real email.

---

## 3. The 5 AI agents — explained like you're new to this

Imagine a **five-person expert team** sitting around a table. The customer's financial data comes in one end; a warm, compliant, ready-to-send message comes out the other. Each person does one job well and hands off to the next. Every agent is a real LLM (Groq's Llama 3.3 70B) with real tools, and you can watch each one work, step by step, live in the staff console.

```
  Customer's financial data (accessed only with consent)
            │
            ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ 1️⃣  THE PROFILER  — "What's this customer's situation?"        │
 │     Reads spending patterns, month-over-month trends, and      │
 │     LIFE EVENTS (salary hike, new dependant, big purchase),    │
 │     and spots which products they're missing.                  │
 │     Tools: Transaction Analyzer · Life Event Detector          │
 ├──────────────────────────────────────────────────────────────┤
 │ 2️⃣  THE WELLNESS ADVISOR  — "How financially healthy are they?"│
 │     Scores the customer 0–100 across 5 pillars: Savings,       │
 │     Emergency Fund, Insurance, Investments, Debt. Names the     │
 │     critical gaps and the quick wins.                          │
 │     Tool: Wellness Calculator                                  │
 ├──────────────────────────────────────────────────────────────┤
 │ 3️⃣  THE NUDGE STRATEGIST  — "What should we suggest, and how?"  │
 │     Matches each gap to a REAL SBI product, picks a behavioural │
 │     angle (loss aversion / social proof / etc.), and drafts a  │
 │     short, personalised suggestion.                            │
 │     Tool: SBI Knowledge Search (RAG over real product docs)    │
 ├──────────────────────────────────────────────────────────────┤
 │ 4️⃣  THE COMPLIANCE OFFICER  — "Is this honest and legal?" 🛡️    │
 │     THE GATE. Validates each nudge against RBI / DPDP / IRDAI   │
 │     rules and flags misselling. A rejected nudge is never sent.│
 │     Tools: SBI Knowledge Search · Compliance Checker           │
 ├──────────────────────────────────────────────────────────────┤
 │ 5️⃣  THE CONVERSATION AGENT  — "Now say it like a human."       │
 │     Rewrites the approved nudge into a warm, natural message    │
 │     — and this is the message the customer actually receives.  │
 │     Also powers the live customer chat.                        │
 └──────────────────────────────────────────────────────────────┘
            │
            ▼
   Consent + compliance gated → polished email → customer
```

**Why five agents instead of one big prompt?** Because each step is **specialised** and **auditable**. When a regulator asks *"why did you send this?"*, we can point to the exact agent, its tool output, and its reasoning — not a black box. And critically, the Compliance Officer is an **independent gate**: it can veto the Strategist.

**An honest engineering detail we're proud of:** for the things that *must* be exact — the financial figures, the wellness score, and the final compliance verdict — we don't blindly trust the LLM (language models sometimes drop or mangle numbers). We recompute those **deterministically** in code and make them authoritative, while the agents' reasoning is preserved for transparency. So the AI provides the intelligence and the human tone; deterministic code guarantees the math and the legal gate. (More on this in §6.)

---

## 4. How it actually works (the complete workflow)

There are exactly **three ways** the engine ever runs. Understanding these three removes all the mystery.

### A. On-demand — the customer opens the app
```
Customer logs in
   → Analysis starts automatically (no button to press)
   → The 5 agents run in sequence, streaming live to the staff console
   → Customer sees: Health Score, Insights, Life Events, Quick Actions
   → Customer can chat (bilingual, grounded in real SBI knowledge)
   → Customer can hit "Re-analyze" anytime to refresh
```
This needs **no proactive consent** — it's the customer using their own dashboard, on demand. (Proactive consent governs the bank reaching *out*, not the customer looking *in*.)

### B. The daily sweep — the always-on proactive engine
Once a day (22:00 / 10 PM server time) a scheduled job goes through customers one by one and asks, in order:
```
1. Has this customer CONSENTED to proactive engagement?
      → No  → skip completely (no detection, no AI, no nudge).
2. Is there a NEW signal since the last analysis
   (a salary hike, a new dependant, a rent jump…)?
      → Nothing new → do nothing (we don't re-bill the AI for no reason).
3. Is the last analysis stale (older than ~12 hours)?
      → Fresh → just record the signal.
4. All checks pass → run the 5 agents, generate nudges,
   auto-send the low-risk (Tier 1) ones by email.
```
So the daily sweep is a **smart scheduled check**, not a blind re-run.

### C. The real-time trigger — reacting the moment something happens
There's a webhook: `POST /api/engagement/webhook/transaction`. In a real SBI deployment, the **core-banking system calls this the instant a transaction posts** (e.g., a salary credit or a large purchase). On arrival it records the event, checks consent, and **only for meaningful signals** wakes the agents immediately. A routine ₹200 coffee is recorded but does **not** run the AI.

**An important honesty point — "does it magically know when something happens?"**
No system magically watches every account in real time. Something has to **tell** FinPulse an event occurred. That happens in one of two ways: (1) the bank's transaction system **pushes** the event to the webhook — that's the instant path; or (2) the **next daily sweep catches it**. In this prototype the data is synthetic, so there's no live banking feed pushing events — which is exactly why we include a tool (`tools/ingest_event.py`) that simulates that push so you can see the real-time path end-to-end. The wiring is real and production-ready; in production you simply connect SBI's transaction stream / Account Aggregator to the webhook.

### The guardrails that apply whenever it runs
- **At most one email per customer per 24 hours.** No exceptions.
- **No repeat nudge on the same topic for 30 days.**
- **Regulated products (loans, insurance, mutual funds) never auto-send** — they wait for a human in the staff Review Queue.

### What the staff member does
```
Opens the Staff Console
   → Dashboard: customers analysed, nudges generated, response rate, life events
   → Nudges → Review Queue: approve / reject Tier 2 & Tier 3 nudges
                             (each shows the exact regulation behind it)
   → Nudges → Engagement Log: an audit of EVERY nudge across all tiers
   → Analytics: health-score distribution, nudges by product, top life events
```

---

## 5. System architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                         FRONTEND  (Next.js 14)                          │
│   /customer  → health score, insights, chat, consent control           │
│   /staff     → live agent view, review queue, engagement log, analytics │
│            hosted on Vercel · talks to the backend over HTTPS           │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │  REST + Server-Sent Events (live stream)
┌───────────────────────────────▼───────────────────────────────────────┐
│                          BACKEND  (FastAPI on Render)                    │
│                                                                          │
│   ┌─────────────┐   ┌──────────────┐   ┌───────────────────────────┐    │
│   │ API Routes  │   │  Services    │   │  Agent Crew (CrewAI)      │    │
│   │ customer,   │──▶│ engagement,  │──▶│  Profiler → Wellness →     │    │
│   │ analysis,   │   │ consent,     │   │  Strategist → Compliance → │    │
│   │ nudges,     │   │ delivery,    │   │  Conversation             │    │
│   │ dashboard,  │   │ audit,       │   │  (wrapped by LangGraph     │    │
│   │ consent,    │   │ scheduler    │   │   as a streamable graph)   │    │
│   │ engagement  │   └──────────────┘   └────────────┬──────────────┘    │
│   └─────────────┘                                   │  grounded by RAG  │
│         │                 ┌───────────────┐         ▼                   │
│         │                 │ Data Providers │   ┌──────────┐             │
│         │                 │ synthetic /    │   │ ChromaDB │  SBI / RBI / │
│         │                 │ sbi_sandbox /  │   │ (Cloud)  │  DPDP docs   │
│         │                 │ acct_aggregator│   └──────────┘             │
│         ▼                 └───────┬────────┘                            │
│   ┌──────────────┐        ┌───────▼──────┐      ┌──────────────┐         │
│   │ PostgreSQL   │        │ Groq Llama   │      │ SMTP (email) │         │
│   │ (Neon)       │        │ 3.3 70B      │      │ HTML nudges  │         │
│   └──────────────┘        └──────────────┘      └──────────────┘         │
└──────────────────────────────────────────────────────────────────────────┘
```

- **CrewAI** orchestrates the 5 agents and their tools; each step returns a structured (Pydantic-validated) result.
- **LangGraph** wraps the pipeline as a streamable state machine, so the staff console sees each step live (Server-Sent Events).
- **ChromaDB RAG** grounds the strategist, compliance officer, and chat agent in a **real** SBI products + RBI + DPDP + financial-literacy knowledge base.
- **Pluggable data providers** mean the agents never need to know whether data came from the demo store, the SBI sandbox, or an RBI Account Aggregator — it's a single configuration switch.

---

## 6. How we keep the numbers honest

This is one of the most important design decisions, so it gets its own short section.

LLMs are brilliant at language but **unreliable at copying exact numbers**. If we let the AI transcribe a customer's balance, income, or health score, it sometimes drops or changes them — which would produce a wrong score or a misleading nudge. So FinPulse uses a simple rule: **the AI provides intelligence and tone; deterministic code guarantees the facts.**

- **Customer financials** (balance, income, spending, savings rate, products held) are re-injected from the **source record** after the profiler runs — the AI can't zero them out.
- **The wellness score** is recomputed by a deterministic calculator and made authoritative; the AI's version is only for the live narrative.
- **The compliance verdict** is decided by a deterministic, consent-aware checker. The compliance *agent's* reasoning is preserved and shown to staff, but the deterministic result is what actually gates delivery.
- **The customer-facing message** is the Conversation Agent's polished text, with any mandatory regulatory disclosure auto-appended before sending.

The result: every score is reproducible, every nudge is grounded in real figures, and the legal gate never depends on a model "remembering" to be careful.

---

## 7. Privacy, security & regulatory readiness

Regulatory readiness is a **first-class design goal**, not an afterthought. Five independent layers stand between an AI idea and a customer's inbox.

### 🛡️ Layer 1 — Consent-native (DPDP Act 2023)
Nothing proactive happens without the customer's explicit, **purpose-bound, channel-scoped, time-boxed, revocable** consent. Customers grant or withdraw it themselves from the app. The system reads the **live** consent state — it's never assumed. No consent → the customer is skipped entirely.

### 🛡️ Layer 2 — The compliance gate
A deterministic, consent-aware checker independently flags guaranteed-return language, verifies the mandatory disclosure for each product, and re-checks consent. A nudge with misselling language or without consent is **rejected** and never sent.

### 🛡️ Layer 3 — Risk-tiered human approval
This is the design choice that makes proactive AI **defensible** in Indian banking — because for many products, full automation would be illegal.

| Tier | Products | What happens | Why (the law) |
|---|---|---|---|
| **Tier 1 · Low** | Savings, FD, RD, UPI, Wallet, Digital | ✅ **Auto-send** if compliance approves | RBI Fair Practices Code |
| **Tier 2 · Medium** | Credit cards, personal/home/auto/education loans | 🧑‍💼 **Staff approval** | RBI Digital Lending Direction **DNCR.04** (suitability) |
| **Tier 3 · High** | Mutual funds, insurance, ULIPs, equity | 🧑‍💼 **Staff approval** | **IRDAI** Advertising Code + **SEBI** Investment Advisor Regulations |

Unknown products **default to Tier 2** (fail-safe — never auto-send something we can't classify).

### 🛡️ Layer 4 — Honest delivery + throttling
Approved nudges are sent over **real SMTP email** as a polished, branded HTML message; the status is marked `sent` only when the mail server actually accepts it. Plus: max one email per customer per 24h, and no repeat nudge on the same topic for 30 days.

### 🛡️ Layer 5 — Full audit trail + authentication
**Every** consent change, analysis run, proactive trigger, tier-routing decision, staff action, and delivery attempt is written to a tamper-evident audit log — the regulator-facing accountability trail. Staff routes are protected by a bearer token, with optional per-customer scoping.

### 🔒 Privacy by design
Credentials live only in environment variables, never in the repository. The prototype runs entirely on a **privacy-safe synthetic dataset** — no real PAN, Aadhaar, or account numbers — so the full model is proven end-to-end without ever touching sensitive data.

### 🌐 Data residency & production path
This prototype uses **Groq's API (US-based)** for fast iteration on synthetic data. However, the architecture is **provider-pluggable via LiteLLM** — for SBI production, a **single config change** swaps the endpoint to an **on-premise LLaMA 3.1 70B hosted inside SBI's VPC**. Zero customer PII ever leaves the bank's infrastructure, ensuring full compliance with **DPDP Act 2023 §16 (cross-border transfer)** and **RBI data-localization directives**. The same applies to the rest of the stack: embeddings move to a self-hosted model, ChromaDB to `CHROMA_MODE=local` inside the VPC, and the database to SBI's on-prem / Mumbai-region Postgres — all configuration changes, not rewrites. The five-agent logic, RAG, compliance, consent, and audit run **identically** against the in-country stack.

---

## 8. Business impact — in actual numbers

> **How to read this:** SBI doesn't publish per-customer engagement economics, so this is a **transparent projection model** for a **1-month pilot of 10,00,000 (1 million) consenting, digitally-active customers**. Every figure follows from the stated assumptions, so the model is fully auditable and scales linearly with the cohort. It's illustrative, not a guarantee.

### Assumptions
| Assumption | Value | Basis |
|---|---|---|
| Pilot cohort (consenting, digitally active) | 10,00,000 customers | A realistic YONO sub-segment |
| Customers with a relevant signal / month | 35% → 3,50,000 | Life-event + gap detection rate |
| Nudge cost (email) | ≈ ₹0.05 each | Transactional email is near-free |
| Generic-blast click-through (baseline) | 1.5% | Typical bank mass-outreach |
| Personalised, well-timed click-through | 9% | 5–6× uplift for behaviour-triggered, consented outreach |
| Click → product conversion | 6% | Conservative for a warm, opted-in offer |
| Avg. first-year value per converted product | ₹2,500 | Blended across FD/RD/credit/insurance cross-sell |

### Projected monthly impact (per 1M-customer pilot)
| Metric | Reactive / generic (today) | With FinPulse | Uplift |
|---|---:|---:|---:|
| Relevant customers reached | 3,50,000 | 3,50,000 | — |
| Engaged (clicked) | 5,250 | 31,500 | **6×** |
| Products converted | 315 | 1,890 | **6×** |
| Cross-sell revenue (first-year) | ₹7.9 L | ₹47.3 L | **+₹39.4 L** |
| Outreach cost (email) | ₹17,500 | ₹17,500 | flat |
| **Net monthly gain** | — | — | **≈ ₹47 L** |
| **Annualised (×12)** | — | — | **≈ ₹5.6 Cr** |

### Operational & trust impact
| Metric | Without FinPulse | With FinPulse | Benefit |
|---|---|---|---|
| Nudges needing human review | 100% (or unsafe full-auto) | **~5%** (Tier 2 + 3 only) | Staff focus only where law requires |
| Misselling on auto-sent nudges | High risk | **0** (deterministic gate) | Compliant by construction |
| Time to detect a life event | Days / never | **Minutes** (real-time webhook) | Right moment, every time |
| Auditability of a decision | Partial | **100%** | Regulator-ready |
| Customer control over data | Buried in T&C | **One-tap consent** | DPDP-aligned trust |

> **Manageable staff workload:** by auto-routing 95% of low-risk nudges, FinPulse ensures the **Staff Review Queue only sees the ~5% of high-value, regulated products** (loans, insurance, mutual funds) — keeping Relationship Manager workload manageable and focused on revenue generation rather than rubber-stamping routine savings nudges.

**Why the numbers hold up:** the 5–6× engagement uplift compounds three documented effects — *relevance* (real behaviour), *timing* (a real event), and *trust* (the customer opted in). The ~95% automation rate mirrors the product catalogue (most useful nudges are low-risk and auto-send). And because email is effectively free, almost the entire uplift flows to the bottom line and scales linearly to SBI's full base.

---

## 9. Technology stack

**Backend** — FastAPI (REST + live SSE streaming) · CrewAI + crewai-tools (multi-agent orchestration) · LangGraph (streamable pipeline) · LangChain · **Groq Llama 3.3 70B** (powers all 5 agents; 3 keys rotated for throughput) · LiteLLM · ChromaDB (RAG) · Hugging Face Inference (embeddings) · SQLAlchemy + **PostgreSQL (Neon)** · APScheduler (daily sweep) · httpx.

**Frontend** — Next.js 14 (App Router) · self-hosted fonts via `next/font` (no third-party calls) · vanilla CSS SBI/YONO design system · Framer Motion · Recharts · Lucide React.

---

## 10. Project structure

```
State Bank of India/
├── backend/
│   ├── main.py                  # FastAPI entry (+ /api/health, scheduler lifecycle)
│   ├── agents/                  # The 5-agent crew + tools + risk-tier engine
│   │   ├── crew.py              # 5-step pipeline + deterministic data/score merge
│   │   ├── llms.py              # Groq factory (3-key rotation) + LiteLLM patches
│   │   ├── risk_tier.py         # Single source of truth for Tier 1/2/3 routing
│   │   └── tools/               # transaction analyzer, life-event detector, RAG, wellness, compliance
│   ├── data_providers/          # synthetic / sbi_sandbox / account_aggregator
│   ├── services/                # consent, audit, delivery (HTML email), engagement, scheduler
│   ├── api/                     # routes, schemas, security (auth), store (persistence)
│   ├── graphs/                  # LangGraph engagement graph
│   ├── rag/                     # embeddings, ingest + knowledge_base/*.md
│   ├── database/                # models, connection (Neon), seed
│   ├── tools/                   # ingest_event.py — simulate a real-time core-banking event
│   ├── data/                    # synthetic data generator + JSON
│   └── config/                  # settings (env-driven)
└── frontend/
    └── src/
        ├── app/                 # /, /customer/*, /staff/*
        ├── components/          # common, customer, staff UI
        ├── hooks/               # useCustomer, useAnalysis, useChat, useConsent
        └── lib/                 # api client, constants, utils
```

---

## 11. Cloud development workflow

The repository is cloud-first:

1. Push source changes to GitHub.
2. Vercel builds and deploys `frontend/`.
3. Render builds and deploys `backend/` from `render.yaml`.
4. Neon Postgres and Chroma Cloud remain managed external data services.

Local dependency folders, generated builds, CLI state, caches, and secret files are intentionally excluded from Git. Reproducible cloud builds use `frontend/package-lock.json` and `backend/requirements.txt`.

Administrative data generation, database seeding, and RAG ingestion scripts remain in `backend/`, but they are maintenance operations—not deployment prerequisites. Database seeding is destructive and must only be run intentionally against the correct Neon database.

---

## 12. Deployment (Vercel + Render)

**This project is live:**
- **Frontend (Vercel):** https://sbi-fin-pulse-dn42ayt9i-krishna-s-projects07.vercel.app/
- **Backend (Render):** https://sbi-finpulse-api.onrender.com

How it's wired:

- **Backend → Render**: a `render.yaml` blueprint is included at the repo root — it pins Python 3.12, installs the pinned `requirements.txt`, binds to Render's `$PORT`, and exposes a `/api/health` check. The live service is deployed at `https://sbi-finpulse-api.onrender.com`.
- **Frontend → Vercel**: set the project **Root Directory to `frontend`** and add `NEXT_PUBLIC_API_URL=https://sbi-finpulse-api.onrender.com` so the app talks to the live backend.
- **CORS**: `CORS_ORIGINS` on Render is set to the exact Vercel URL above so the browser can call the API.
- **Scheduler at scale**: the daily sweep is guarded by a Postgres advisory lock so only one worker runs it. For large deployments, run it as a dedicated **Render Cron Job** hitting `POST /api/engagement/scan` instead of inside the web app.

📄 **Full step-by-step guide:** see [`DEPLOYMENT.md`](./DEPLOYMENT.md).

---

## 13. Environment variables

| Group | Keys |
|---|---|
| **Core (required)** | `DATABASE_URL` (Neon), `GROQ_API_KEY`, `HF_TOKEN` |
| **Groq rotation (recommended)** | `GROQ_API_KEY_2`, `GROQ_API_KEY_3` (fall back to key 1 if blank) |
| **Vector store** | `CHROMA_MODE`, `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE` |
| **Data provider** | `DATA_PROVIDER` (`synthetic` / `sbi_sandbox` / `account_aggregator`) + provider creds |
| **Email delivery** | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` |
| **Proactive engine** | `ENABLE_SCHEDULER`, `AUTO_SEND_APPROVED`, `PROACTIVE_CHANNEL`, `DELIVERY_COOLDOWN_HOURS`, `SAME_GAP_COOLDOWN_DAYS` |
| **Auth** | `STAFF_API_TOKEN`, `ENFORCE_CUSTOMER_SCOPE` |
| **Frontend** | `NEXT_PUBLIC_API_URL` |

---

## 14. Key API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/customers` · `/{id}` · `/{id}/transactions` | Customer data (via active data provider) |
| `POST` / `GET` | `/api/analyze/{id}` · `/api/analyze/{id}/stream` | Run the 5-agent crew (sync / live SSE stream) |
| `GET` | `/api/analysis/{id}` · `/api/wellness/{id}` · `/api/insights/{id}` | Stored results |
| `POST` / `GET` | `/api/chat` · `/api/chat/history/{id}` | RAG chat + history |
| `GET` | `/api/nudges` · `/api/nudges/{customer_id}` | Engagement log feed |
| `PUT` | `/api/nudges/{id}/approve` · `/reject` · `/send` | Staff actions on Tier 2/3 nudges |
| `GET` / `POST` | `/api/consent/{id}` · `/grant` · `/revoke` | DPDP consent lifecycle |
| `GET` / `POST` | `/api/engagement/scan` · `/process/{id}` · `/webhook/transaction` · `/audit` | Proactive engine + audit |
| `GET` | `/api/dashboard/stats` · `/activity` · `/analytics` · `/api/health` | Dashboard + readiness |

---

## 15. Demo script (including the live real-time test)

1. **Customer app** → on first visit, the 5-agent crew runs **automatically**. Watch the health score, insights, and life events appear. Hit **Re-analyze** to run it again.
2. Go to **Profile** → **grant proactive-engagement consent** (channel: email).
3. **Trigger a real-time event** (simulating the bank's transaction feed) — from `backend/` with the venv active:
   ```powershell
   .\venv\Scripts\python.exe tools\ingest_event.py --customer CUST_011 --scenario salary_hike --grant-consent --reset-analysis
   ```
   This writes a real transaction, runs all 5 agents, and (for a Tier-1 product) **emails a polished, branded nudge** to the customer.
4. **Staff → Nudges**:
   - **Review Queue** — Tier 2 (credit) & Tier 3 (insurance/MF) nudges wait here, each showing the regulation behind it. Click **Approve & send** (this also emails the customer) or **Reject**.
   - **Engagement Log** — every nudge across all tiers, with compliance verdict, delivery status, and timestamps.
5. **Staff → Analytics** → health-score distribution, nudges by product, top life events, behavioural frames.
6. Check `GET /api/engagement/audit` for the full decision trail.

> Note: only **Tier 1** products auto-email. If the strategist picks insurance/MF/loans (Tier 2/3), the nudge correctly lands in the Review Queue — approve it there to send. That's the compliance design working, not a failure.

---

## 16. Why FinPulse wins — mapped to the judging criteria

| Criterion | How FinPulse delivers |
|---|---|
| **Innovation** | A 5-agent advisory crew with an *independent* compliance gate and risk-tiered human-in-the-loop routing — proactive AI engineered to be legally defensible, not just clever. |
| **Technical Feasibility** | A working end-to-end prototype: live agent streaming, RAG grounding, real branded HTML email, deterministic scoring, and a full audit trail — on a production-grade stack. |
| **Business Potential** | A transparent model projecting **≈ ₹5.6 Cr/year per 1M customers** in cross-sell uplift at near-zero marginal cost. |
| **Scalability** | Email keeps marginal cost near zero; a pluggable data layer connects to the SBI sandbox or Account Aggregator with one config switch; the model scales linearly across SBI's base. |
| **User Experience** | A clean, bilingual (EN/हिं), YONO-style app where analysis just happens — plus a customer-owned, one-tap consent control. |
| **Regulatory Readiness** | Consent-native (DPDP 2023), a deterministic compliance gate, risk-tiered approval aligned to RBI / IRDAI / SEBI, a complete audit trail, and a clear in-country deployment path. |

---

<div align="center">

**FinPulse — proactive engagement that customers trust, and regulators can audit.**

*Built for SBI × GFF 2026 · Problem Statement 3: Digital Engagement*

</div>
