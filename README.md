# SBI FinPulse
### Agentic AI for Proactive, Personalized, Consent-First Digital Engagement

A bank that reaches out at the right moment, with your permission, instead of waiting for you to log in.

Built for the SBI x Global Fintech Fest (GFF) 2026 Hackathon, AI and Emerging Tech track. Problem Statement 3: Digital Engagement.

Stack at a glance: 5 AI Agents, CrewAI, LangGraph, Groq Llama 3.3 70B, ChromaDB RAG, FastAPI, Next.js 14, PostgreSQL (Neon).

---

## Live deployment

| Surface | URL |
|---|---|
| Frontend | https://sbi-fin-pulse-dn42ayt9i-krishna-s-projects07.vercel.app/ |
| API docs | https://sbi-finpulse-api.onrender.com/docs |
| Source (GitHub) | https://github.com/23110572-hash/SBI-FinPulse |

A note on the backend: it runs on Render's free tier, which spins down after about 15 minutes of inactivity. The first request after it has been idle can take 30 to 60 seconds to wake up. Give it a moment and it is fast after that.

---

## What you will find in this document

I wrote this to make you understand exactly what FinPulse is, why it matters, and how every piece works. You do not need any prior context. We will go from the problem, to the solution, to the architecture, to how the five AI agents think, to how it stays safe and legal, and finally to the business impact in real numbers.

