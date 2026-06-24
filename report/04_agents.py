"""04 — The 5-Agent Pipeline (block diagram)."""
from matplotlib.patches import Circle
from style import (NAVY, BLUE, SURFACE, SUBTLE, GOLD, GOLD_L, GREEN, GREEN_L,
                   RED, RED_L, INK, GREY, W_BOLD, W_SEMI, W_MED, FONT_FAMILY,
                   new_canvas, title_block, box, arrow, label, footer, save)


def build():
    fig, ax = new_canvas(16, 9)
    title_block(ax, "The Crew", "Five Specialised AI Agents",
                "Each agent does one job, then hands off. Every step streams live and is auditable.")

    # ---- input / output rails ----
    box(ax, 4, 38.5, 40, 4, "Customer data (accessed only with consent)",
        fc=NAVY, ec=NAVY, tc="#fff", fs=10.5, weight=W_BOLD)
    box(ax, 56, 38.5, 40, 4, "Gated by consent + compliance, then emailed",
        fc=GREEN, ec=GREEN, tc="#fff", fs=10.5, weight=W_BOLD)

    agents = [
        ("1", "Customer\nProfiler", "Spending patterns,\ntrends & life events;\nproduct gaps",
         "Transaction Analyzer\nLife Event Detector", SURFACE, NAVY),
        ("2", "Wellness\nAdvisor", "0-100 health score\nacross 5 pillars;\ngaps & quick wins",
         "Wellness Calculator", SURFACE, NAVY),
        ("3", "Nudge\nStrategist", "Best SBI product +\nbehavioural frame\n+ timing", "SBI Knowledge\nSearch (RAG)", GOLD_L, GOLD),
        ("4", "Compliance\nOfficer", "RBI / DPDP / IRDAI\ncheck; blocks\nmisselling - THE GATE",
         "Compliance Checker\nRAG", RED_L, RED),
        ("5", "Conversation\nAgent", "Warm, bilingual,\ncustomer-ready text\n(this is what's sent)",
         "SBI Knowledge\nSearch", GREEN_L, GREEN),
    ]

    n = len(agents)
    x0, gap = 4.0, 2.0
    w = (92 - gap * (n - 1)) / n
    y, h = 14.5, 21
    for i, (num, name, desc, tools, fc, ec) in enumerate(agents):
        x = x0 + i * (w + gap)
        box(ax, x, y, w, h, "", fc=fc, ec=ec, lw=1.8)
        cx = x + w / 2
        ax.add_patch(Circle((cx, y + h - 3.0), 1.7, color=ec, zorder=3))
        ax.text(cx, y + h - 3.0, num, ha="center", va="center", color="#fff",
                fontsize=12.5, weight=W_BOLD, family=FONT_FAMILY, zorder=4)
        ax.text(cx, y + h - 7.6, name, ha="center", va="center", color=ec,
                fontsize=12.5, weight=W_BOLD, family=FONT_FAMILY, linespacing=1.25)
        ax.text(cx, y + h - 13.4, desc, ha="center", va="center", color=INK,
                fontsize=10.4, weight=W_BOLD, family=FONT_FAMILY, linespacing=1.42)
        ax.text(cx, y + 2.6, tools, ha="center", va="center", color=GREY,
                fontsize=9.0, weight=W_BOLD, family=FONT_FAMILY, linespacing=1.3)
        if i < n - 1:
            arrow(ax, (x + w + 0.15, y + h / 2), (x + w + gap - 0.15, y + h / 2),
                  color=GREY, lw=2.4, mut=15)

    arrow(ax, (12, 38.5), (12, 35.7), color=NAVY, lw=2.4)
    arrow(ax, (88, 35.7), (88, 38.5), color=GREEN, lw=2.4)

    # honest-by-design note
    box(ax, 4, 4, 92, 7.2, "", fc=SUBTLE, ec=BLUE, lw=1.3)
    label(ax, 6, 9.2, "Honest by design", fs=11.5, color=NAVY, weight=W_BOLD, ha="left")
    label(ax, 6, 6.4,
          "AI provides the intelligence and human tone. For facts that must be exact — balances, the wellness score, the legal verdict —\n"
          "deterministic code recomputes and is authoritative, while the agents' reasoning is preserved for full transparency.",
          fs=9.5, color=GREY, weight=W_SEMI, ha="left")

    footer(ax)
    save(fig, "04_agents.png")


if __name__ == "__main__":
    build()
