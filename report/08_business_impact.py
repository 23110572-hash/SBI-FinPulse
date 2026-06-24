"""08 — Business Impact in actual numbers."""
from matplotlib.patches import FancyBboxPatch
from style import (NAVY, BLUE, SURFACE, SUBTLE, GOLD, GOLD_L, GREEN, GREEN_L,
                   GREY, GREY_L, INK, LINE, W_BOLD, W_SEMI, W_MED, FONT_FAMILY,
                   new_canvas, title_block, box, label, footer, save)


def stat_card(ax, x, y, w, h, big, small, color):
    box(ax, x, y, w, h, "", fc="#fff", ec=color, lw=2)
    label(ax, x + w / 2, y + h - 4.6, big, fs=24, color=color, weight=W_BOLD)
    ax.text(x + w / 2, y + 3.2, small, ha="center", va="center", color=GREY,
            fontsize=10.5, weight=W_BOLD, family=FONT_FAMILY, linespacing=1.4)


def hbar(ax, x, y, h, frac, color, value_txt, name_txt, maxw):
    # track
    ax.add_patch(FancyBboxPatch((x, y), maxw, h, boxstyle="round,pad=0.02,rounding_size=0.8",
                                facecolor=SUBTLE, edgecolor="none"))
    ax.add_patch(FancyBboxPatch((x, y), max(2.2, maxw * frac), h,
                                boxstyle="round,pad=0.02,rounding_size=0.8",
                                facecolor=color, edgecolor="none"))
    label(ax, x - 1.5, y + h / 2, name_txt, fs=11.5, color=INK, weight=W_BOLD, ha="right")
    label(ax, x + max(2.2, maxw * frac) + 2, y + h / 2, value_txt, fs=12,
          color=color, weight=W_BOLD, ha="left")


def build():
    fig, ax = new_canvas(16, 9)
    title_block(ax, "Business Impact", "Projected Impact — 1-Month Pilot of 1 Million Customers",
                "A transparent model: every figure follows from stated assumptions and scales linearly.")

    # ---- headline stat cards ----
    cards = [
        ("~Rs.5.6 Cr", "annual cross-sell\nuplift / 1M users", GREEN),
        ("6x", "engagement vs\ngeneric blasts", NAVY),
        ("~5%", "of nudges need\nhuman review", GOLD),
        ("0", "misselling on\nauto-sent nudges", BLUE),
    ]
    w, gap = 21.5, 2.0
    x = 4
    for big, small, c in cards:
        stat_card(ax, x, 31, w, 11, big, small, c)
        x += w + gap

    # ---- revenue comparison bars ----
    label(ax, 4, 26.5, "First-year cross-sell revenue (per month)", fs=12,
          color=NAVY, weight=W_BOLD, ha="left")
    maxw = 58
    hbar(ax, 26, 19.5, 4.2, 7.9 / 47.3, GREY_L, "Rs.7.9 L", "Reactive / generic", maxw)
    hbar(ax, 26, 13.0, 4.2, 1.0, GREEN, "Rs.47.3 L  (+Rs.39.4 L)", "With FinPulse", maxw)

    # ---- assumptions strip ----
    box(ax, 4, 3.2, 92, 6.4, "", fc=SUBTLE, ec=BLUE, lw=1.2)
    label(ax, 6, 7.6, "Key assumptions", fs=10.8, color=NAVY, weight=W_BOLD, ha="left")
    label(ax, 6, 4.9,
          "35% have a relevant signal/month · click-through 1.5% -> 9% (5-6x) · conversion 6% · Rs.2,500 first-year value/product · email cost ~Rs.0.05.",
          fs=9.3, color=GREY, weight=W_SEMI, ha="left")

    footer(ax)
    save(fig, "08_business_impact.png")


if __name__ == "__main__":
    build()
