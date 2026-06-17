"""
Shared notebook builder + design system for the HAL Predictive AI training set.

Every notebook imports these helpers so the visual language (callout boxes,
banners, vocabulary cards) is identical across all six notebooks. Think of this
as the "design system as code".

Usage in a notebook-build script:

    from nbbuild import *
    cells = [
        md(banner("Notebook 0", "What is Predictive AI?", "Generic equipment demo")),
        md(vocab("Dataset", "A dataset is just a table ...")),
        code("import pandas as pd\n..."),
        md(did("We just loaded 300 past machines ...")),
        md(turn("Change n=300 to n=50 and re-run ...")),
        md(recap("What we learned", ["a", "b", "c"])),
    ]
    build(cells, "/Users/flam/Desktop/HAL_AI/notebooks/00_intro.ipynb",
          title="Predictive AI 00 - Intro")
"""
import json

# ----------------------------------------------------------------------------
# Palette  (defense / engineering, professional, emoji-free)
# ----------------------------------------------------------------------------
INK      = "#1f2d3d"   # banner slate
TEAL     = "#0b6e7a"   # vocabulary
GREEN    = "#2e7d32"   # what just happened
AMBER    = "#b26a00"   # your turn
PURPLE   = "#5b2a86"   # recap
SLATE    = "#445566"   # note / caveat
RED      = "#9c2b2b"   # watch out

FONT = ("font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,"
        "Helvetica,Arial,sans-serif;")

def _box(accent, bg, label, body, label_color=None):
    label_color = label_color or accent
    head = (f"<div style=\"font-weight:700;letter-spacing:.4px;"
            f"color:{label_color};font-size:13px;margin-bottom:6px;"
            f"text-transform:uppercase;\">{label}</div>") if label else ""
    return (f"<div style=\"{FONT}border-left:5px solid {accent};background:{bg};"
            f"padding:14px 18px;border-radius:6px;margin:10px 0;color:#222;"
            f"line-height:1.55;font-size:15px;\">{head}{body}</div>")

# ----------------------------------------------------------------------------
# Callout components
# ----------------------------------------------------------------------------
def banner(kicker, title, subtitle=""):
    """Big title banner at the top of a notebook."""
    sub = (f"<div style=\"color:#c7d2dd;font-size:15px;margin-top:8px;\">"
           f"{subtitle}</div>") if subtitle else ""
    return (f"<div style=\"{FONT}background:{INK};border-radius:10px;"
            f"padding:28px 30px;color:#fff;\">"
            f"<div style=\"text-transform:uppercase;letter-spacing:2px;"
            f"font-size:13px;color:#7fb6c4;font-weight:700;\">{kicker}</div>"
            f"<div style=\"font-size:30px;font-weight:800;margin-top:6px;"
            f"line-height:1.2;\">{title}</div>{sub}</div>")

def section(title, n=None):
    """A styled section divider used between steps."""
    tag = (f"<span style=\"background:{TEAL};color:#fff;border-radius:20px;"
           f"padding:2px 12px;font-size:14px;margin-right:10px;\">"
           f"Step {n}</span>") if n is not None else ""
    return (f"<div style=\"{FONT}border-bottom:3px solid {INK};"
            f"padding-bottom:8px;margin:22px 0 6px 0;font-size:22px;"
            f"font-weight:800;color:{INK};\">{tag}{title}</div>")

def bigidea(body):
    return _box(INK, "#eef2f6", "The big idea", body)

def story(body):
    return _box(INK, "#eef2f6", "The scenario", body)

def vocab(term, body):
    return _box(TEAL, "#e6f4f6", f"Vocabulary &nbsp;—&nbsp; {term}", body)

def did(body):
    return _box(GREEN, "#eaf5ea", "What just happened", body)

def turn(body):
    return _box(AMBER, "#fdf2e0", "Your turn", body)

def note(body):
    return _box(SLATE, "#eef1f4", "Note", body)

def watchout(body):
    return _box(RED, "#f8ecec", "Watch out", body)

def recap(title, bullets):
    items = "".join(
        f"<li style=\"margin:5px 0;\">{b}</li>" for b in bullets)
    body = f"<ul style=\"margin:6px 0 0 0;padding-left:20px;\">{items}</ul>"
    return _box(PURPLE, "#f2eaf7", title, body)

def nextup(body):
    return _box(PURPLE, "#f2eaf7", "Coming up next", body)

# ----------------------------------------------------------------------------
# Cell constructors
# ----------------------------------------------------------------------------
def _src(text):
    # nbformat wants source as a list of lines, each keeping its newline.
    lines = text.split("\n")
    return [l + "\n" for l in lines[:-1]] + [lines[-1]]

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": _src(text)}

def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": _src(text)}

# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------
def build(cells, path, title="Notebook"):
    nb = {
        "cells": cells,
        "metadata": {
            "colab": {"name": title, "provenance": [], "toc_visible": True},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    with open(path, "w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"wrote {path}  ({len(cells)} cells)")
    return path
