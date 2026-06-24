"""Shared styling + drawing helpers for the SBI FinPulse report diagrams.

Every diagram script imports this so all images share one visual language
(SBI palette, Poppins typography, rounded blocks, arrows, badges).

Run any diagram with the backend venv so matplotlib is available, e.g.:
    .\backend\venv\Scripts\python.exe report\01_architecture.py
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless render
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
FONT_DIR = ROOT / "fonts"
IMG_DIR = ROOT / "images"
IMG_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------------------------
# SBI brand palette
# --------------------------------------------------------------------------
NAVY = "#1A237E"      # primary SBI blue
NAVY2 = "#283593"
BLUE = "#3F51B5"      # light blue
BLUE_L = "#5C6BC0"
SURFACE = "#E8EAF6"   # pale blue surface
SUBTLE = "#F5F6FF"
GOLD = "#C49B2A"
GOLD_L = "#F5E6B8"
GREEN = "#2E7D32"
GREEN_L = "#E8F5E9"
AMBER = "#F57F17"
AMBER_L = "#FFF8E1"
RED = "#C62828"
RED_L = "#FFEBEE"
INK = "#1A1A2E"
GREY = "#6B6B85"
GREY_L = "#8A8AA3"
LINE = "#D8D9E6"
BG = "#FFFFFF"
CANVAS = "#F4F5FB"


# --------------------------------------------------------------------------
# Fonts — register Poppins, fall back to default if missing
# --------------------------------------------------------------------------
def _register_fonts() -> str:
    family = "DejaVu Sans"
    if FONT_DIR.exists():
        for ttf in FONT_DIR.glob("Poppins-*.ttf"):
            try:
                fm.fontManager.addfont(str(ttf))
            except Exception:
                pass
        # confirm Poppins is now known to matplotlib
        names = {f.name for f in fm.fontManager.ttflist}
        if "Poppins" in names:
            family = "Poppins"
    plt.rcParams["font.family"] = family
    plt.rcParams["axes.unicode_minus"] = False
    return family


FONT_FAMILY = _register_fonts()
# Poppins weight aliases (matplotlib maps these to the registered faces)
W_BOLD = "bold"
W_SEMI = "semibold"
W_MED = "medium"
W_REG = "normal"


# --------------------------------------------------------------------------
# Canvas helpers
# --------------------------------------------------------------------------
def new_canvas(w=16, h=9, bg=BG):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100 * h / w)
    ax.axis("off")
    return fig, ax


def title_block(ax, kicker, title, subtitle=None, x=4, y=None):
    """Top-left kicker + bold title + optional subtitle."""
    top = ax.get_ylim()[1]
    y = top - 3.5 if y is None else y
    ax.text(x, y, kicker.upper(), fontsize=11.5, color=GOLD, weight=W_BOLD,
            family=FONT_FAMILY, va="top")
    ax.text(x, y - 3.0, title, fontsize=22, color=NAVY, weight=W_BOLD,
            family=FONT_FAMILY, va="top")
    if subtitle:
        ax.text(x, y - 7.2, subtitle, fontsize=11.5, color=GREY, weight=W_MED,
                family=FONT_FAMILY, va="top")
    return y


def box(ax, x, y, w, h, text="", *, fc=BG, ec=LINE, tc=INK, fs=12,
        weight=W_BOLD, lw=1.4, rounding=0.025, align="center",
        title=None, title_fs=None, title_color=None, pad_top=0):
    """Rounded rectangle with centered (or titled) text. (x,y) = bottom-left."""
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={rounding * min(w, h) * 8}",
        linewidth=lw, edgecolor=ec, facecolor=fc, mutation_aspect=1)
    ax.add_patch(patch)
    cx, cy = x + w / 2, y + h / 2
    if title:
        ax.text(cx, y + h - h * 0.26 - pad_top, title, ha="center", va="center",
                fontsize=title_fs or (fs + 1.5), color=title_color or tc,
                weight=W_BOLD, family=FONT_FAMILY)
        if text:
            ax.text(cx, y + h * 0.33, text, ha="center", va="center",
                    fontsize=fs, color=tc, weight=weight, family=FONT_FAMILY,
                    linespacing=1.45)
    elif text:
        ha = {"center": "center", "left": "left"}[align]
        tx = cx if align == "center" else x + w * 0.08
        ax.text(tx, cy, text, ha=ha, va="center", fontsize=fs, color=tc,
                weight=weight, family=FONT_FAMILY, linespacing=1.45)
    return (cx, cy)


def chip(ax, x, y, w, h, text, *, fc=SURFACE, tc=NAVY, fs=10.5, weight=W_SEMI):
    """Small pill / badge."""
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=1.2",
                           linewidth=0, facecolor=fc)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, weight=weight, family=FONT_FAMILY)


def arrow(ax, p0, p1, *, color=BLUE, lw=2.2, style="-|>", mut=18,
          connection="arc3,rad=0", ls="-"):
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=mut,
                        linewidth=lw, color=color, connectionstyle=connection,
                        linestyle=ls, zorder=1)
    ax.add_patch(a)


def label(ax, x, y, text, *, fs=10.5, color=GREY, weight=W_MED, ha="center",
          va="center", rot=0):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=color, weight=weight,
            family=FONT_FAMILY, rotation=rot)


def footer(ax, text="SBI FinPulse · Agentic AI for Digital Engagement · GFF 2026"):
    ax.text(50, 1.5, text, ha="center", va="center", fontsize=9.5,
            color=GREY_L, weight=W_MED, family=FONT_FAMILY)


def save(fig, name):
    out = IMG_DIR / name
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor(),
                pad_inches=0.25)
    plt.close(fig)
    print(f"  saved {out.relative_to(ROOT)}")
    return out
