"""07 — Privacy, Security & Compliance: five gates before an email sends."""
from style import (NAVY, BLUE, SURFACE, SUBTLE, GOLD, GREEN, GREEN_L, INK, GREY,
                   W_BOLD, W_SEMI, W_MED, FONT_FAMILY,
                   new_canvas, title_block, box, arrow, label, footer, save)


def build():
    fig, ax = new_canvas(16, 9)
    title_block(ax, "Trust", "Five Gates Between an AI Idea and a Customer's Inbox",
                "Regulatory readiness is built into the architecture, not bolted on afterwards.")

    layers = [
        ("1", "Consent (DPDP 2023)", "Purpose-bound, channel-scoped,\ntime-boxed, revocable. No consent\nmeans the customer is skipped."),
        ("2", "Compliance Gate", "Deterministic checker flags\nmisselling, verifies disclosures,\nre-checks consent. Can reject."),
        ("3", "Risk-Tiered Approval", "Tier 1 auto-sends; Tier 2 & 3\n(loans, insurance, MF) wait for\na human, per RBI/IRDAI/SEBI."),
        ("4", "Honest Delivery", "Real SMTP; 'sent' only if accepted.\nMax 1 email / 24h; no repeat\ntopic for 30 days."),
        ("5", "Audit + Auth", "Every action logged for regulators.\nStaff bearer-token; optional\nper-customer scoping."),
    ]

    n = len(layers)
    x0, gap = 4.0, 1.6
    w = (92 - gap * (n - 1)) / n
    y, h = 16, 24
    for i, (num, name, desc) in enumerate(layers):
        x = x0 + i * (w + gap)
        # darker -> lighter ramp
        shade = ["#1A237E", "#283593", "#303F9F", "#3949AB", "#3F51B5"][i]
        box(ax, x, y, w, h, "", fc=shade, ec=shade)
        cx = x + w / 2
        label(ax, cx, y + h - 3.4, "GATE " + num, fs=10.5, color=GOLD, weight=W_BOLD)
        label(ax, cx, y + h - 8.2, name, fs=11.5, color="#fff", weight=W_BOLD)
        ax.text(cx, y + h - 15.8, desc, ha="center", va="center", color="#D6DAF5",
                fontsize=9.6, weight=W_SEMI, family=FONT_FAMILY, linespacing=1.5)
        if i < n - 1:
            arrow(ax, (x + w + 0.1, y + h / 2), (x + w + gap - 0.1, y + h / 2),
                  color=GOLD, lw=2.4, mut=14)

    box(ax, 4, 4, 92, 8, "", fc=GREEN_L, ec=GREEN, lw=1.4)
    label(ax, 6, 9.4, "Data residency & production path", fs=11.5, color=GREEN, weight=W_BOLD, ha="left")
    label(ax, 6, 6.2,
          "Prototype uses Groq (US) on synthetic data. The LiteLLM layer makes inference provider-pluggable: one config change points it at an\n"
          "on-premise LLaMA 3.1 70B inside SBI's VPC. Zero PII leaves the bank — full DPDP §16 + RBI data-localization compliance.",
          fs=9.3, color=GREY, weight=W_SEMI, ha="left")

    footer(ax)
    save(fig, "07_security_layers.png")


if __name__ == "__main__":
    build()
