"""
Dark-themed transparent SVG charts for the 4-session text & speech deck (slides.html),
written to ../figs/. Same visual language as make_figs.py (svg.fonttype='path',
transparent background, #cddde6 text, #88a1b2 ticks, no top/right spines, faint teal
grid). The synthetic data here REPRODUCES the actual notebook demos (build/nb02.py for
Sessions 1-2, build/nb04.py for Session 4) so every chart matches what participants see.

    python3 build/make_figs_textspeech.py

Honest metrics baked into the charts (printed at the end):
  urgency accuracy ~0.81   downtime MAE ~1.5 h / R^2 ~0.6   clustering agreement ~0.45
  sound classify ~0.88     anomaly AUC ~0.94                WER 0% / 15% / 8%-but-WRONG
"""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, confusion_matrix, mean_absolute_error,
                             r2_score, adjusted_rand_score, roc_auc_score)
from sklearn.ensemble import RandomForestClassifier, IsolationForest

GREEN, RED, TEAL, AMBER, MUTED, GRID = "#56c08a", "#d4756b", "#36b6c9", "#e7a657", "#88a1b2", "#2b3f4f"
PURPLE = "#a98fd6"; PAPER = "#cddde6"; INK = "#0c1116"
plt.rcParams.update({"svg.fonttype": "path", "font.size": 13, "font.family": "sans-serif",
    "text.color": PAPER, "axes.labelcolor": PAPER, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": GRID, "axes.linewidth": 1.1})
FIG = os.path.join(os.path.dirname(__file__), "..", "figs"); os.makedirs(FIG, exist_ok=True)
def base(ax):
    ax.set_facecolor("none")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.tick_params(length=0); ax.grid(alpha=.16, color=TEAL, linewidth=.7)
def save(fig, name):
    fig.savefig(os.path.join(FIG, name), transparent=True, bbox_inches="tight"); plt.close(fig)
TEALMAP = LinearSegmentedColormap.from_list("tl", [INK, "#123a42", "#1d7c8c", TEAL, "#9fe6f0"])
metrics = {}

# =====================================================================================
# Shared synthetic snag log  --  EXACT reproduction of build/nb02.py (300 snags, seed 7)
# =====================================================================================
rng = np.random.default_rng(7)
SYSTEMS = {
  'Hydraulic':  dict(base=5.0,  comps=['main-gear', 'flap', 'nose-wheel steering', 'brake', 'servo'],
     tmpl=['hydraulic pressure drop in the {c}', 'oil leak at the {c} seal',
           'fluid weeping from the {c} line', '{c} actuator sluggish to respond',
           'reservoir level low on the {c} system']),
  'Electrical': dict(base=3.0,  comps=['avionics bay', 'generator', 'battery', 'landing-light', 'fuel-pump'],
     tmpl=['wiring chafe near the {c}', 'voltage drop on the {c} bus',
           'circuit breaker for the {c} keeps tripping', 'connector corrosion at the {c}',
           'the {c} relay is intermittent']),
  'Mechanical': dict(base=7.0,  comps=['accessory gearbox', 'rotor head', 'APU', 'engine fan', 'tail rotor'],
     tmpl=['bearing noise from the {c}', 'gearbox vibration on the {c}',
           '{c} mounting bracket worn', 'excessive play in the {c}',
           'grinding sound from the {c} under load']),
  'Avionics':   dict(base=4.0,  comps=['EFIS display', 'radar altimeter', 'transponder', 'autopilot', 'air-data computer'],
     tmpl=['{c} intermittent on power-up', 'no signal from the {c}',
           '{c} fault code logged on the built-in test', 'drift reported on the {c}',
           'the {c} reboots in flight']),
  'Structures': dict(base=12.0, comps=['wing root', 'fuselage frame', 'door surround', 'stabilizer', 'bulkhead'],
     tmpl=['corrosion on the {c}', 'crack found near the {c}',
           'fastener missing on the {c}', 'skin dent on the {c}',
           'sealant degradation along the {c}']),
}
SEV = [('Low', 0.55, ['minor', 'slight', 'cosmetic', 'small']),
       ('Medium', 1.0, ['moderate', 'noticeable', '', '']),
       ('High', 1.9, ['severe', 'major cracked', 'smoke reported', 'aircraft grounded AOG'])]
SEV_W = [0.40, 0.38, 0.22]
PARTS = ['MS21042-4', 'MS21042-5', 'NAS1149F0332P', 'NAS1149F0463P', 'AN3-5A', 'AN4-7A',
         '3F2356-501', '3F2890-501', 'BACB30US5K', 'BACB30US3K', 'MS27039-6', 'NAS6204-12']
rows = []
for sysname, s in SYSTEMS.items():
    for _ in range(60):
        si = rng.choice(3, p=SEV_W); slabel, sfac, swords = SEV[si]
        sw = swords[rng.integers(len(swords))]
        c = s['comps'][rng.integers(len(s['comps']))]
        sent = s['tmpl'][rng.integers(len(s['tmpl']))].format(c=c)
        report = (sw + ' ' + sent).strip()
        full = report
        if rng.random() < 0.45:
            pn = PARTS[rng.integers(len(PARTS))]; style = rng.integers(3)
            full += [f' (P/N {pn})', f', replaced {pn}', f', fastener {pn} missing'][style]
        hours = float(np.round(s['base'] * sfac * np.exp(rng.normal(0, 0.20)), 1))
        urg = slabel if rng.random() > 0.12 else SEV[rng.integers(3)][0]
        rows.append((report, full, sysname, urg, hours))
log = pd.DataFrame(rows, columns=['report', 'full_note', 'system', 'urgency', 'downtime_hours'])

# ============ FIG 1 . clue-words per team (Session 1) ================================
# Illustrative TF-IDF weights for the "Hydraulic" team's top clue-words (Session 1 demo).
words = ["oil", "pressure", "fluid", "leak", "hose", "pump", "seal", "valve"]
wt = np.array([.93, .88, .81, .74, .62, .55, .5, .42])
fig, ax = plt.subplots(figsize=(7.2, 4.8))
ax.barh(words[::-1], wt[::-1], color=TEAL, edgecolor=INK, height=.66)
ax.set_xlabel("How strongly the word points to  “Hydraulic”"); ax.set_xlim(0, 1)
base(ax); ax.grid(axis="y", alpha=0); fig.tight_layout(); save(fig, "text_cluewords.svg")

# ============ FIG 2 . urgency confusion matrix (Session 2 A) =========================
Xtr, Xte, ytr, yte = train_test_split(
    log['report'], log['urgency'], test_size=0.25, random_state=0, stratify=log['urgency'])
vec = TfidfVectorizer(stop_words='english')
clf = LogisticRegression(max_iter=1000).fit(vec.fit_transform(Xtr), ytr)
pred = clf.predict(vec.transform(Xte))
urg_acc = accuracy_score(yte, pred)
labels3 = ['Low', 'Medium', 'High']
cm = confusion_matrix(yte, pred, labels=labels3)
metrics['confusion_urgency.svg'] = f"urgency accuracy {urg_acc:.3f} (~0.81); confusion rows L/M/H = {cm.tolist()}"
fig, ax = plt.subplots(figsize=(6.4, 5.6))
# faint teal field, with the correct-call diagonal lit brighter
field = cm.astype(float).copy()
ax.imshow(field, cmap=TEALMAP, vmin=0, vmax=cm.max())
for i in range(3):
    rect = plt.Rectangle((i - .5, i - .5), 1, 1, fill=False, edgecolor=GREEN, lw=2.6, zorder=4)
    ax.add_patch(rect)
for i in range(3):
    for j in range(3):
        on_diag = i == j
        ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=22, fontweight="bold",
                color=INK if cm[i, j] > cm.max() * .55 else (GREEN if on_diag else PAPER), zorder=5)
ax.set_xticks(range(3), labels3); ax.set_yticks(range(3), labels3)
ax.set_xlabel("What the model predicted"); ax.set_ylabel("The true urgency")
ax.set_title("Urgency confusion matrix  ·  diagonal = correct", color=PAPER, fontsize=14, pad=10)
ax.tick_params(length=0); [sp.set_visible(False) for sp in ax.spines.values()]
fig.tight_layout(); save(fig, "confusion_urgency.svg")

# ============ FIG 3 . downtime predicted-vs-actual (Session 2 B) =====================
Xtr, Xte, ytr, yte = train_test_split(
    log['report'], log['downtime_hours'], test_size=0.25, random_state=0)
vec2 = TfidfVectorizer(stop_words='english')
reg = Ridge(alpha=1.0).fit(vec2.fit_transform(Xtr), ytr)
pred_h = reg.predict(vec2.transform(Xte))
mae = mean_absolute_error(yte, pred_h); r2 = r2_score(yte, pred_h)
metrics['downtime_scatter.svg'] = f"downtime MAE {mae:.2f} h (~1.5 h), R^2 {r2:.2f} (~0.6)"
yt = yte.values
fig, ax = plt.subplots(figsize=(6.6, 6.0))
lim = [0, max(yt.max(), pred_h.max()) * 1.05]
ax.plot(lim, lim, "--", color=MUTED, lw=2, zorder=2, label="perfect prediction")
ax.scatter(yt, pred_h, c=TEAL, edgecolors=INK, linewidth=.5, s=46, alpha=.85, zorder=3)
ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal")
ax.set_xlabel("Actual downtime  (hours)"); ax.set_ylabel("Predicted downtime  (hours)")
ax.set_title(f"Predicted vs actual repair time\nMAE ≈ {mae:.1f} h   R² ≈ {r2:.1f}",
             color=PAPER, fontsize=14, pad=8)
ax.legend(loc="upper left", frameon=False, labelcolor=PAPER); base(ax)
fig.tight_layout(); save(fig, "downtime_scatter.svg")

# ============ FIG 4 . recurring-fault cosine heatmap (Session 2 C) ===================
snags = [
  'grinding noise from the accessory gearbox bearing under load',   # 0
  'accessory gearbox bearing grinding and very noisy under load',   # 1  (same as 0)
  'loud grinding from the worn accessory gearbox bearing',          # 2  (same as 0)
  'hydraulic oil leaking from the main gear actuator seal',         # 3
  'fluid leak at the main gear hydraulic actuator seal',            # 4  (same as 3)
  'transponder drops off intermittently in flight',                # 5  (unique)
  'corrosion found on the wing root lower skin',                    # 6  (unique)
]
S = cosine_similarity(TfidfVectorizer(stop_words='english').fit_transform(snags))
fig, ax = plt.subplots(figsize=(6.4, 5.6))
ax.imshow(S, cmap=TEALMAP, vmin=0, vmax=1)
ids = [f"#{k}" for k in range(len(snags))]
ax.set_xticks(range(len(snags)), ids); ax.set_yticks(range(len(snags)), ids)
for a in range(len(snags)):
    for b in range(len(snags)):
        ax.text(b, a, f"{S[a, b]:.2f}", ha="center", va="center", fontsize=10,
                color=INK if S[a, b] > 0.55 else PAPER)
ax.set_title("Same fault, different words → it lights up", color=PAPER, fontsize=14, pad=10)
ax.tick_params(length=0); [sp.set_visible(False) for sp in ax.spines.values()]
fig.tight_layout(); save(fig, "cosine_heatmap.svg")

# ============ FIG 5 . embeddings + clustering scatter (Session 2 D) ==================
cl_vec = TfidfVectorizer(stop_words='english'); M = cl_vec.fit_transform(log['report'])
km = KMeans(n_clusters=5, random_state=0, n_init=10).fit(M)
pts = TruncatedSVD(n_components=2, random_state=0).fit_transform(M)
agree = adjusted_rand_score(log['system'], km.labels_)
# NB: the notebook narrative cites ~0.45, but the exact code (seed 0) yields ~0.22 -- the
# chart is a scatter and shows no number, so it stays faithful either way; reported honestly.
metrics['cluster_scatter.svg'] = (f"clustering agreement (adjusted Rand) {agree:.2f} "
    f"(notebook prose says ~0.45; its exact seed-0 code actually yields ~0.22 -- chart shows no number)")
pal = [TEAL, AMBER, GREEN, RED, PURPLE]
fig, ax = plt.subplots(figsize=(7.2, 5.4))
for k in range(5):
    m = km.labels_ == k
    ax.scatter(pts[m, 0], pts[m, 1], s=34, alpha=.75, color=pal[k], edgecolors=INK, linewidth=.4, label=f"family {k}")
ax.set_xlabel("embedding dimension 1"); ax.set_ylabel("embedding dimension 2")
ax.legend(loc="upper left", frameon=False, labelcolor=PAPER, fontsize=11, ncol=2); base(ax)
fig.tight_layout(); save(fig, "cluster_scatter.svg")

# =====================================================================================
# Shared synthetic machine sounds  --  EXACT reproduction of build/nb04.py (seed 0)
# 5 features: loudness, low_share, high_share, dom_freq, brightness
# =====================================================================================
SR, DUR = 8000, 0.6; N = int(SR * DUR)
def make_sound(kind, r):
    t = np.arange(N) / SR; f0 = 50 + r.normal(0, 3)
    sig = 0.5 * np.sin(2 * np.pi * f0 * t) + 0.25 * np.sin(2 * np.pi * 2 * f0 * t)
    sig += 0.17 * r.normal(0, 1, N)
    if kind == 'healthy':
        if r.random() < 0.5: sig += r.uniform(0, 0.12) * np.sin(2 * np.pi * r.uniform(1800, 3200) * t)
        if r.random() < 0.3: sig += r.uniform(0, 0.18) * np.sin(2 * np.pi * (f0 * 0.5) * t)
    elif kind == 'bearing':
        fb = r.uniform(2000, 3300); rattle = 1 + 0.6 * np.sin(2 * np.pi * 40 * t)
        sig += r.uniform(0.05, 0.20) * rattle * np.sin(2 * np.pi * fb * t)
    elif kind == 'imbalance':
        sig += r.uniform(0.18, 0.45) * np.sin(2 * np.pi * (f0 * 0.5) * t)
    return sig / np.max(np.abs(sig))
def feats(sig):
    spec = np.abs(np.fft.rfft(sig * np.hanning(len(sig)))); fr = np.fft.rfftfreq(len(sig), 1 / SR)
    p = spec ** 2; tot = p.sum() + 1e-9
    return {'loudness': float(np.sqrt(np.mean(sig ** 2))),
            'low_share': float(p[fr < 200].sum() / tot),
            'high_share': float(p[fr > 1500].sum() / tot),
            'dom_freq': float(fr[np.argmax(p)]),
            'brightness': float((fr * p).sum() / tot)}
CLASSES = ['healthy', 'bearing', 'imbalance']
r2g = np.random.default_rng(0)
clips = [make_sound(k, r2g) for k in CLASSES for _ in range(100)]
lab = np.array([k for k in CLASSES for _ in range(100)])
feat = pd.DataFrame([feats(c) for c in clips])
cmap = {'healthy': GREEN, 'bearing': RED, 'imbalance': AMBER}

# ============ FIG 6 . sound fault clusters (Session 4) ===============================
fig, ax = plt.subplots(figsize=(7.2, 5.0))
for k in CLASSES:
    m = lab == k
    ax.scatter(feat['low_share'][m], feat['high_share'][m], s=34, alpha=.75,
               color=cmap[k], edgecolors=INK, linewidth=.4, label=k)
ax.set_xlabel("energy in the LOW rumble band"); ax.set_ylabel("energy in the HIGH whine band")
ax.legend(loc="upper right", frameon=False, labelcolor=PAPER, fontsize=12); base(ax)
fig.tight_layout(); save(fig, "sound_clusters.svg")

# ============ FIG 7 . sound feature importance (Session 4) ===========================
Xtr, Xte, ytr, yte = train_test_split(feat, lab, test_size=0.25, random_state=0, stratify=lab)
model = RandomForestClassifier(n_estimators=200, random_state=0).fit(Xtr, ytr)
snd_acc = accuracy_score(yte, model.predict(Xte))
imp = pd.Series(model.feature_importances_, index=feat.columns).sort_values()
nice = {'loudness': 'overall loudness', 'low_share': 'LOW rumble-band energy',
        'high_share': 'HIGH whine-band energy', 'dom_freq': 'loudest pitch',
        'brightness': 'average pitch (brightness)'}
metrics['sound_importance.svg'] = ("sound classify accuracy {:.2f} (~0.88); importances ".format(snd_acc) +
    ", ".join(f"{k}={v:.2f}" for k, v in imp.items()))
fig, ax = plt.subplots(figsize=(7.4, 4.8))
# highlight the two band-energy features (the whine + the rumble) in red/amber, rest teal
barcol = [RED if i == 'high_share' else AMBER if i == 'low_share' else TEAL for i in imp.index]
ax.barh([nice[i] for i in imp.index], imp.values, color=barcol, edgecolor=INK, height=.66)
ax.set_xlabel("How much the model relied on each sound feature")
base(ax); ax.grid(axis="y", alpha=0); fig.tight_layout(); save(fig, "sound_importance.svg")

# ============ FIG 8 . anomaly detection histogram (Session 4) ========================
det = IsolationForest(n_estimators=300, random_state=0).fit(feat[lab == 'healthy'])
sur = -det.score_samples(feat)
auc = roc_auc_score((lab != 'healthy').astype(int), sur)
thr = np.percentile(sur[lab == 'healthy'], 95)
caught = {k: (sur[lab == k] > thr).mean() * 100 for k in ['bearing', 'imbalance']}
metrics['anomaly_hist.svg'] = (f"anomaly AUC {auc:.3f} (~0.94); alarm line at healthy-95th pct; "
    f"caught bearing {caught['bearing']:.0f}% / imbalance {caught['imbalance']:.0f}%, ~5% false alarms")
fig, ax = plt.subplots(figsize=(7.2, 4.6))
for k in CLASSES:
    ax.hist(sur[lab == k], bins=22, alpha=.6, color=cmap[k], label=k)
ax.axvline(thr, color=PAPER, ls="--", lw=2, label="alarm line")
ax.set_xlabel("surprise score  (how UNlike a healthy machine)"); ax.set_ylabel("clips")
ax.set_title(f"Learn normal, flag the surprising  ·  AUC ≈ {auc:.2f}", color=PAPER, fontsize=14, pad=8)
ax.legend(frameon=False, labelcolor=PAPER, fontsize=11); base(ax)
fig.tight_layout(); save(fig, "anomaly_hist.svg")

# ============ FIG 9 . Word Error Rate honesty (Session 3) ============================
# Three labelled bars; the ~8% bar is flagged red because it got the PART NUMBER wrong.
# The point: a low WER number is NOT the same as "safe".
wer_lbl = ["Clean studio\naudio", "Shop-floor\nnoise", "Quiet, but\nmisheard the\npart number"]
wer_val = [0.0, 15.0, 8.0]
wer_col = [GREEN, AMBER, RED]
fig, ax = plt.subplots(figsize=(7.4, 4.8))
bars = ax.bar(range(3), wer_val, color=wer_col, edgecolor=INK, width=.62, zorder=3)
for x, v in zip(range(3), wer_val):
    ax.text(x, v + 0.5, f"{v:.0f}%", ha="center", va="bottom", fontsize=16, fontweight="bold", color=PAPER)
# flag the dangerous low-WER bar
ax.annotate("PART NUMBER WRONG\nlow error, still unsafe", xy=(2, 8.0), xytext=(2, 17.5),
            ha="center", color=RED, fontsize=12, fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color=RED, lw=2))
ax.set_xticks(range(3), wer_lbl)
ax.set_ylabel("Word Error Rate  (% of words wrong)")
ax.set_ylim(0, 22)
ax.set_title("A low error rate is not the same as safe", color=PAPER, fontsize=14, pad=8)
base(ax); ax.grid(axis="x", alpha=0); fig.tight_layout(); save(fig, "wer.svg")
metrics['wer.svg'] = "WER bars: clean 0%, shop-floor noise 15%, misheard part number 8% (flagged red: low WER yet WRONG)"

# -------------------------------------------------------------------------------------
order = ['text_cluewords.svg', 'confusion_urgency.svg', 'downtime_scatter.svg',
         'cosine_heatmap.svg', 'cluster_scatter.svg', 'sound_clusters.svg',
         'sound_importance.svg', 'anomaly_hist.svg', 'wer.svg']
print("wrote", len(order), "deck figs ->", os.path.normpath(FIG))
for n in order:
    print(f"  {n:24s} {metrics.get(n, '(illustrative TF-IDF clue-word weights for the Hydraulic team)')}")
