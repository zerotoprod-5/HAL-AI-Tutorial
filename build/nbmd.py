"""
Colab-safe design system for the workshop notebooks — a DROP-IN replacement for
nbbuild. Callouts render as an emoji marker + bold label + Markdown blockquote
(no HTML <div>, no inline colour), so they look identical in Google Colab, GitHub
and Jupyter and never depend on colour. Same public API as nbbuild, so a build
script only changes:  `from nbbuild import *`  ->  `from nbmd import *`.

Basic inline tags in the content (<b>, <i>, <code>, <br>, &mdash;, &rarr;) still
render in Colab/GitHub; only the coloured boxes are gone.
"""
import json, os

# Callout markers (match notebook 04's Colab-safe convention)
M_VOCAB, M_DID, M_TURN, M_RECAP = "🟦", "🟩", "🟧", "🟪"
M_WARN, M_IDEA, M_STORY, M_NOTE, M_NEXT = "⚠️", "💡", "📍", "ℹ️", "🟪"

def _q(body):
    return "\n".join("> " + line for line in body.split("\n"))

def _box(marker, label, body):
    head = f"> {marker} **{label}**"
    return head if not body else head + "\n>\n" + _q(body)

# ---- public API (same names/signatures as nbbuild) ------------------------
def banner(kicker, title, subtitle=""):
    tag = f"**{kicker}**" + (f" — {subtitle}" if subtitle else "")
    return f"# {title}\n\n{tag}"

def section(title, n=None):
    return f"## Step {n} · {title}" if n is not None else f"## {title}"

def bigidea(body):  return _box(M_IDEA,  "THE BIG IDEA", body)
def story(body):    return _box(M_STORY, "THE SCENARIO", body)
def vocab(term, body): return _box(M_VOCAB, f"VOCABULARY — {term}", body)
def did(body):      return _box(M_DID,   "WHAT JUST HAPPENED", body)
def turn(body):     return _box(M_TURN,  "YOUR TURN", body)
def note(body):     return _box(M_NOTE,  "NOTE", body)
def watchout(body): return _box(M_WARN,  "WATCH OUT", body)
def nextup(body):   return _box(M_NEXT,  "COMING UP NEXT", body)

def recap(title, bullets):
    return f"> {M_RECAP} **{title.upper()}**\n>\n" + "\n".join(f"> - {b}" for b in bullets)

# A reusable Colab-safe legend (replaces the old coloured LEGEND html blocks)
LEGEND = ("As you scroll you will meet four little callouts: "
          "🟦 a new word, 🟩 what a cell just did, 🟧 something to try, 🟪 the recap.")

# ---- cell constructors / build (identical to nbbuild) ---------------------
def _src(text):
    lines = text.split("\n")
    return [l + "\n" for l in lines[:-1]] + [lines[-1]]

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": _src(text)}

def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": _src(text)}

def build(cells, path, title="Notebook"):
    nb = {"cells": cells, "metadata": {
        "colab": {"name": title, "provenance": [], "toc_visible": True},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"}},
        "nbformat": 4, "nbformat_minor": 5}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"wrote {path}  ({len(cells)} cells)")
    return path
