"""
Light-theme chart variants for the PRINT reference guide (reference_guide.html / the PDF),
for the FOUR text & speech sessions. Dark ink on a transparent (white-page) background so the
charts read on paper — the print counterpart of the dark deck figures in
build/make_figs_textspeech.py. Numbers mirror the notebooks' honest results.

Writes ../figs/*_light.svg. Run with a python that has matplotlib + sklearn:
    python3 build/make_print_figs_textspeech.py
"""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

INK, TEAL, AMBER, GREEN, RED, GRID = "#1c2630", "#0b6e7a", "#b26a00", "#2e7d32", "#b3433a", "#d7dee5"
MUTED = "#56657a"
plt.rcParams.update({"svg.fonttype": "path", "font.size": 13, "font.family": "sans-serif",
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": "#9fb0bd", "axes.linewidth": 1.1})
FIG = os.path.join(os.path.dirname(__file__), "..", "figs")
WHITE_TEAL = LinearSegmentedColormap.from_list("wt", ["#ffffff", "#cfe6ea", "#5aa9b4", "#0b6e7a"])

def base(ax):
    ax.set_facecolor("none")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.tick_params(length=0); ax.grid(alpha=.5, color=GRID, linewidth=.8)
def save(fig, name): fig.savefig(os.path.join(FIG, name), transparent=True, bbox_inches="tight"); plt.close(fig)
rng = np.random.default_rng(42)

# 1 ── SESSION 1 · top URGENT clue-words (what the text model keyed on) ───────
words = ["crack", "smoke", "fire", "grounded", "fuel leak", "structural", "spar", "burning"]
weight = np.array([1.92, 1.74, 1.66, 1.51, 1.33, 1.08, 0.92, 0.81])
order = np.argsort(weight)
fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.barh(np.array(words)[order], weight[order], color=TEAL, edgecolor="white", height=.66)
ax.set_xlabel("How strongly the word points to URGENT")
base(ax); ax.grid(axis="y", alpha=0); fig.tight_layout(); save(fig, "cluewords_light.svg")

# 2 ── SESSION 1 · the accuracy trap, as a tiny bar pair ──────────────────────
labels = ["Always-\"routine\"\nshortcut", "The real\nmodel"]
acc = np.array([0.85, 0.90]); recall = np.array([0.0, 0.95])
x = np.arange(2); w = 0.38
fig, ax = plt.subplots(figsize=(7.0, 4.2))
ax.bar(x - w/2, acc, w, color="#9fb0bd", edgecolor="white", label="Accuracy")
ax.bar(x + w/2, recall, w, color=TEAL, edgecolor="white", label="URGENT recall")
for xi, a, r in zip(x, acc, recall):
    ax.text(xi - w/2, a + .015, f"{a:.0%}", ha="center", color=MUTED, fontsize=11)
    ax.text(xi + w/2, r + .015, f"{r:.0%}", ha="center", color=TEAL, fontsize=11)
ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylim(0, 1.06); ax.set_ylabel("Score")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2, frameon=False, fontsize=10.5)
base(ax); ax.grid(axis="x", alpha=0); fig.tight_layout(); save(fig, "accuracytrap_light.svg")

# 3 ── SESSION 2 · recurring-fault similarity heatmap (same fault, 5 wordings) ─
phrases = [
    "hydraulic pressure low on main gear",      # chronic A
    "display flickers on startup",
    "low hyd pressure, main landing gear",       # chronic A reworded
    "cabin light intermittent fault",
    "main gear hydraulic pressure dropping",     # chronic A reworded
    "tyre wear within limits",
]
S = cosine_similarity(TfidfVectorizer().fit_transform(phrases))
fig, ax = plt.subplots(figsize=(5.6, 5.0))
im = ax.imshow(S, cmap=WHITE_TEAL, vmin=0, vmax=1)
ax.set_xticks(range(6)); ax.set_yticks(range(6))
ax.set_xticklabels([f"#{i+1}" for i in range(6)]); ax.set_yticklabels([f"#{i+1}" for i in range(6)])
for i in range(6):
    for j in range(6):
        ax.text(j, i, f"{S[i,j]:.2f}", ha="center", va="center", fontsize=9,
                color="white" if S[i, j] > 0.55 else MUTED)
ax.set_title("Snags #1, #3, #5 are the same fault, worded differently", fontsize=12, color=INK, pad=10)
cb = fig.colorbar(im, ax=ax, fraction=.046, pad=.04); cb.outline.set_visible(False)
cb.ax.tick_params(length=0); ax.tick_params(length=0)
fig.tight_layout(); save(fig, "cosine_heatmap_light.svg")

# 4 ── SESSION 2 · predict downtime HOURS (regression: predicted vs actual) ────
n = 90
actual = rng.uniform(1, 12, n)
pred = actual + rng.normal(0, 1.5, n)
fig, ax = plt.subplots(figsize=(7.0, 4.6))
lim = [0, 13]
ax.plot(lim, lim, color=AMBER, lw=2.4, ls="--", zorder=4, label="Perfect prediction")
ax.scatter(actual, pred, c=TEAL, edgecolors="white", linewidth=.6, s=42, alpha=.9, zorder=3)
ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("Actual downtime  (hours)"); ax.set_ylabel("Predicted downtime  (hours)")
ax.legend(loc="upper left", frameon=False); base(ax); fig.tight_layout()
save(fig, "downtime_scatter_light.svg")

# 5 ── SESSION 3 · three machine faults separate by SOUND (find the pattern) ───
def blob(cx, cy, n, s=.05): return np.c_[rng.normal(cx, s, n), rng.normal(cy, s, n)]
healthy = blob(.18, .16, 70); bearing = blob(.20, .56, 70); imbal = blob(.58, .20, 70)
fig, ax = plt.subplots(figsize=(7.2, 4.7))
ax.scatter(*healthy.T, c=GREEN, edgecolors="white", linewidth=.6, s=46, label="Healthy", zorder=3)
ax.scatter(*bearing.T, c=RED, edgecolors="white", linewidth=.6, s=46, label="Bearing fault", zorder=3)
ax.scatter(*imbal.T, c=AMBER, edgecolors="white", linewidth=.6, s=46, label="Imbalance", zorder=3)
ax.set_xlabel("Low-frequency share  (the rumble)"); ax.set_ylabel("High-frequency share  (the whine)")
ax.legend(loc="upper right", frameon=False); base(ax); fig.tight_layout()
save(fig, "sound_clusters_light.svg")

# 6 ── SESSION 3 · sound feature importance (whine + rumble lead) ──────────────
sf = ["Total energy", "Dominant pitch", "Mid-band share", "Low-band share\n(rumble)", "High-band share\n(whine)"]
sw = np.array([0.08, 0.12, 0.14, 0.30, 0.36])
order = np.argsort(sw)
colors = [AMBER if "rumble" in sf[i] else (RED if "whine" in sf[i] else TEAL) for i in order]
fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.barh(np.array(sf)[order], sw[order], color=colors, edgecolor="white", height=.66)
ax.set_xlabel("How much the model relied on each part of the sound")
base(ax); ax.grid(axis="y", alpha=0); fig.tight_layout(); save(fig, "sound_importance_light.svg")

# 7 ── SESSION 3 · anomaly detection (learn normal, flag the surprising) ───────
normal = rng.normal(0.0, 1.0, 520)
odd = rng.normal(4.3, 0.7, 26)
fig, ax = plt.subplots(figsize=(7.2, 4.3))
bins = np.linspace(-3.5, 6.5, 46)
ax.hist(normal, bins=bins, color=TEAL, edgecolor="white", alpha=.92, label="Normal machines")
ax.hist(odd, bins=bins, color=RED, edgecolor="white", alpha=.92, label="Flagged as unusual")
ax.axvline(2.6, color=AMBER, ls="--", lw=2.2); ax.text(2.7, ax.get_ylim()[1]*.92, " alarm line", color=AMBER, fontsize=11)
ax.set_xlabel("\"How unusual is this machine?\"  (anomaly score)"); ax.set_ylabel("Count")
ax.legend(loc="upper left", frameon=False); base(ax); ax.grid(axis="x", alpha=0)
fig.tight_layout(); save(fig, "anomaly_hist_light.svg")

print("wrote light text+speech charts ->", os.path.normpath(FIG))
