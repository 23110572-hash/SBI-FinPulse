"""09 — Prototype today vs Production (in-country) path."""
from style import (NAVY, BLUE, SURFACE, SUBTLE, GOLD, GREEN, GREEN_L, AMBER_L,
                   INK, GREY, W_BOLD, W_SEMI, W_MED, FONT_FAMILY,
                   new_canvas, title_block, box, chip, arrow, label, footer, save)


def build():
    fig, ax = new_canvas(16, 9)
    title_block(ax, "Production Path", "In-Country Ready — Configuration, Not a Rewrite",
                "The agents, RAG, compliance, consent and audit run identically; only the endpoints change.")

    # column headers
    chip(ax, 30, 39, 31, 3.8, "PROTOTYPE (TODAY)", fc=AMBER_L, tc="#8a5a00", fs=11, weight=W_BOLD)
    chip(ax, 64, 39, 32, 3.8, "SBI PRODUCTION (IN-COUNTRY)", fc=GREEN_L, tc=GREEN, fs=11, weight=W_BOLD)

    rows = [
        ("LLM inference", "Groq API (US)", "On-prem LLaMA 3.1 70B in SBI VPC"),
        ("Embeddings", "Hugging Face (US)", "Self-hosted model in the VPC"),
        ("Vector store", "Chroma Cloud", "Chroma local inside the VPC"),
        ("Database", "Neon Postgres", "SBI on-prem / Mumbai-region RDS"),
        ("Email", "Gmail SMTP", "SBI outbound mail gateway"),
    ]
    y, h, step = 33, 4.8, 5.8
    for layer, proto, prod in rows:
        box(ax, 4, y, 24, h, layer, fc=NAVY, ec=NAVY, tc="#fff", fs=10.8, weight=W_BOLD)
        box(ax, 30, y, 31, h, proto, fc=AMBER_L, ec=GOLD, tc=INK, fs=10.2, weight=W_BOLD)
        box(ax, 64, y, 32, h, prod, fc=GREEN_L, ec=GREEN, tc=INK, fs=10.2, weight=W_BOLD)
        arrow(ax, (61.4, y + h / 2), (63.8, y + h / 2), color=GREEN, lw=2, mut=13)
        y -= step

    # bottom note
    box(ax, 4, 3.2, 92, 5.8, "", fc=SUBTLE, ec=BLUE, lw=1.3)
    label(ax, 6, 7.4, "Why a CISO can say yes", fs=11.2, color=NAVY, weight=W_BOLD, ha="left")
    label(ax, 6, 4.6,
          "LiteLLM makes inference provider-pluggable — one config change swaps the US endpoint for an on-prem model. Zero customer PII\n"
          "leaves the bank, satisfying DPDP Act 2023 §16 (cross-border transfer) and RBI data-localization directives.",
          fs=9.4, color=GREY, weight=W_SEMI, ha="left")

    footer(ax)
    save(fig, "09_data_residency.png")


if __name__ == "__main__":
    build()
