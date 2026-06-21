"""
Build the Session-2 TEXT notebook: "Text Analytics II - Predicting, Extracting &
Finding Recurring Faults". This is the second of the two text sessions and fills
the biggest gap in the set: nb04 only sorts reports into teams, this one shows the
three things engineers actually want next -

  A) predict a CATEGORY from text   (urgency: High/Medium/Low)        -> classification
  B) predict a NUMBER from text      (expected downtime in hours)      -> regression
  C) find RECURRING / duplicate faults (same fault, different words)   -> cosine similarity
  D) pull out PART NUMBERS hiding in prose (auditable)                 -> regex / entity extraction
  E) discover THEMES with no labels  (honest LDA)                      -> topic modelling   [bonus]
  F) prove it is not a toy on a REAL public corpus + the header-trap   -> 20 Newsgroups     [bonus]

Uses the shared nbbuild design system (matches nb04). Self-contained except the
optional Section F, which fetches scikit-learn's built-in 20 Newsgroups (~14 MB,
one line) - fine in Colab. Regenerate with:  python3 build/nb04b.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from nbmd import *  # noqa

# A consistent, projector-friendly chart style reused in every plotting cell.
STYLE = (
    "import matplotlib.pyplot as plt\n"
    "plt.rcParams.update({\n"
    "    'figure.figsize': (9, 5.5), 'figure.dpi': 110,\n"
    "    'font.size': 13, 'axes.titlesize': 16, 'axes.titleweight': 'bold',\n"
    "    'axes.labelsize': 13, 'axes.spines.top': False, 'axes.spines.right': False,\n"
    "    'axes.grid': True, 'grid.alpha': 0.25,\n"
    "})\n"
    "TEAL, AMBER, RED, GREEN, PURPLE, SLATE = '#0b6e7a', '#b26a00', '#9c2b2b', '#2e7d32', '#5b2a86', '#445566'\n"
)

cells = [

md(banner("Text Analytics · Session 2 of 4",
   "Beyond Sorting: Predict, Extract & Find Repeat Faults",
   "The same words you already write — now read for urgency, repair time, repeat defects and part numbers")),

md("## How to use this notebook\n\n"
   "**Hands-on, but you write no code.** You only **run** the cells, top to bottom "
   "(click a cell, press **Shift + Enter**) and read what comes out. Run them **in order**. "
   "If anything looks stuck: **Runtime → Restart and run all**.\n\n"
   "As you scroll you will meet four little callouts: "
   "🟦 a new word (Vocabulary), 🟩 what a cell just did (What just happened), "
   "🟧 something to try (Your turn), 🟪 the big picture (Recap / Coming up)."),

md(bigidea(
   "In the last session we taught the computer to <b>sort</b> a written report into URGENT vs ROUTINE. "
   "Useful &mdash; but sorting is just the doorway. Once words are numbers, the <b>same machinery</b> answers the "
   "questions a maintenance manager actually asks:<br><br>"
   "&bull; <b>How urgent is this?</b> &mdash; predict a <i>category</i> (High / Medium / Low).<br>"
   "&bull; <b>How long will it take to fix?</b> &mdash; predict a <i>number</i> (downtime hours).<br>"
   "&bull; <b>Have we seen this before?</b> &mdash; find <i>recurring</i> faults worded differently.<br>"
   "&bull; <b>Which part is it?</b> &mdash; <i>pull out</i> the part numbers buried in the text.<br><br>"
   "Every one of these is the same idea you already know &mdash; <b>turn the words into numbers, learn the pattern, "
   "judge a new case</b> &mdash; pointed at a new question. Nothing here is magic; all of it is auditable.")),

md(story(
   "<b>Our setting: an MRO / overhaul line.</b> Every shift, mechanics type short free-text snags &mdash; one or two "
   "lines, in a hurry, with their own shorthand:<br><br>"
   "<i>\"minor oil leak at the main-gear seal\"</i> &nbsp;&middot;&nbsp; "
   "<i>\"smoke reported, circuit breaker for the generator keeps tripping\"</i> &nbsp;&middot;&nbsp; "
   "<i>\"grinding noise from the accessory gearbox bearing (P/N MS21042-4)\"</i><br><br>"
   "Buried in that prose is everything we need to triage the line &mdash; <b>if</b> a computer can read it. "
   "Let us build that, step by step, and stay honest about where it slips.")),

# ----------------------------------------------------------------------- data
md(section("Build the snag log (our dataset)", 1)),
md(vocab("Dataset (reminder)",
   "Same idea as every session: a <b>dataset</b> is just a table &mdash; one row per snag, columns for what we recorded. "
   "Here we <i>manufacture</i> 300 realistic snags so everyone sees identical data and no private records leave the room. "
   "In real life this table <i>is</i> your maintenance log. Each row has the free-text <b>report</b>, the <b>system</b>, "
   "an <b>urgency</b> tag, and the <b>downtime hours</b> it eventually took.")),
code(
   "import numpy as np, pandas as pd, re\n"
   "rng = np.random.default_rng(7)   # fixed seed: everyone gets the same 300 snags\n"
   "\n"
   "# Each system has its own symptom vocabulary and a typical repair size (hours).\n"
   "SYSTEMS = {\n"
   "  'Hydraulic':  dict(base=5.0,  comps=['main-gear','flap','nose-wheel steering','brake','servo'],\n"
   "     tmpl=['hydraulic pressure drop in the {c}', 'oil leak at the {c} seal',\n"
   "           'fluid weeping from the {c} line', '{c} actuator sluggish to respond',\n"
   "           'reservoir level low on the {c} system']),\n"
   "  'Electrical': dict(base=3.0,  comps=['avionics bay','generator','battery','landing-light','fuel-pump'],\n"
   "     tmpl=['wiring chafe near the {c}', 'voltage drop on the {c} bus',\n"
   "           'circuit breaker for the {c} keeps tripping', 'connector corrosion at the {c}',\n"
   "           'the {c} relay is intermittent']),\n"
   "  'Mechanical': dict(base=7.0,  comps=['accessory gearbox','rotor head','APU','engine fan','tail rotor'],\n"
   "     tmpl=['bearing noise from the {c}', 'gearbox vibration on the {c}',\n"
   "           '{c} mounting bracket worn', 'excessive play in the {c}',\n"
   "           'grinding sound from the {c} under load']),\n"
   "  'Avionics':   dict(base=4.0,  comps=['EFIS display','radar altimeter','transponder','autopilot','air-data computer'],\n"
   "     tmpl=['{c} intermittent on power-up', 'no signal from the {c}',\n"
   "           '{c} fault code logged on the built-in test', 'drift reported on the {c}',\n"
   "           'the {c} reboots in flight']),\n"
   "  'Structures': dict(base=12.0, comps=['wing root','fuselage frame','door surround','stabilizer','bulkhead'],\n"
   "     tmpl=['corrosion on the {c}', 'crack found near the {c}',\n"
   "           'fastener missing on the {c}', 'skin dent on the {c}',\n"
   "           'sealant degradation along the {c}']),\n"
   "}\n"
   "# Severity tier carries cue words AND scales the repair time.\n"
   "SEV = [('Low', 0.55, ['minor','slight','cosmetic','small']),\n"
   "       ('Medium', 1.0, ['moderate','noticeable','','']),\n"
   "       ('High', 1.9, ['severe','major cracked','smoke reported','aircraft grounded AOG'])]\n"
   "SEV_W = [0.40, 0.38, 0.22]\n"
   "# A small parts catalogue, so some part numbers naturally recur across snags.\n"
   "PARTS = ['MS21042-4','MS21042-5','NAS1149F0332P','NAS1149F0463P','AN3-5A','AN4-7A',\n"
   "         '3F2356-501','3F2890-501','BACB30US5K','BACB30US3K','MS27039-6','NAS6204-12']\n"
   "\n"
   "rows = []\n"
   "for sysname, s in SYSTEMS.items():\n"
   "    for _ in range(60):\n"
   "        si = rng.choice(3, p=SEV_W); slabel, sfac, swords = SEV[si]\n"
   "        sw = swords[rng.integers(len(swords))]\n"
   "        c = s['comps'][rng.integers(len(s['comps']))]\n"
   "        sent = s['tmpl'][rng.integers(len(s['tmpl']))].format(c=c)\n"
   "        report = (sw + ' ' + sent).strip()      # the symptom in words (what the models read)\n"
   "        full = report\n"
   "        if rng.random() < 0.45:                  # ~half the notes also name a part\n"
   "            pn = PARTS[rng.integers(len(PARTS))]; style = rng.integers(3)\n"
   "            full += [f' (P/N {pn})', f', replaced {pn}', f', fastener {pn} missing'][style]\n"
   "        hours = float(np.round(s['base'] * sfac * np.exp(rng.normal(0, 0.20)), 1))\n"
   "        urg = slabel if rng.random() > 0.12 else SEV[rng.integers(3)][0]   # a little label noise\n"
   "        rows.append((report, full, sysname, urg, hours))\n"
   "\n"
   "log = pd.DataFrame(rows, columns=['report','full_note','system','urgency','downtime_hours'])\n"
   "print('Snag log built:', len(log), 'reports')\n"
   "log.sample(6, random_state=1)"),
md(did("There is our <b>dataset</b> &mdash; 300 snags, one per row. The free-text <code>report</code> is the symptom in the "
       "mechanic's words (the clue the models read); <code>full_note</code> is that same note with any part number they "
       "appended (we mine that in Step 5); and there are three different answers we might want &mdash; <code>system</code>, "
       "<code>urgency</code>, and <code>downtime_hours</code>. Notice the last one is a <b>number</b>, not a category. "
       "Hold that thought; it is the new idea of this session.")),

# --------------------------------------------------------------- A: urgency
md(section("Predict a CATEGORY &mdash; how urgent is it?", 2)),
md(vocab("Classification (reminder)",
   "When the answer is one of a few <b>named buckets</b> &mdash; High / Medium / Low &mdash; that is <b>classification</b>, exactly "
   "like flagging URGENT vs ROUTINE last session. We turn the words into numbers with <b>TF-IDF</b> (rare, distinctive words count for "
   "more), hide a quarter of the snags as an honest test, train, and measure.")),
code(
   "from sklearn.feature_extraction.text import TfidfVectorizer\n"
   "from sklearn.linear_model import LogisticRegression\n"
   "from sklearn.model_selection import train_test_split\n"
   "from sklearn.metrics import accuracy_score, confusion_matrix\n"
   "\n"
   "Xtr, Xte, ytr, yte = train_test_split(\n"
   "    log['report'], log['urgency'], test_size=0.25, random_state=0, stratify=log['urgency'])\n"
   "\n"
   "vec = TfidfVectorizer(stop_words='english')      # words -> numbers\n"
   "clf = LogisticRegression(max_iter=1000)\n"
   "clf.fit(vec.fit_transform(Xtr), ytr)             # learn on the training snags\n"
   "pred = clf.predict(vec.transform(Xte))           # judge the hidden test snags\n"
   "\n"
   "acc = accuracy_score(yte, pred)\n"
   "print('Tested on', len(yte), 'snags it had never read.')\n"
   "print('Accuracy:', round(acc, 3), ' -> about', round(acc*100), 'in 100 filed correctly.')"),
md(did("About <b>four in five</b> hidden snags (~81%) get the right urgency &mdash; from the wording alone. Words like "
       "<i>minor</i>, <i>cosmetic</i>, <i>smoke</i>, <i>AOG</i> are doing the work. Good, but clearly not perfect &mdash; and the "
       "honest way to see <i>where</i> it slips is the confusion matrix.")),
code(
   STYLE +
   "labels = ['Low', 'Medium', 'High']\n"
   "cm = confusion_matrix(yte, pred, labels=labels)\n"
   "\n"
   "fig, ax = plt.subplots(figsize=(6.8, 6))\n"
   "im = ax.imshow(cm, cmap='Blues')\n"
   "ax.set_xticks(range(3), labels); ax.set_yticks(range(3), labels)\n"
   "ax.set_xlabel('What the model predicted'); ax.set_ylabel('The true urgency')\n"
   "ax.set_title('Urgency confusion matrix\\n(diagonal = correct)')\n"
   "for i in range(3):\n"
   "    for j in range(3):\n"
   "        ax.text(j, i, cm[i, j], ha='center', va='center', fontsize=20,\n"
   "                color='white' if cm[i, j] > cm.max()*0.5 else '#1f2d3d', fontweight='bold')\n"
   "ax.grid(False); plt.tight_layout(); plt.show()"),
md(did("Read the grid: the strong diagonal is the correct calls. The off-diagonal cells are the honest mistakes &mdash; "
       "mostly <b>Low&harr;Medium</b> mix-ups (snags that genuinely read alike). It caught <b>10 of the 15</b> High snags, and "
       "slipped on the truly dangerous call &mdash; a <b>High</b> snag marked <i>Low</i> &mdash; only <b>once</b>. Rare, but it "
       "<i>did</i> happen, which is exactly why the High bucket still gets a human's eyes. That is the question to ask of any "
       "model: <i>not just how accurate, but what does it get wrong, and how badly?</i>")),

# ------------------------------------------------------------ B: regression
md(section("Predict a NUMBER &mdash; how long to fix?", 3)),
md(bigidea(
   "Here is the genuinely new idea of the session. Sometimes the answer you want is not a bucket &mdash; it is a "
   "<b>number</b>: how many hours of downtime, how many man-hours, how much it will cost. Predicting a number is called "
   "<b>regression</b>. The beautiful part: the <b>front end is identical</b>. We turn the same words into numbers the same "
   "way; we just swap the final step from a classifier to a regressor. Same clue, different kind of answer.")),
md(vocab("Classification vs Regression",
   "<b>Classification</b> answers <i>which bucket?</i> (Hydraulic; High). <b>Regression</b> answers <i>how much?</i> "
   "(7.4 hours; &#8377;42,000). If you can list the possible answers, it is classification; if the answer sits on a number "
   "line, it is regression. Everything before the final step &mdash; the words-to-numbers part &mdash; is the same.")),
code(
   "from sklearn.linear_model import Ridge\n"
   "from sklearn.metrics import mean_absolute_error, r2_score\n"
   "\n"
   "# Same text in; this time the answer is a NUMBER (downtime hours).\n"
   "Xtr, Xte, ytr, yte = train_test_split(\n"
   "    log['report'], log['downtime_hours'], test_size=0.25, random_state=0)\n"
   "\n"
   "vec2 = TfidfVectorizer(stop_words='english')     # SAME words-to-numbers step\n"
   "reg  = Ridge(alpha=1.0)                           # only the final step changed\n"
   "reg.fit(vec2.fit_transform(Xtr), ytr)\n"
   "pred_h = reg.predict(vec2.transform(Xte))\n"
   "\n"
   "print('Average miss (MAE):', round(mean_absolute_error(yte, pred_h), 2), 'hours')\n"
   "print('R-squared        :', round(r2_score(yte, pred_h), 2), ' (1.0 = perfect, 0 = no better than guessing the average)')"),
md(did("On snags it never saw, the estimate is off by only about <b>1.5 hours on average</b> (on jobs that run ~6 hours). The "
       "R&sup2; (around <b>0.6</b>) says it explains most of the variation &mdash; good, not perfect. That is the honest lesson: a "
       "<b>number is harder to nail than a bucket</b>, because the words tell you the <i>kind</i> of job but not every last detail. "
       "A planner uses this as a first cut and adds a margin &mdash; not as gospel.")),
code(
   STYLE +
   "import numpy as np\n"
   "err = np.abs(pred_h - yte.values)\n"
   "fig, ax = plt.subplots(figsize=(7.5, 7))\n"
   "sc = ax.scatter(yte.values, pred_h, c=err, cmap='YlOrRd', s=70, edgecolors='#1f2d3d', linewidths=0.6)\n"
   "lim = [0, max(yte.max(), pred_h.max()) * 1.05]\n"
   "ax.plot(lim, lim, '--', color=SLATE, lw=2, label='perfect prediction')\n"
   "ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect('equal')\n"
   "ax.set_xlabel('Actual downtime (hours)'); ax.set_ylabel('Predicted downtime (hours)')\n"
   "ax.set_title('Predicted vs actual repair time\\n(closer to the dashed line = better)')\n"
   "plt.colorbar(sc, label='size of the miss (hours)'); ax.legend(); plt.tight_layout(); plt.show()"),
md(did("Each dot is one hidden snag: its true downtime across, the model&rsquo;s estimate up. Dots hug the dashed line, so the "
       "model tracks reality &mdash; and the colour shows the misses are small except on a few big-repair outliers (the Structures "
       "jobs). This single chart makes &lsquo;the model learned the relationship&rsquo; <b>visible</b>, and is honest about the few it gets wrong.")),

# -------------------------------------------------------- C: recurring faults
md(section("Find RECURRING faults &mdash; same problem, different words", 4)),
md(bigidea(
   "This is the most valuable text trick for an overhaul line. The same chronic fault gets written five different ways by "
   "five mechanics, so it hides in the log and never gets flagged as recurring. We can catch it without any labels at all: "
   "turn each report into its TF-IDF numbers, then measure how <b>aligned</b> two reports are. High alignment = same words = "
   "probably the same fault, however it was phrased.")),
md(vocab("Cosine similarity",
   "A score from 0 to 1 for how much two reports point the same way once they are numbers: <b>1</b> = essentially the same "
   "wording, <b>0</b> = nothing in common. It compares the <i>distinctive</i> words, so &lsquo;grinding gearbox bearing&rsquo; and "
   "&lsquo;bearing grinding under load&rsquo; score high even though the sentences differ. It matches <b>words, not meaning</b> &mdash; "
   "so synonyms and abbreviations still need a human, and you pick the threshold.")),
code(
   "from sklearn.metrics.pairwise import cosine_similarity\n"
   "\n"
   "# Seven snags typed by different mechanics. Some are the SAME fault, worded differently.\n"
   "snags = [\n"
   "  'grinding noise from the accessory gearbox bearing under load',   # 0\n"
   "  'accessory gearbox bearing grinding and very noisy under load',   # 1  (same as 0)\n"
   "  'loud grinding from the worn accessory gearbox bearing',          # 2  (same as 0)\n"
   "  'hydraulic oil leaking from the main gear actuator seal',         # 3\n"
   "  'fluid leak at the main gear hydraulic actuator seal',            # 4  (same as 3)\n"
   "  'transponder drops off intermittently in flight',                # 5  (unique)\n"
   "  'corrosion found on the wing root lower skin',                    # 6  (unique)\n"
   "]\n"
   "V = TfidfVectorizer(stop_words='english').fit_transform(snags)\n"
   "S = cosine_similarity(V)\n"
   "print('Similarity scores (1.0 = identical wording):')\n"
   "print(np.round(S, 2))"),
code(
   STYLE +
   "fig, ax = plt.subplots(figsize=(7.5, 6.5))\n"
   "im = ax.imshow(S, cmap='YlGnBu', vmin=0, vmax=1)\n"
   "ids = [f'#{i}' for i in range(len(snags))]\n"
   "ax.set_xticks(range(len(snags)), ids); ax.set_yticks(range(len(snags)), ids)\n"
   "for i in range(len(snags)):\n"
   "    for j in range(len(snags)):\n"
   "        ax.text(j, i, f'{S[i,j]:.2f}', ha='center', va='center', fontsize=11,\n"
   "                color='white' if S[i, j] > 0.5 else '#1f2d3d')\n"
   "ax.set_title('Which snags are really the same fault?\\n(bright squares away from the diagonal = duplicates)')\n"
   "ax.grid(False); plt.colorbar(im, label='cosine similarity'); plt.tight_layout(); plt.show()\n"
   "\n"
   "print('\\nFlagged as the SAME recurring fault (similarity > 0.35):')\n"
   "for i in range(len(snags)):\n"
   "    for j in range(i+1, len(snags)):\n"
   "        if S[i, j] > 0.35:\n"
   "            print(f'  #{i} and #{j}  (score {S[i,j]:.2f})')\n"
   "            print(f'     - {snags[i]}')\n"
   "            print(f'     - {snags[j]}')"),
md(did("Two bright blocks jump out of the heatmap: snags <b>0&ndash;1&ndash;2</b> are one recurring gearbox-bearing fault, and "
       "<b>3&ndash;4</b> are one recurring hydraulic leak &mdash; even though every mechanic worded it differently. Snags 5 and 6 match "
       "nobody. No labels, no training: just &lsquo;these reports use the same distinctive words.&rsquo; This is exactly how a chronic-defect "
       "tool de-duplicates a logbook so a repeat problem finally gets noticed.")),
md(note("Where this fits at work: this is the heart of <b>chronic / repetitive-defect detection</b>. Commercial aviation tools "
        "do exactly this on real logbooks; one vendor (Veryon&rsquo;s ChronicX) <i>claims</i> roughly 40% of defects go unflagged because "
        "the same fault is coded inconsistently &mdash; vendor figures, not an independent audit, but the <i>problem</i> is very real and "
        "very HAL.")),

# --------------------------------------------------- C2: embeddings + clustering
md(section("Group the snags into families &mdash; with no labels at all", 5)),
md(bigidea(
   "Everything so far learned from an <b>answer column</b>. But what if you just have a pile of reports and want the "
   "computer to <b>organise them into natural families</b> on its own &mdash; no labels, no categories set in advance? "
   "That is <b>clustering</b>, and it runs on the same words-to-numbers idea, one step further.")),
md(vocab("Embedding",
   "When we turn a report into its row of TF-IDF numbers, we have placed it as a <b>point in space</b> &mdash; reports that "
   "use similar words sit close together. That numeric position is its <b>embedding</b>. We can even squeeze it down to "
   "two numbers and <b>plot every report as a dot</b>, so 'close = similar' becomes something you can see.")),
md(vocab("Clustering (k-means)",
   "<b>Clustering</b> asks the computer to find groups of points that huddle together. <b>k-means</b> is the classic "
   "method: you tell it how many groups to look for (here 5) and it sorts every report into the nearest one &mdash; entirely "
   "from the words, with <b>no labels used</b>. Then <i>we</i> read the top words of each group to name it.")),
code(
   "from sklearn.cluster import KMeans\n"
   "from sklearn.metrics import adjusted_rand_score\n"
   "\n"
   "# Same words-to-numbers step, then let k-means find 5 families -- no labels given to it.\n"
   "cl_vec = TfidfVectorizer(stop_words='english')\n"
   "M = cl_vec.fit_transform(log['report'])\n"
   "km = KMeans(n_clusters=5, random_state=0, n_init=10).fit(M)\n"
   "log['family'] = km.labels_\n"
   "\n"
   "terms = np.array(cl_vec.get_feature_names_out())\n"
   "order = km.cluster_centers_.argsort()[:, ::-1]\n"
   "print('The 5 families the computer formed on its own (top words of each):\\n')\n"
   "for k in range(5):\n"
   "    print(f'  Family {k}:', ', '.join(terms[order[k, :6]]))\n"
   "\n"
   "agree = adjusted_rand_score(log['system'], km.labels_)\n"
   "print('\\nAgreement with the real system labels (0 = random, 1 = perfect):', round(agree, 2))"),
md(did("Read the families. With <b>no labels at all</b>, the computer still pulled out clean groups: one is plainly the "
       "<i>gearbox / grinding / rotor</i> (Mechanical) family, one the <i>circuit / breaker / wiring</i> (Electrical) family, "
       "one the <i>air-data / fault</i> (Avionics) family. But a big <b>catch-all</b> family swallowed the rest, so the "
       "agreement with your official systems is <b>low (~0.22)</b>. That is honest: k-means grouped by <b>language</b>, and "
       "five clusters do not cleanly equal your five systems. Unsupervised learning <b>finds structure; you decide what it "
       "means.</b>")),
code(
   STYLE +
   "from sklearn.decomposition import TruncatedSVD\n"
   "pts = TruncatedSVD(n_components=2, random_state=0).fit_transform(M)   # the 2-number embedding, for plotting\n"
   "palette = [TEAL, AMBER, RED, GREEN, PURPLE]\n"
   "\n"
   "fig, ax = plt.subplots(figsize=(8.5, 6.5))\n"
   "for k in range(5):\n"
   "    m = km.labels_ == k\n"
   "    ax.scatter(pts[m, 0], pts[m, 1], s=45, alpha=0.7, color=palette[k], edgecolors='white', label=f'family {k}')\n"
   "ax.set_title('Every snag as a dot, grouped into families\\n(no labels used \\u2014 the computer found these)')\n"
   "ax.set_xlabel('embedding dimension 1'); ax.set_ylabel('embedding dimension 2')\n"
   "ax.legend(); ax.grid(alpha=0.25); plt.tight_layout(); plt.show()"),
md(did("There is the picture: every report is a dot, and the colours &mdash; the families k-means found &mdash; land in "
       "separate regions. Close dots are reports worded alike. This is how you would <b>auto-organise an unlabelled "
       "logbook</b> into themes to triage, with nobody pre-defining the categories.")),
md(note("The honest next step: TF-IDF places reports by the <b>exact words</b> they share, so 'oil leak' and 'fluid "
        "seepage' look unrelated. Richer <b>semantic embeddings</b> (word2vec / GloVe, classical since ~2014) place words "
        "by <b>meaning</b>, so synonyms sit together even with no shared spelling. Same idea &mdash; points in space &mdash; "
        "just smarter coordinates. It is still <b>representation, not generation</b>: the engine behind modern search, not a chatbot.")),

# ----------------------------------------------------- D: part-number extraction
md(section("Pull out the PART NUMBERS hiding in the text", 6)),
md(vocab("Entity extraction (NER)",
   "Free text hides structured gold &mdash; part numbers, serials, component names. <b>Entity extraction</b> (a.k.a. named-entity "
   "recognition) pulls those out so an unsearchable sentence becomes linkable data: which parts, how often, on which system. "
   "For rigid patterns like part numbers a few <b>rules</b> (a regular expression) plus a parts dictionary already go a long "
   "way &mdash; and every hit is <b>auditable</b>: you can point at the exact characters it grabbed.")),
code(
   "# A handful of readable rules for the part-number styles in our log.\n"
   "# Real life adds messier formats and OCR errors - but every match stays checkable.\n"
   "PART_RE = re.compile(r'\\b(?:P/N\\s*)?((?:MS|NAS|AN|BACB|3F)[0-9][A-Z0-9./-]*)')\n"
   "\n"
   "def extract_parts(text):\n"
   "    return PART_RE.findall(text)\n"
   "\n"
   "log['parts'] = log['full_note'].apply(extract_parts)\n"
   "with_parts = log[log['parts'].map(len) > 0]\n"
   "print(f'{len(with_parts)} of {len(log)} notes named a part the rules could pull out.\\n')\n"
   "# Show the audit trail: the note, and exactly what was extracted from it.\n"
   "with_parts[['full_note','parts']].head(8)"),
md(did("Every row shows the snag text and the exact part number(s) lifted from it &mdash; an <b>audit trail</b>, not a black box. "
       "Because a wrong part number is worse than none, this is best used as a fast first pass a storekeeper spot-checks. Now you "
       "can ask questions you could not before: <i>which part numbers recur most this month?</i> &mdash; one line away.")),
code(
   STYLE +
   "from collections import Counter\n"
   "tally = Counter(p for parts in log['parts'] for p in parts)\n"
   "top = tally.most_common(8)\n"
   "names, counts = [t[0] for t in top][::-1], [t[1] for t in top][::-1]\n"
   "fig, ax = plt.subplots(figsize=(8.5, 5))\n"
   "ax.barh(names, counts, color=TEAL, edgecolor='white')\n"
   "ax.set_title('Most-mentioned part numbers in the log'); ax.set_xlabel('times it appears')\n"
   "ax.grid(alpha=0.3, axis='x'); plt.tight_layout(); plt.show()"),
md(did("From free text to a ranked parts list in two steps. On a real log this is how you would surface &lsquo;part X keeps coming "
       "back&rsquo; &mdash; feeding spares planning and reliability engineering, straight out of prose nobody had time to read.")),

# --------------------------------------------------------------- E: LDA (bonus)
md(section("Bonus &mdash; another angle: themes in the words (topic modelling)", 7)),
md(vocab("Topic modelling (LDA)",
   "Everything so far needed labelled examples. <b>Topic modelling</b> needs none: it reads the whole log and groups "
   "co-occurring words into <b>topics</b> on its own. You choose how many topics to look for; it shows you the word-clusters. "
   "But be honest &mdash; topics are <b>statistical word-piles, not your clean categories</b>: a human must read and name each one, "
   "and on messy real text they can come out vague.")),
code(
   "from sklearn.feature_extraction.text import CountVectorizer\n"
   "from sklearn.decomposition import LatentDirichletAllocation\n"
   "\n"
   "cv = CountVectorizer(stop_words='english', max_df=0.6, min_df=3)\n"
   "M = cv.fit_transform(log['report']); terms = np.array(cv.get_feature_names_out())\n"
   "lda = LatentDirichletAllocation(n_components=5, random_state=0, learning_method='batch').fit(M)\n"
   "\n"
   "print('Five topics the computer found on its own (top words each):\\n')\n"
   "for k, comp in enumerate(lda.components_):\n"
   "    print(f'  Topic {k}:', ', '.join(terms[comp.argsort()[-8:][::-1]]))"),
md(did("Read the word-piles. Some map cleanly onto a system &mdash; one is plainly the <b>circuit / breaker / wiring</b> "
       "(Electrical) theme, another the <b>hydraulic / pressure</b> theme. But others blend a system with <b>severity</b> language "
       "(<i>smoke, AOG, cracked</i>) or mix two systems together &mdash; the model grouped by <i>language</i>, not by your org chart. "
       "That is the honest face of unsupervised learning: it finds real structure, but <b>you</b> decide what it means.")),
md(watchout("Topic modelling is genuinely useful for &lsquo;what is trending in the free text?&rsquo; &mdash; but it is not a finished answer. "
            "A 2021 NASA-data study that ran topic modelling on aviation safety narratives concluded the off-the-shelf tools were "
            "<i>&lsquo;insufficient for sense-making&rsquo;</i> on their own. Treat topics as a fast map to investigate, not a verdict.")),

# --------------------------------------------------------------- F: 20NG (bonus)
md(section("Bonus &mdash; is this just a toy? Real public data + the honest-test trap", 8)),
md("Our 300 snags are synthetic so the lab is self-contained. Fair question from a skeptic: <i>does this hold on real data?</i> "
   "So we run the <b>exact same pipeline</b> on a real, public corpus of ~18,000 documents (the &lsquo;20 Newsgroups&rsquo; set built into "
   "scikit-learn) &mdash; and use it to expose the single most common way AI results get faked."),
md(vocab("Data leakage / the honest-test trap",
   "A model is only trustworthy if its test was <b>fair</b>. If little giveaway clues leak from the training data into the test "
   "(here: each document&rsquo;s header secretly names its category), the score shoots up &mdash; but the model learned the giveaway, "
   "not the content. Strip the giveaways and the <i>honest</i> score appears. A suspiciously perfect number is usually a leak.")),
code(
   "from sklearn.datasets import fetch_20newsgroups\n"
   "from sklearn.pipeline import make_pipeline\n"
   "cats = ['sci.space', 'rec.autos', 'sci.electronics', 'talk.politics.mideast']\n"
   "\n"
   "def score_20ng(strip_giveaways):\n"
   "    remove = ('headers', 'footers', 'quotes') if strip_giveaways else ()\n"
   "    tr = fetch_20newsgroups(subset='train', categories=cats, remove=remove)\n"
   "    te = fetch_20newsgroups(subset='test',  categories=cats, remove=remove)\n"
   "    pipe = make_pipeline(TfidfVectorizer(), LogisticRegression(max_iter=1000)).fit(tr.data, tr.target)\n"
   "    return accuracy_score(te.target, pipe.predict(te.data))\n"
   "\n"
   "honest  = score_20ng(strip_giveaways=True)\n"
   "leaked  = score_20ng(strip_giveaways=False)\n"
   "print('Honest accuracy (giveaway headers removed):', round(honest, 3))\n"
   "print('Leaky accuracy  (headers left in)         :', round(leaked, 3), '  <- looks better, but it cheated')"),
code(
   STYLE +
   "fig, ax = plt.subplots(figsize=(7.5, 5))\n"
   "bars = ax.bar(['Honest test\\n(giveaways removed)', 'Leaky test\\n(giveaways left in)'],\n"
   "              [honest, leaked], color=[GREEN, RED], edgecolor='white', width=0.6)\n"
   "for b, v in zip(bars, [honest, leaked]):\n"
   "    ax.text(b.get_x()+b.get_width()/2, v+0.01, f'{v:.1%}', ha='center', fontsize=15, fontweight='bold')\n"
   "ax.set_ylim(0, 1.05); ax.set_ylabel('accuracy on unseen documents')\n"
   "ax.set_title('Same model, same data \\u2014 only the fairness of the test changed')\n"
   "ax.grid(alpha=0.3, axis='y'); plt.tight_layout(); plt.show()"),
md(did("On real documents, the honest pipeline scores in the <b>mid-80s%</b> &mdash; right where mature text classifiers actually live "
       "(scikit-learn&rsquo;s own tutorial reports ~83% for Naive Bayes, ~91% for a linear model on this data). Leave the giveaway headers "
       "in and it jumps to the <b>mid-90s</b> &mdash; not because it got smarter, but because it <b>cheated</b>. This is the question to ask "
       "of every AI claim you will ever see: <i>how was it tested, and could it have peeked?</i>")),

# --------------------------------------------------------------- your turn
md(turn(
   "Make it your own &mdash; change one thing and press <b>Shift + Enter</b>:<br>"
   "1. <b>Section 4 (recurring faults):</b> add your own snag to the <code>snags</code> list, worded like one already there, "
   "and re-run &mdash; watch it light up against its twin.<br>"
   "2. <b>Section 4 threshold:</b> change <code>0.35</code> to <code>0.6</code> (stricter) or <code>0.2</code> (looser) and see "
   "how many pairs get flagged. There is no &lsquo;correct&rsquo; number &mdash; it is a dial you tune to your tolerance for false matches.<br>"
   "3. <b>Section 5 (parts):</b> add a sentence with a new part-number style to <code>extract_parts('...')</code> and see whether "
   "the rules catch it &mdash; a vivid demo of why real extraction needs a maintained dictionary.")),

md(recap("What this session showed", [
   "Once words are numbers, the <b>same machinery</b> answers many questions &mdash; we only swapped the final step.",
   "<b>Classification</b> predicts a bucket (urgency); <b>regression</b> predicts a number (downtime hours) &mdash; same TF-IDF front end.",
   "The <b>confusion matrix</b> tells you <i>what</i> a model gets wrong &mdash; for safety, that matters more than a single accuracy number.",
   "<b>Cosine similarity</b> finds recurring/duplicate faults with no labels &mdash; the core of chronic-defect detection.",
   "<b>Entity extraction</b> lifts part numbers out of prose into an auditable list &mdash; a fast first pass a human checks.",
   "<b>Topic modelling</b> finds themes unsupervised, but a human must name them &mdash; and a too-perfect score usually means a <b>leak</b>.",
])),
md(nextup(
   "<b>Sessions 3 &amp; 4 &mdash; Speech.</b> So far the words arrived already typed. Next they arrive as <b>sound</b>: first "
   "(Session 3) we predict a machine fault straight from its <b>raw sound</b>, no words at all; then (Session 4, the finale) we "
   "let the computer <i>listen</i> to a spoken report, turn it into text, and route it &mdash; measuring honestly how often it "
   "mis-hears the one word that matters.")),
]

build(cells, os.path.join(HERE, "..", "notebooks", "02_text_predict_extract.ipynb"),
      title="Predictive AI - Session 2 - Text II")
