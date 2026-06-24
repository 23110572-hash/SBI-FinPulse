"""03 — Complete System Architecture."""
from style import (NAVY, NAVY2, BLUE, SURFACE, SUBTLE, GOLD, GREEN, GREEN_L,
                   AMBER_L, INK, GREY, LINE, W_BOLD, W_SEMI, W_MED, FONT_FAMILY,
                   new_canvas, title_block, box, arrow, label, footer, save)


def build():
    fig, ax = new_canvas(16, 10)   # ylim = 62.5
    title_block(ax, "Architecture", "End-to-End System Architecture",
                "A Next.js frontend on Vercel drives a FastAPI backend that orchestrates the agents, RAG and data stores.")

    # ---------- FRONTEND band ----------
    box(ax, 4, 43, 92, 6.2, "", fc=SUBTLE, ec=BLUE, lw=1.6)
    label(ax, 6.5, 47.8, "FRONTEND  ·  Next.js 14  ·  Vercel", fs=12, color=NAVY, weight=W_BOLD, ha="left")
    box(ax, 7, 43.6, 42, 3.4, "Customer App — score, insights, chat, consent",
        fc="#fff", ec=BLUE, tc=NAVY, fs=10, weight=W_BOLD)
    box(ax, 51, 43.6, 42, 3.4, "Staff Console — live agents, queue, audit, analytics",
        fc="#fff", ec=BLUE, tc=NAVY, fs=10, weight=W_BOLD)

    arrow(ax, (50, 43), (50, 40.5), color=GREY, lw=2.4)
    label(ax, 50, 41.6, "HTTPS  ·  REST + Server-Sent Events (live stream)", fs=9.6,
          color=GREY, weight=W_BOLD)

    # ---------- BACKEND band ----------
    box(ax, 4, 7, 92, 33, "", fc="#FBFBFE", ec=NAVY, lw=1.8)
    label(ax, 6.5, 38.0, "BACKEND  ·  FastAPI  ·  Render", fs=12, color=NAVY, weight=W_BOLD, ha="left")

    # Row 1 — routes, services, crew
    box(ax, 7, 26, 24, 9, "customer · analysis · chat\nnudges · dashboard\nconsent · engagement",
        fc=SURFACE, ec=BLUE, tc=NAVY, fs=9.6, weight=W_SEMI, title="API Routes", title_fs=11.5, title_color=NAVY)
    box(ax, 33, 26, 24, 9, "engagement · consent\ndelivery · audit\nscheduler",
        fc=SURFACE, ec=BLUE, tc=NAVY, fs=9.6, weight=W_SEMI, title="Services", title_fs=11.5, title_color=NAVY)
    box(ax, 59, 26, 33, 9, "Profiler · Wellness · Strategist\nCompliance · Conversation\n(LangGraph streamable graph)",
        fc=NAVY, ec=NAVY, tc="#E8EAF6", fs=9.6, weight=W_SEMI, title="Agent Crew  ·  CrewAI", title_fs=11.5, title_color="#fff")
    arrow(ax, (31, 30.5), (33, 30.5), color=GREY, lw=2)
    arrow(ax, (57, 30.5), (59, 30.5), color=GREY, lw=2)

    # Row 2 — providers, RAG, LLM
    box(ax, 7, 15, 24, 8.5, "synthetic · sbi_sandbox\naccount_aggregator",
        fc=AMBER_L, ec=GOLD, tc=INK, fs=9.6, weight=W_SEMI, title="Data Providers", title_fs=11, title_color="#8a5a00")
    box(ax, 59, 15, 15.5, 8.5, "SBI · RBI · DPDP\nknowledge base",
        fc=GREEN_L, ec=GREEN, tc=INK, fs=9.4, weight=W_SEMI, title="ChromaDB RAG", title_fs=10.5, title_color=GREEN)
    box(ax, 76.5, 15, 15.5, 8.5, "Groq Llama\n3.3 70B (x3 keys)",
        fc="#EDE7F6", ec="#7E57C2", tc=INK, fs=9.4, weight=W_SEMI, title="LLM", title_fs=10.5, title_color="#5E35B1")
    arrow(ax, (19, 26), (19, 23.5), color=GREY, lw=2)
    arrow(ax, (70, 26), (67, 23.5), color=GREY, lw=1.8, connection="arc3,rad=0.15")
    arrow(ax, (80, 26), (84, 23.5), color=GREY, lw=1.8, connection="arc3,rad=-0.15")

    # Row 3 — data layer + governance
    box(ax, 7, 8.5, 24, 4.6, "PostgreSQL (Neon) — data + audit",
        fc="#fff", ec=NAVY, tc=GREY, fs=9.4, weight=W_BOLD)
    box(ax, 33, 8.5, 24, 4.6, "SMTP — branded HTML email",
        fc="#fff", ec=NAVY, tc=GREY, fs=9.4, weight=W_BOLD)
    box(ax, 59, 8.5, 33, 4.6, "Consent · Compliance · Risk-Tier · Audit",
        fc=GOLD, ec=GOLD, tc=NAVY, fs=10, weight=W_BOLD)

    footer(ax)
    save(fig, "03_architecture.png")


if __name__ == "__main__":
    build()
