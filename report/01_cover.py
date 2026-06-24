"""01 — Executive summary slide."""
from style import (NAVY, BLUE, SURFACE, SUBTLE, GOLD, GOLD_L, GREEN, GREEN_L,
                   INK, GREY, W_BOLD, W_SEMI, W_MED, FONT_FAMILY,
                   new_canvas, title_block, box, chip, label, footer, save)


def build():
    fig, ax = new_canvas(16, 9)
    title_block(ax, "Executive Summary", "What is SBI FinPulse?",
                "An AI powered engagement platform that helps SBI deliver timely, personalized and compliant financial guidance.")

    # one-line definition band (manual line breaks so it never overflows)
    box(ax, 4, 36.5, 92, 6,
        "FinPulse proactively identifies customer needs, detects key life events,\n and delivers personalized, compliance approved financial recommendations.",
        fc=NAVY, ec=NAVY, tc="#fff", fs=11.5, weight=W_BOLD)

    # four pillar cards
    pillars = [
        ("PROACTIVE", "Engages customers at the \nright moment based on real life\n financial events and behavior changes.", GOLD, GOLD_L),
        ("PERSONALISED", "Tailors recommendations using\n each customer's financial\n behavior, goals and life stage.", BLUE, SUBTLE),
        ("CONSENT FIRST", "Customer controlled,\n DPDP compliant engagement.\n No consent, No action.", GREEN, GREEN_L),
        ("COMPLIANT", "Human oversight and regulatory\n checks ensure recommendations\n remain safe, compliant and auditable.", NAVY, SURFACE),
    ]
    w, gap = 21.8, 1.6
    x = 4
    for head, desc, c, cl in pillars:
        box(ax, x, 20.5, w, 13.5, "", fc=cl, ec=c, lw=1.8)
        label(ax, x + w / 2, 31.0, head, fs=12.5, color=c, weight=W_BOLD)
        ax.text(x + w / 2, 25.0, desc, ha="center", va="center", color=INK,
                fontsize=9.4, weight=W_BOLD, family=FONT_FAMILY, linespacing=1.5)
        x += w + gap

    # delivers chips (fixed width so the row always fits)
    label(ax, 4, 16.6, "WHAT IT DELIVERS :", fs=11, color=GOLD, weight=W_BOLD, ha="left")
    facts = ["Financial Health score 0-100", "Branded email nudges", "Staff review queue", "Compliance Audit Trial"]
    cw, cg = 22, 1.3
    x = 4
    for f in facts:
        chip(ax, x, 10.8, cw, 4.0, f, fc=SURFACE, tc=NAVY, fs=10.5, weight=W_BOLD)
        x += cw + cg

    footer(ax)
    save(fig, "01_cover.png")


if __name__ == "__main__":
    build()
