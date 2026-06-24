"""06 — Risk-Tiered Approval, mapped to Indian regulation."""
from style import (NAVY, GREEN, GREEN_L, AMBER, AMBER_L, RED, RED_L, INK, GREY,
                   GOLD, W_BOLD, W_SEMI, W_MED, FONT_FAMILY,
                   new_canvas, title_block, box, chip, label, footer, save)


def build():
    fig, ax = new_canvas(16, 9)
    title_block(ax, "Compliance", "Risk-Tiered Approval — The Most Automation That's Legal",
                "Low-risk nudges auto-send; regulated products always get a human. Only ~5% reach the staff queue.")

    rows = [
        ("TIER 1", "LOW RISK", GREEN, GREEN_L,
         "Savings · FD · RD · UPI · Wallet · Digital",
         "AUTO-SEND if compliance approves",
         "Defensible under RBI Fair Practices Code", "~95%"),
        ("TIER 2", "MEDIUM RISK", AMBER, AMBER_L,
         "Credit cards · Personal / Home / Auto / Education loans",
         "HELD for staff approval",
         "RBI Digital Lending Direction DNCR.04 (suitability)", "~4%"),
        ("TIER 3", "HIGH RISK", RED, RED_L,
         "Mutual funds · Insurance · ULIPs · Equity",
         "HELD for staff sign-off",
         "IRDAI Advertising Code + SEBI Investment Adviser Regs", "~1%"),
    ]

    y, h = 31, 11
    for t1, t2, c, cl, products, action, reg, pct in rows:
        box(ax, 4, y, 92, h, "", fc=cl, ec=c, lw=1.8)
        # left tier label block
        box(ax, 5.2, y + 1.1, 21, h - 2.2, "", fc=c, ec=c)
        label(ax, 15.7, y + h / 2 + 1.4, t1, fs=14, color="#fff", weight=W_BOLD)
        label(ax, 15.7, y + h / 2 - 2.4, t2, fs=10, color="#fff", weight=W_SEMI)
        # products
        label(ax, 28.5, y + h - 3.0, products, fs=10.8, color=INK, weight=W_BOLD, ha="left")
        # action
        label(ax, 28.5, y + h / 2 - 0.2, "Routing:  " + action, fs=10.2, color=c, weight=W_BOLD, ha="left")
        # regulation
        label(ax, 28.5, y + 2.4, "Why:  " + reg, fs=9.4, color=GREY, weight=W_SEMI, ha="left")
        # volume chip
        chip(ax, 82, y + h / 2 - 1.7, 11, 3.4, pct, fc="#ffffffcc", tc=c, fs=12, weight=W_BOLD)
        y -= (h + 0.8)

    box(ax, 4, 3.0, 92, 3.4, "Unknown products default to Tier 2 — fail-safe: we never auto-send something we can't classify.",
        fc=NAVY, ec=NAVY, tc="#fff", fs=10, weight=W_BOLD)
    footer(ax)
    save(fig, "06_risk_tiers.png")


if __name__ == "__main__":
    build()
