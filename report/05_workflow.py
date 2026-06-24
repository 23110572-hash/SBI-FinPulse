"""05 — End-to-end working flow: the three ways the engine runs."""
from style import (NAVY, BLUE, SURFACE, SUBTLE, GOLD, GOLD_L, GREEN, GREEN_L,
                   AMBER_L, RED, INK, GREY, W_BOLD, W_SEMI, W_MED, FONT_FAMILY,
                   new_canvas, title_block, box, chip, arrow, label, footer, save)


def column(ax, x, w, header, hcolor, steps):
    chip(ax, x, 40, w, 3.6, header, fc=hcolor, tc="#fff", fs=11, weight=W_BOLD)
    y, h, gap = 33.5, 6.8, 1.5
    centers = []
    for txt, fc, ec, tc in steps:
        box(ax, x, y, w, h, txt, fc=fc, ec=ec, tc=tc, fs=11.5, weight=W_BOLD, lw=1.4)
        centers.append((x + w / 2, y))
        y -= (h + gap)
    for i in range(len(centers) - 1):
        cx, by = centers[i]
        arrow(ax, (cx, by), (cx, centers[i + 1][1] + h), color=GREY, lw=2, mut=13)


def build():
    fig, ax = new_canvas(16, 9)
    title_block(ax, "Working Flow", "Three Ways the Engine Runs",
                "On-demand for the customer; a daily sweep; and instant reaction to a pushed event.")

    w = 28
    column(ax, 4, w, "A · ON-DEMAND (no consent needed)", NAVY, [
        ("Customer logs in", SURFACE, NAVY, INK),
        ("5 agents auto-run", SUBTLE, BLUE, INK),
        ("Score, insights, chat shown", SUBTLE, BLUE, INK),
        ("'Re-analyze' anytime", SUBTLE, BLUE, INK),
    ])
    column(ax, 36, w, "B · DAILY SWEEP (10 PM)", GOLD, [
        ("Consent? No, skip entirely", AMBER_L, GOLD, INK),
        ("New signal since last run?", AMBER_L, GOLD, INK),
        ("Analysis stale (>12h)?", AMBER_L, GOLD, INK),
        ("Run crew, auto-send Tier 1", GOLD_L, GOLD, INK),
    ])
    column(ax, 68, w, "C · REAL-TIME (pushed event)", GREEN, [
        ("Bank pushes a transaction", GREEN_L, GREEN, INK),
        ("Consent + material signal?", GREEN_L, GREEN, INK),
        ("Run the crew immediately", GREEN_L, GREEN, INK),
        ("Email now / queue for review", GREEN_L, GREEN, INK),
    ])

    # guardrails bar
    box(ax, 4, 3, 92, 4.2, "", fc=NAVY, ec=NAVY)
    label(ax, 6.5, 5.1, "GUARDRAILS", fs=10.5, color=GOLD, weight=W_BOLD, ha="left")
    label(ax, 27, 5.1, "Max 1 email / customer / 24h", fs=10, color="#fff", weight=W_BOLD)
    label(ax, 55, 5.1, "No repeat topic for 30 days", fs=10, color="#fff", weight=W_BOLD)
    label(ax, 82, 5.1, "Tier 2 / 3 always need a human", fs=10, color="#fff", weight=W_BOLD)

    footer(ax)
    save(fig, "05_workflow.png")


if __name__ == "__main__":
    build()
