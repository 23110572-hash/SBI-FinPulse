"""02 — The Problem vs The Solution."""
from style import (NAVY, BLUE, GOLD, GREEN, GREEN_L, RED, RED_L, INK, GREY,
                   W_BOLD, W_SEMI, W_MED, FONT_FAMILY,
                   new_canvas, title_block, box, arrow, label, footer, save)


def build():
    fig, ax = new_canvas(16, 9)
    title_block(ax, "Why FinPulse", "From a Reactive Bank to a Proactive Companion",
                "Banks hold rich data but engage generically and too late. FinPulse fixes timing, relevance and trust.")

    # panel bounds
    panel_top, panel_bottom = 42, 6
    ph = panel_top - panel_bottom

    # ---- LEFT: the problem ----
    box(ax, 4, panel_bottom, 42, ph, "", fc=RED_L, ec="#EBB6B6", lw=1.5)
    label(ax, 25, panel_top - 2.8, "TODAY  ·  REACTIVE & GENERIC", fs=12, color=RED, weight=W_BOLD)
    problems = [
        ("Wrong timing", "Mass blasts that ignore real life events"),
        ("No relevance", "One-size-fits-all offers, banner blindness"),
        ("Low trust", "No consent, no transparency, feels like spam"),
        ("Missed moments", "Salary hikes, new baby, under-insurance ignored"),
    ]
    y = panel_top - 6.2
    for h, d in problems:
        box(ax, 6.5, y - 6.4, 37, 6.4, d, fc="#fff", ec="#EBB6B6", tc=INK, fs=10.2,
            weight=W_BOLD, title=h, title_fs=11.5, title_color=RED)
        y -= 7.4

    # ---- center arrow ----
    arrow(ax, (46.8, 24), (53.2, 24), color=GOLD, lw=3.4, mut=26)
    label(ax, 50, 27, "FinPulse", fs=11, color=GOLD, weight=W_BOLD)

    # ---- RIGHT: the solution ----
    box(ax, 54, panel_bottom, 42, ph, "", fc=GREEN_L, ec="#B7DCBA", lw=1.5)
    label(ax, 75, panel_top - 2.8, "WITH FINPULSE  ·  PROACTIVE & PERSONAL", fs=11.5, color=GREEN, weight=W_BOLD)
    solutions = [
        ("Right moment", "Daily sweep + real-time event triggers"),
        ("Truly personal", "5 agents reason over this customer's data"),
        ("Consent-first", "DPDP-aligned, customer-owned consent"),
        ("Provably compliant", "Deterministic gate + risk-tiered sign-off"),
    ]
    y = panel_top - 6.2
    for h, d in solutions:
        box(ax, 56.5, y - 6.4, 37, 6.4, d, fc="#fff", ec="#B7DCBA", tc=INK, fs=10.2,
            weight=W_BOLD, title=h, title_fs=11.5, title_color=GREEN)
        y -= 7.4

    footer(ax)
    save(fig, "02_problem_solution.png")


if __name__ == "__main__":
    build()