1. [The problem we set out to solve](#1-the-problem-we-set-out-to-solve)
2. [Our solution in one picture](#2-our-solution-in-one-picture)
3. [The five AI agents explained simply](#3-the-five-ai-agents-explained-simply)
4. [How it actually works, the complete workflow](#4-how-it-actually-works-the-complete-workflow)
5. [System architecture](#5-system-architecture)
6. [How we keep the numbers honest](#6-how-we-keep-the-numbers-honest)
7. [Privacy, security and regulatory readiness](#7-privacy-security-and-regulatory-readiness)
8. [Business impact in real numbers](#8-business-impact-in-real-numbers)
9. [Technology stack](#9-technology-stack)
10. [Project structure](#10-project-structure)
11. [Why FinPulse fits the judging criteria](#11-why-finpulse-fits-the-judging-criteria)

---

## 1. The problem we set out to solve

Problem Statement 3 (Digital Engagement) asks for AI driven engagement models that proactively interact with customers based on their behavior, financial patterns and life events.

Here is the reality today. Banks hold a goldmine of information about how their customers earn, spend and save, but they still engage reactively and generically:

- A mass SMS blast that ignores what is actually happening in your life.
- A "personalized" offer that is really the same offer everyone got.
- A notification at the wrong time, about the wrong thing.

The result is banner blindness, where we ignore everything, along with low trust and missed moments that matter. A salary hike that could become a savings habit, a new baby that means the family needs insurance, a rising rent that signals stress, all of it passes by unnoticed.

Doing the opposite, reaching out at exactly the right moment with something genuinely useful, is hard for four real reasons:

| The challenge | Why it is genuinely hard |
|---|---|
| Proactivity at scale | SBI has hundreds of millions of customers. No human team can hand review every message, yet Indian law restricts fully automated outreach for many products. |
| Real relevance | The message must reflect this customer's actual behavior, not a segment average. |
| Trust and compliance | Every proactive touch must respect the DPDP Act 2023 (consent), RBI fair practice rules, and IRDAI and SEBI advertising rules. No misselling, and no "guaranteed returns." |
| Explainability | Staff and regulators must be able to see and audit why the AI sent each message. |

I engineered FinPulse to solve all four at once.

---

## 2. Our solution in one picture

FinPulse is an agentic engagement layer that sits on top of the bank's data. Instead of one AI model guessing an offer, a team of five specialized AI agents works like a real advisory desk. They study the customer, score their financial health, design a suggestion, compliance check it, and write it in warm, human language.

A proactive engine runs that team automatically, with a daily sweep plus real-time triggers, and a consent, compliance and audit layer decides whether anything actually reaches the customer.

The product has two faces:

| Customer App (`/customer`) | Staff Console (`/staff`) |
|---|---|
| A clean, YONO style experience: a financial health score from 0 to 100, AI insights and detected life events, quick actions, a bilingual (English and Hindi) chat grounded in real SBI knowledge, and a consent switch the customer fully owns. Analysis starts automatically, so there is nothing to hunt for. There is also a Re-analyze button to refresh on demand. | A control room: watch the five agents reason live, see proactive signals as they are detected, approve or reject the regulated nudges that need human sign off, and audit every nudge ever sent, with its compliance verdict, delivery status and timestamps. |

The one line pitch: proactive, personalized, consent-first, provably compliant and explainable, delivered by real email.

---

## 3. The five AI agents explained simply

Picture a five person expert team sitting around a table. The customer's financial data comes in one end, and a warm, compliant, ready to send message comes out the other. Each person does one job well and hands off to the next. Every agent is a real LLM (Groq's Llama 3.3 70B) with real tools, and you can watch each one work, step by step, live in the staff console.

```
  Customer's financial data (accessed only with consent)
            |
            v
 +--------------------------------------------------------------+
 | 1. THE PROFILER   "What is this customer's situation?"        |
 |    Reads spending patterns, month over month trends, and      |
 |    life events (salary hike, new dependant, big purchase),    |
 |    and spots which products they are missing.                 |
 |    Tools: Transaction Analyzer, Life Event Detector           |
 +--------------------------------------------------------------+
 | 2. THE WELLNESS ADVISOR   "How financially healthy are they?" |
 |    Scores the customer 0 to 100 across 5 pillars: Savings,    |
 |    Emergency Fund, Insurance, Investments, Debt. Names the    |
 |    critical gaps and the quick wins.                          |
 |    Tool: Wellness Calculator                                  |
 +--------------------------------------------------------------+
 | 3. THE NUDGE STRATEGIST   "What should we suggest, and how?"  |
 |    Matches each gap to a real SBI product, picks a behavioral |
 |    angle (loss aversion, social proof, and so on), and drafts |
 |    a short, personalized suggestion.                          |
 |    Tool: SBI Knowledge Search (RAG over real product docs)    |
 +--------------------------------------------------------------+
 | 4. THE COMPLIANCE OFFICER   "Is this honest and legal?"       |
 |    The gate. Validates each nudge against RBI, DPDP and IRDAI |
 |    rules and flags misselling. A rejected nudge is never sent.|
 |    Tools: SBI Knowledge Search, Compliance Checker            |
 +--------------------------------------------------------------+
 | 5. THE CONVERSATION AGENT   "Now say it like a human."        |
 |    Rewrites the approved nudge into a warm, natural message,  |
 |    and this is the message the customer actually receives.    |
 |    Also powers the live customer chat.                        |
 +--------------------------------------------------------------+
            |
            v
   Consent and compliance gated, polished email, customer
```

Why five agents instead of one big prompt? Because each step is specialized and auditable. When a regulator asks why we sent a message, we can point to the exact agent, its tool output and its reasoning, rather than a black box. And critically, the Compliance Officer is an independent gate that can veto the Strategist.

There is one engineering detail I am genuinely proud of. For the things that must be exact, the financial figures, the wellness score and the final compliance verdict, we do not blindly trust the LLM, because language models sometimes drop or mangle numbers. We recompute those deterministically in code and make them authoritative, while the agents' reasoning is preserved for transparency. So the AI provides the intelligence and the human tone, and deterministic code guarantees the math and the legal gate. There is more on this in section 6.

---

## 4. How it actually works, the complete workflow

There are exactly three ways the engine ever runs. Once you understand these three, the rest is simple.

### A. On demand, the customer opens the app
```
Customer logs in
   -> Analysis starts automatically (no button to press)
   -> The 5 agents run in sequence, streaming live to the staff console
   -> Customer sees: Health Score, Insights, Life Events, Quick Actions
   -> Customer can chat (bilingual, grounded in real SBI knowledge)
   -> Customer can hit "Re-analyze" anytime to refresh
```
This needs no proactive consent, because it is the customer using their own dashboard, on demand. Proactive consent governs the bank reaching out, not the customer looking in.

### B. The daily sweep, the always on proactive engine
Once a day (22:00, or 10 PM server time) a scheduled job goes through customers one by one and asks, in order:
```
1. Has this customer consented to proactive engagement?
      -> No  -> skip completely (no detection, no AI, no nudge).
2. Is there a new signal since the last analysis
   (a salary hike, a new dependant, a rent jump)?
      -> Nothing new -> do nothing (we do not re-bill the AI for no reason).
3. Is the last analysis stale (older than about 12 hours)?
      -> Fresh -> just record the signal.
4. All checks pass -> run the 5 agents, generate nudges,
   auto-send the low risk (Tier 1) ones by email.
```
So the daily sweep is a smart scheduled check, not a blind re-run.

### C. The real-time trigger, reacting the moment something happens
There is a webhook: `POST /api/engagement/webhook/transaction`. In a real SBI deployment, the core banking system calls this the instant a transaction posts, for example a salary credit or a large purchase. On arrival it records the event, checks consent, and only for meaningful signals wakes the agents immediately. A routine 200 rupee coffee is recorded but does not run the AI.

One honest point worth making: does it magically know when something happens? No system magically watches every account in real time. Something has to tell FinPulse that an event occurred. That happens in one of two ways. Either the bank's transaction system pushes the event to the webhook, which is the instant path, or the next daily sweep catches it. In this prototype the data is synthetic, so there is no live banking feed pushing events, which is exactly why we include a tool (`tools/ingest_event.py`) that simulates that push so you can see the real-time path end to end. The wiring is real and production ready. In production you simply connect SBI's transaction stream or Account Aggregator to the webhook.

### The guardrails that apply whenever it runs
- At most one email per customer per 24 hours. No exceptions.
- No repeat nudge on the same topic for 30 days.
- Regulated products (loans, insurance, mutual funds) never auto-send. They wait for a human in the staff Review Queue.

### What the staff member does
```
Opens the Staff Console
   -> Dashboard: customers analyzed, nudges generated, response rate, life events
   -> Nudges > Review Queue: approve or reject Tier 2 and Tier 3 nudges
                             (each shows the exact regulation behind it)
   -> Nudges > Engagement Log: an audit of every nudge across all tiers
   -> Analytics: health score distribution, nudges by product, top life events
```

---

## 5. System architecture

```
+-------------------------------------------------------------------------+
|                         FRONTEND  (Next.js 14)                          |
|   /customer  -> health score, insights, chat, consent control           |
|   /staff     -> live agent view, review queue, engagement log, charts   |
|            hosted on Vercel, talks to the backend over HTTPS            |
+-------------------------------+---------------------------------------+
                                |  REST + Server-Sent Events (live stream)
+-------------------------------v---------------------------------------+
|                          BACKEND  (FastAPI on Render)                   |
|                                                                         |
|   +-------------+   +--------------+   +---------------------------+    |
|   | API Routes  |   |  Services    |   |  Agent Crew (CrewAI)      |    |
|   | customer,   |-->| engagement,  |-->|  Profiler > Wellness >     |   |
|   | analysis,   |   | consent,     |   |  Strategist > Compliance > |   |
|   | nudges,     |   | delivery,    |   |  Conversation             |    |
|   | dashboard,  |   | audit,       |   |  (wrapped by LangGraph     |   |
|   | consent,    |   | scheduler    |   |   as a streamable graph)   |   |
|   | engagement  |   +--------------+   +------------+--------------+    |
|   +-------------+                                   |  grounded by RAG  |
|         |                 +---------------+         v                   |
|         |                 | Data Providers|   +----------+              |
|         |                 | synthetic /   |   | ChromaDB |  SBI / RBI / |
|         |                 | sbi_sandbox / |   | (Cloud)  |  DPDP docs   |
|         |                 | acct_aggregator|  +----------+              |
|         v                 +-------+-------+                             |
|   +--------------+        +-------v------+      +--------------+        |
|   | PostgreSQL   |        | Groq Llama   |      | SMTP (email) |        |
|   | (Neon)       |        | 3.3 70B      |      | HTML nudges  |        | 
|   +--------------+        +--------------+      +--------------+        |
+-------------------------------------------------------------------------+
```

- CrewAI orchestrates the 5 agents and their tools, and each step returns a structured, Pydantic validated result.
- LangGraph wraps the pipeline as a streamable state machine, so the staff console sees each step live over Server-Sent Events.
- ChromaDB RAG grounds the strategist, the compliance officer and the chat agent in a real knowledge base of SBI products plus RBI, DPDP and financial literacy material.
- Pluggable data providers mean the agents never need to know whether data came from the demo store, the SBI sandbox, or an RBI Account Aggregator. It is a single configuration switch.

---

## 6. How we keep the numbers honest

This is one of the most important design decisions, so it gets its own short section.

LLMs are brilliant at language but unreliable at copying exact numbers. If we let the AI transcribe a customer's balance, income or health score, it sometimes drops or changes them, which would produce a wrong score or a misleading nudge. So FinPulse follows a simple rule: the AI provides intelligence and tone, and deterministic code guarantees the facts.

- Customer financials (balance, income, spending, savings rate, products held) are re-injected from the source record after the profiler runs, so the AI cannot zero them out.
- The wellness score is recomputed by a deterministic calculator and made authoritative. The AI's version is only for the live narrative.
- The compliance verdict is decided by a deterministic, consent aware checker. The compliance agent's reasoning is preserved and shown to staff, but the deterministic result is what actually gates delivery.
- The customer facing message is the Conversation Agent's polished text, with any mandatory regulatory disclosure auto-appended before sending.

The result is that every score is reproducible, every nudge is grounded in real figures, and the legal gate never depends on a model remembering to be careful.

---

## 7. Privacy, security and regulatory readiness

I treated regulatory readiness as a first class design goal, not an afterthought. Five independent layers stand between an AI idea and a customer's inbox.

### Layer 1, consent first (DPDP Act 2023)
Nothing proactive happens without the customer's explicit, purpose bound, channel scoped, time boxed and revocable consent. Customers grant or withdraw it themselves from the app. The system reads the live consent state and never assumes it. No consent means the customer is skipped entirely.

### Layer 2, the compliance gate
A deterministic, consent aware checker independently flags guaranteed return language, verifies the mandatory disclosure for each product, and re-checks consent. A nudge with misselling language, or without consent, is rejected and never sent.

### Layer 3, risk tiered human approval
This is the design choice that makes proactive AI defensible in Indian banking, because for many products full automation would be illegal.

| Tier | Products | What happens | Why (the law) |
|---|---|---|---|
| Tier 1, Low | Savings, FD, RD, UPI, Wallet, Digital | Auto-send if compliance approves | RBI Fair Practices Code |
| Tier 2, Medium | Credit cards, personal, home, auto and education loans | Staff approval | RBI Digital Lending Direction (suitability) |
| Tier 3, High | Mutual funds, insurance, ULIPs, equity | Staff approval | IRDAI Advertising Code and SEBI Investment Adviser Regulations |

Unknown products default to Tier 2. This is a fail safe, so we never auto-send something we cannot classify.

### Layer 4, honest delivery and throttling
Approved nudges go out over real SMTP email as a polished, branded HTML message, and the status is marked sent only when the mail server actually accepts it. On top of that: at most one email per customer per 24 hours, and no repeat nudge on the same topic for 30 days.

### Layer 5, full audit trail and authentication
Every consent change, analysis run, proactive trigger, tier routing decision, staff action and delivery attempt is written to a tamper evident audit log. This is the regulator facing accountability trail. Staff routes are protected by a bearer token, with optional per customer scoping.

### Privacy by design
Credentials live only in environment variables, never in the repository. The prototype runs entirely on a privacy safe synthetic dataset, with no real PAN, Aadhaar or account numbers, so the full model is proven end to end without ever touching sensitive data.

### Data residency and the production path
This prototype uses Groq's API, which is US based, for fast iteration on synthetic data. The architecture is provider pluggable via LiteLLM, so for SBI production a single configuration change swaps the endpoint to an on-premise Llama 3.1 70B hosted inside SBI's VPC. No customer PII ever leaves the bank's infrastructure, which keeps us aligned with the DPDP Act 2023 cross border transfer provisions and RBI data localization directives. The same applies to the rest of the stack: embeddings move to a self hosted model, ChromaDB to `CHROMA_MODE=local` inside the VPC, and the database to SBI's on-premise or Mumbai region Postgres. These are configuration changes, not rewrites. The five agent logic, RAG, compliance, consent and audit all run identically against the in country stack.

---

## 8. Business impact in real numbers

How to read this: SBI does not publish per customer engagement economics, so this is a transparent projection model for a one month pilot of 1,000,000 (10 lakh) consenting, digitally active customers. Every figure follows from the stated assumptions, so the model is fully auditable and scales linearly with the cohort. It is illustrative, not a guarantee.

### Assumptions
| Assumption | Value | Basis |
|---|---|---|
| Pilot cohort (consenting, digitally active) | 1,000,000 customers | A realistic YONO sub-segment |
| Customers with a relevant signal per month | 35% (350,000) | Life event and gap detection rate |
| Nudge cost (email) | about 0.05 rupees each | Transactional email is near free |
| Generic blast click-through (baseline) | 1.5% | Typical bank mass outreach |
| Personalized, well timed click-through | 9% | 5 to 6x uplift for behavior triggered, consented outreach |
| Click to product conversion | 6% | Conservative for a warm, opted in offer |
| Average first year value per converted product | 2,500 rupees | Blended across FD, RD, credit and insurance cross-sell |

### Projected monthly impact (per 1M customer pilot)
| Metric | Reactive / generic (today) | With FinPulse | Uplift |
|---|---:|---:|---:|
| Relevant customers reached | 350,000 | 350,000 | same |
| Engaged (clicked) | 5,250 | 31,500 | 6x |
| Products converted | 315 | 1,890 | 6x |
| Cross-sell revenue (first year) | 7.9 L | 47.3 L | +39.4 L |
| Outreach cost (email) | 17,500 | 17,500 | flat |
| Net monthly gain | | | about 39 L rupees |
| Annualized (12 months) | | | about 4.7 Cr rupees |

The net monthly gain is the cross-sell uplift over the reactive baseline (about 47.3 L minus 7.9 L), which is roughly 39 L rupees a month after the negligible email cost, and about 4.7 Cr rupees a year. These are the honest, uplift based figures, not gross revenue.

### Operational and trust impact
| Metric | Without FinPulse | With FinPulse | Benefit |
|---|---|---|---|
| Nudges needing human review | 100% (or unsafe full auto) | about 5% (Tier 2 and 3 only) | Staff focus only where the law requires |
| Misselling on auto-sent nudges | High risk | 0 (deterministic gate) | Compliant by construction |
| Time to detect a life event | Days, or never | Minutes (real-time webhook) | Right moment, every time |
| Auditability of a decision | Partial | 100% | Regulator ready |
| Customer control over data | Buried in terms and conditions | One-tap consent | DPDP aligned trust |

A point on staff workload: by auto routing about 95% of low risk nudges, FinPulse makes sure the Staff Review Queue only sees the roughly 5% of high value, regulated products such as loans, insurance and mutual funds. That keeps relationship manager workload manageable and focused on revenue rather than rubber stamping routine savings nudges.

Why the numbers hold up: the 5 to 6x engagement uplift compounds three well understood effects, relevance (real behavior), timing (a real event) and trust (the customer opted in). The roughly 95% automation rate mirrors the product catalog, since most useful nudges are low risk and auto-send. And because email is effectively free, almost the entire uplift flows to the bottom line and scales linearly to SBI's full base.

---

## 9. Technology stack

Backend: FastAPI (REST plus live SSE streaming), CrewAI and crewai-tools (multi agent orchestration), LangGraph (streamable pipeline), LangChain, Groq Llama 3.3 70B (powers all 5 agents), LiteLLM, ChromaDB (RAG), Hugging Face Inference (embeddings), SQLAlchemy with PostgreSQL (Neon), APScheduler (daily sweep), and httpx.

Frontend: Next.js 14 (App Router), self hosted fonts via `next/font` (no third party calls), a vanilla CSS SBI and YONO design system, Framer Motion, Recharts, and Lucide React.

---

## 10. Project structure

```
State Bank of India/
  backend/
    main.py                  FastAPI entry (plus /api/health, scheduler lifecycle)
    agents/                  The 5 agent crew, tools and risk tier engine
      crew.py                5 step pipeline plus deterministic data and score merge
      llms.py                Groq factory (3 key rotation) plus LiteLLM patches
      risk_tier.py           Single source of truth for Tier 1/2/3 routing
      tools/                 transaction analyzer, life event detector, RAG, wellness, compliance
    data_providers/          synthetic / sbi_sandbox / account_aggregator
    services/                consent, audit, delivery (HTML email), engagement, scheduler
    api/                     routes, schemas, security (auth), store (persistence)
    graphs/                  LangGraph engagement graph
    rag/                     embeddings, ingest plus knowledge_base/*.md
    database/                models, connection (Neon), seed
    tools/                   ingest_event.py, simulate a real-time core banking event
    data/                    synthetic data generator plus JSON
    config/                  settings (env driven)
  frontend/
    src/
      app/                   /, /customer/*, /staff/*
      components/            common, customer, staff UI
      hooks/                 useCustomer, useAnalysis, useChat, useConsent
      lib/                   api client, constants, utils
  report/                    executive report generator plus architecture diagrams
```

---
## 11. Why FinPulse fits the judging criteria

| Criterion | How FinPulse delivers |
|---|---|
| Innovation | A 5 agent advisory crew with an independent compliance gate and risk tiered human in the loop routing, so proactive AI is engineered to be legally defensible, not just clever. |
| Technical feasibility | A working end to end prototype: live agent streaming, RAG grounding, real branded HTML email, deterministic scoring and a full audit trail, on a production grade stack. |
| Business potential | A transparent model projecting about 4.7 Cr rupees a year per 1M customers in cross-sell uplift at near zero marginal cost. |
| Scalability | Email keeps marginal cost near zero, a pluggable data layer connects to the SBI sandbox or Account Aggregator with one config switch, and the model scales linearly across SBI's base. |
| User experience | A clean, bilingual (English and Hindi), YONO style app where analysis just happens, plus a customer owned, one-tap consent control. |
| Regulatory readiness | Consent first (DPDP 2023), a deterministic compliance gate, risk tiered approval aligned to RBI, IRDAI and SEBI, a complete audit trail, and a clear in country deployment path. |

FinPulse is proactive engagement that customers trust, and that regulators can audit.

Built for SBI x GFF 2026, Problem Statement 3: Digital Engagement.
