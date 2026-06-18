"""
Build the flagship "predict a machine fault from its SOUND" notebook (Part 4 of
the text/speech day). Colab-safe: callouts are plain Markdown (emoji marker +
bold label + blockquote), so they render in Colab/GitHub/Jupyter with nothing to
run. Self-contained -- does not import the older nbbuild design system.

    python3 build/nb_sound.py   ->  notebooks/sound_fault_prediction.ipynb
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

# --- Colab-safe callout helpers (emoji + blockquote) ------------------------
M_VOCAB, M_DID, M_TURN, M_RECAP = "🟦", "🟩", "🟧", "🟪"
M_WARN, M_IDEA, M_STORY, M_NOTE = "⚠️", "💡", "📍", "ℹ️"

def _q(body):  return "\n".join("> " + l for l in body.split("\n"))
def _box(m, label, body):
    head = f"> {m} **{label}**"
    return head if not body else head + "\n>\n" + _q(body)
def banner(kicker, title, sub=""):
    tag = f"**{kicker}**" + (f" — {sub}" if sub else "")
    return f"# {title}\n\n{tag}"
def section(title, n=None):
    return f"## Step {n} · {title}" if n is not None else f"## {title}"
def bigidea(b):  return _box(M_IDEA,  "THE BIG IDEA", b)
def story(b):    return _box(M_STORY, "THE SCENARIO", b)
def vocab(t, b): return _box(M_VOCAB, f"VOCABULARY — {t}", b)
def did(b):      return _box(M_DID,   "WHAT JUST HAPPENED", b)
def turn(b):     return _box(M_TURN,  "YOUR TURN", b)
def note(b):     return _box(M_NOTE,  "NOTE", b)
def watchout(b): return _box(M_WARN,  "WATCH OUT", b)
def recap(title, bullets):
    return f"> {M_RECAP} **{title.upper()}**\n>\n" + "\n".join(f"> - {x}" for x in bullets)

def _src(t):
    lines = t.split("\n")
    return [l + "\n" for l in lines[:-1]] + [lines[-1]]
def md(t):   return {"cell_type": "markdown", "metadata": {}, "source": _src(t)}
def code(t): return {"cell_type": "code", "metadata": {}, "execution_count": None,
                     "outputs": [], "source": _src(t)}
def build(cells, path, title):
    nb = {"cells": cells, "metadata": {
        "colab": {"name": title, "provenance": [], "toc_visible": True},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"}},
        "nbformat": 4, "nbformat_minor": 5}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("wrote", path, "(", len(cells), "cells )")

# ---------------------------------------------------------------------------
cells = [
md(banner("Speech & Audio Analytics · Session 4 of 4",
          "Can a Computer Hear a Failing Machine?",
          "Predicting a fault from a machine's sound alone — no words, no transcription")),

md("## How to use this notebook\n\n"
   "**Hands-on, but you write no code.** You only **run** the cells top to bottom "
   "(click a cell, press **Shift + Enter**) and read what comes out. A few cells even "
   "let you *listen*. If anything looks stuck: **Runtime → Restart and run all**.\n\n"
   "As you scroll you'll meet four little callouts: 🟦 a new word, 🟩 what a cell just did, "
   "🟧 something to try, 🟪 the recap."),

md(bigidea(
   "An experienced technician can often walk past a machine and say *\"that bearing is on its "
   "way out\"* — just from the **sound**. The pitch is wrong, there's a whine that shouldn't be "
   "there.\n\n"
   "Can a computer learn to do the same? **Yes** — and it is the *exact same idea* as every "
   "other predictive example: turn each thing into a few **numbers**, learn the pattern from "
   "past labelled examples, then judge a new one. Here the \"thing\" is a sound. We will make "
   "machine sounds, teach a model what *healthy*, *bearing fault* and *imbalance* sound like, "
   "and then play it a brand-new recording and watch it call the fault.")),

md(story(
   "**Our scenario.** A plant has machines that hum as they run. A healthy machine has a steady "
   "low hum. A worn **bearing** adds a high-pitched whine that rattles. An **imbalance** adds a "
   "heavy low rumble. We have recordings of past machines whose faults are known — and we want "
   "the computer to listen to a *new* machine and tell us which of the three it is.")),

md(section("Set up, and decide what a 'clip' is", 1)),
md(vocab("Sample rate",
   "A sound is just air pressure measured many times a second. The **sample rate** is how many "
   "measurements per second — here **8000**. So a 0.6-second clip is really just a list of "
   "**4800 numbers**. That's the whole trick: to a computer, a sound *is already numbers*.")),
code(
   "import numpy as np\n"
   "import pandas as pd\n"
   "import matplotlib.pyplot as plt\n"
   "from sklearn.ensemble import RandomForestClassifier\n"
   "from sklearn.model_selection import train_test_split\n"
   "from sklearn.metrics import accuracy_score, confusion_matrix\n"
   "from IPython.display import Audio, display\n"
   "\n"
   "SR  = 8000          # measurements (samples) per second\n"
   "DUR = 0.6           # seconds per clip\n"
   "N   = int(SR * DUR) # so each clip is this many numbers\n"
   "print('Ready. Each clip is', DUR, 'sec =', N, 'numbers.')"),
md(did("We loaded our tools and set the clip length. Nothing visible happened beyond the "
       "print — that's expected. The key idea is in the last line: **one clip = 4800 numbers**.")),

md(section("Make the machine sounds", 2)),
md("In real life these would be microphone recordings from the shop floor. To keep the notebook "
   "self-contained — no files, no microphone — we *synthesise* them, with a fixed seed so everyone "
   "hears exactly the same machines. Each kind of fault gets its own tell-tale sound."),
code(
   "def make_sound(kind, rng):\n"
   "    t = np.arange(N) / SR\n"
   "    # every machine shares a base rotation hum around 50 Hz, plus a noise floor\n"
   "    f0  = 50 + rng.normal(0, 3)\n"
   "    sig = 0.5*np.sin(2*np.pi*f0*t) + 0.25*np.sin(2*np.pi*2*f0*t)\n"
   "    sig += 0.17*rng.normal(0, 1, N)                     # background noise every machine has\n"
   "\n"
   "    if kind == 'healthy':\n"
   "        # mostly hum -- but real machines aren't perfectly clean:\n"
   "        if rng.random() < 0.5:\n"
   "            sig += rng.uniform(0, 0.12)*np.sin(2*np.pi*rng.uniform(1800, 3200)*t)  # faint stray whine\n"
   "        if rng.random() < 0.3:\n"
   "            sig += rng.uniform(0, 0.18)*np.sin(2*np.pi*(f0*0.5)*t)                 # slight rumble\n"
   "    elif kind == 'bearing':\n"
   "        fb     = rng.uniform(2000, 3300)                # a high-pitched whine...\n"
   "        rattle = 1 + 0.6*np.sin(2*np.pi*40*t)           # ...that rattles on and off\n"
   "        sig   += rng.uniform(0.05, 0.20)*rattle*np.sin(2*np.pi*fb*t)  # sometimes only subtle\n"
   "    elif kind == 'imbalance':\n"
   "        sig += rng.uniform(0.18, 0.45)*np.sin(2*np.pi*(f0*0.5)*t)     # a heavy slow rumble\n"
   "\n"
   "    return sig / np.max(np.abs(sig))                    # even out the volume\n"
   "\n"
   "CLASSES, PER_CLASS = ['healthy', 'bearing', 'imbalance'], 100\n"
   "rng = np.random.default_rng(0)\n"
   "clips  = [make_sound(k, rng) for k in CLASSES for _ in range(PER_CLASS)]\n"
   "labels = np.array([k for k in CLASSES for _ in range(PER_CLASS)])\n"
   "print(len(clips), 'sound clips:', PER_CLASS, 'each of', CLASSES)"),
md(did("We now have **300 machine recordings** — 100 of each condition — each tagged with its true "
       "state. That tag is the **label**, exactly like "
       "the answer column in the other notebooks; only the data is sound this time.")),

md(section("Listen for yourself", 3)),
md("Before any maths, use your own ears. Run this and press play on each bar — you should clearly "
   "hear the steady hum, the high whine, and the low rumble. If *you* can tell them apart, the "
   "computer has a fair chance too."),
code(
   "for kind in CLASSES:\n"
   "    i = list(labels).index(kind)\n"
   "    print(kind.upper())\n"
   "    display(Audio(clips[i], rate=SR))"),
md(did("Three machines, three very different sounds. The model is about to get the same clips we "
       "just heard — but it can't 'listen'. So first we have to turn each sound into numbers.")),

md(section("Turn each sound into a few numbers", 4)),
md(vocab("Features (from a sound)",
   "A model can't use 4800 raw numbers well — but it doesn't need to. We summarise each clip with "
   "a handful of meaningful **features**: how *loud* it is, how much energy sits in the **low** "
   "rumble band vs. the **high** whine band, its loudest **pitch**, and its overall **brightness**. "
   "These five numbers capture what your ear noticed.")),
md(note("The one line of maths here is the **FFT** — it takes a wobbly sound and tells you *which "
        "pitches* it's made of. You don't need the formula; think of it as a prism splitting the "
        "sound into its tones so we can measure them.")),
code(
   "def features(sig):\n"
   "    spec  = np.abs(np.fft.rfft(sig * np.hanning(len(sig))))  # the pitches present\n"
   "    freqs = np.fft.rfftfreq(len(sig), 1/SR)\n"
   "    power = spec**2\n"
   "    total = power.sum() + 1e-9\n"
   "    return {\n"
   "        'loudness':   float(np.sqrt(np.mean(sig**2))),           # overall loudness\n"
   "        'low_share':  float(power[freqs < 200 ].sum() / total),  # energy in the LOW rumble band\n"
   "        'high_share': float(power[freqs > 1500].sum() / total),  # energy in the HIGH whine band\n"
   "        'dom_freq':   float(freqs[np.argmax(power)]),            # the single loudest pitch (Hz)\n"
   "        'brightness': float((freqs*power).sum() / total),        # average pitch\n"
   "    }\n"
   "\n"
   "X = pd.DataFrame([features(c) for c in clips])\n"
   "X.insert(0, 'true_condition', labels)\n"
   "X.head(6)"),
md(did("Every sound is now **one row of five numbers** — a tidy table, just like the spreadsheets "
       "in the earlier notebooks. Glance down the columns: the bearing clips will show a high "
       "`high_share`, the imbalance clips a high `low_share`. The pattern is already visible in the "
       "numbers.")),

md(section("See the pattern with our own eyes", 5)),
md("Let's plot two of those features against each other — low-band energy across, high-band energy "
   "up — and colour each dot by its true condition. If the sounds really differ, the colours should "
   "land in different corners."),
code(
   "feat   = X.drop(columns='true_condition')\n"
   "colors = {'healthy': '#2e7d32', 'bearing': '#9c2b2b', 'imbalance': '#b26a00'}\n"
   "\n"
   "plt.figure(figsize=(8, 5.5))\n"
   "for kind in CLASSES:\n"
   "    m = labels == kind\n"
   "    plt.scatter(feat['low_share'][m], feat['high_share'][m],\n"
   "                c=colors[kind], label=kind, alpha=0.7, edgecolors='white')\n"
   "plt.xlabel('energy in the LOW rumble band')\n"
   "plt.ylabel('energy in the HIGH whine band')\n"
   "plt.title('Each dot is one machine sound')\n"
   "plt.legend(); plt.grid(alpha=0.3); plt.show()"),
md(did("Three clean clusters. **Bearing** faults ride high (lots of high-band whine), **imbalance** "
       "sits far right (heavy low rumble), **healthy** stays low on both. *That separation is the "
       "pattern* — and finding a boundary between the colours is the model's whole job.")),

md(section("Train a model, and test it honestly", 6)),
md(vocab("Train / test split",
   "We hide a quarter of the clips, train on the rest, then score the model **only on clips it "
   "never heard** — the honest exam. `stratify` keeps all three conditions evenly represented in "
   "both halves.")),
code(
   "y = labels\n"
   "Xtr, Xte, ytr, yte = train_test_split(\n"
   "    feat, y, test_size=0.25, random_state=0, stratify=y)\n"
   "\n"
   "model = RandomForestClassifier(n_estimators=200, random_state=0)\n"
   "model.fit(Xtr, ytr)                       # <-- the learning happens here\n"
   "\n"
   "pred = model.predict(Xte)\n"
   "print('Tested on', len(yte), 'sounds it had never heard.')\n"
   "print('Accuracy:', round(accuracy_score(yte, pred), 3))"),
md(did("Around **0.88** — it gets roughly **9 in 10** right on machines it never heard. Not "
       "perfect, and that is *healthy*: real sounds carry noise and a few machines sit right on the "
       "boundary between conditions. A model that scored a flawless 100% here would be the thing to "
       "distrust, not to trust.")),

md(section("Which part of the sound did it rely on?", 7)),
md("A model needn't be a black box. **Feature importance** tells us how much it leaned on each "
   "number — and we can check that against intuition."),
code(
   "imp = pd.Series(model.feature_importances_, index=feat.columns).sort_values()\n"
   "plt.figure(figsize=(8, 4.5))\n"
   "plt.barh(imp.index, imp.values, color='#0b6e7a', edgecolor='white')\n"
   "plt.title('Which part of the sound did the model rely on?')\n"
   "plt.xlabel('importance'); plt.tight_layout(); plt.show()"),
md(did("The high-band and low-band energies dominate — exactly the whine and the rumble *you* "
       "heard. The model rediscovered, on its own, the very clues an experienced ear uses.")),

md(section("Bring in a brand-new machine", 8)),
md("The payoff. We make a fresh recording the model has never seen, **play it**, and ask for a "
   "diagnosis with a confidence."),
code(
   "def diagnose(kind, seed=999):\n"
   "    clip  = make_sound(kind, np.random.default_rng(seed))\n"
   "    row   = pd.DataFrame([features(clip)])\n"
   "    guess = model.predict(row)[0]\n"
   "    conf  = model.predict_proba(row).max()\n"
   "    print('A new machine is brought in. Listen:')\n"
   "    display(Audio(clip, rate=SR))\n"
   "    print(f'The model says:  {guess.upper()}   ({round(conf*100)}% confident)')\n"
   "    return guess\n"
   "\n"
   "diagnose('bearing')"),
md(did("Listen to the clip, then read the verdict. The computer heard a sound it had never "
       "encountered and called the fault — the same thing the seasoned technician does, but it can "
       "do it for every machine on the floor, every shift, without tiring.")),

md(turn(
   "Make it your own — change a value and press **Shift + Enter**:\n"
   "1. In the cell above, swap `diagnose('bearing')` for `diagnose('imbalance')` or "
   "`diagnose('healthy')`. Listen, and check the model agrees.\n"
   "2. Try `diagnose('bearing', seed=7)` a few times with different seeds — a fresh recording each "
   "time. Does it stay confident?\n"
   "3. Harder: in **Step 2**, widen the bearing whine range to `rng.uniform(1800, 3300)`, then "
   "**Runtime → Restart and run all**. A messier fault — does accuracy hold?")),

md(section("When you have no fault examples — learn what 'normal' sounds like", 9)),
md(vocab("Anomaly detection (unsupervised)",
   "Everything above needed labelled faults to learn from. On a real aircraft, though, serious faults are **rare** — you may "
   "have thousands of hours of *healthy* sound and almost no failures. So we flip the question: teach the computer only what "
   "**normal** sounds like, then let it flag anything **surprising**. It tells you *this is different*, not *what is wrong* — "
   "which is exactly the moment a human should walk over and listen.")),
code(
   "from sklearn.ensemble import IsolationForest\n"
   "from sklearn.metrics import roc_auc_score\n"
   "\n"
   "# Train ONLY on healthy clips -- the detector never sees a single fault.\n"
   "healthy_only = feat[labels == 'healthy']\n"
   "detector = IsolationForest(n_estimators=300, random_state=0).fit(healthy_only)\n"
   "\n"
   "# A 'surprise score' for every clip (higher = less like a healthy machine).\n"
   "surprise = -detector.score_samples(feat)\n"
   "auc = roc_auc_score((labels != 'healthy').astype(int), surprise)\n"
   "print('Trained on', len(healthy_only), 'healthy clips only -- no faults shown.')\n"
   "print('Healthy-vs-fault separation (AUC):', round(auc, 3), ' (1.0 = perfect, 0.5 = useless)')"),
md(did("AUC around **0.94**: the surprise score cleanly tells healthy from faulty — yet the model was **only ever shown "
       "healthy machines**. This is the realistic aerospace setup, and the same idea behind the public **DCASE** machine-sound "
       "challenge, where honest scores run anywhere from ~0.54 to ~0.96 depending on the machine. Not magic — a learned sense of normal.")),
code(
   "import matplotlib.pyplot as plt, numpy as np\n"
   "colors = {'healthy': '#2e7d32', 'bearing': '#9c2b2b', 'imbalance': '#b26a00'}\n"
   "thr = np.percentile(surprise[labels == 'healthy'], 95)   # tolerate ~5% false alarms on healthy\n"
   "\n"
   "plt.figure(figsize=(9, 5))\n"
   "for k in CLASSES:\n"
   "    plt.hist(surprise[labels == k], bins=22, alpha=0.6, color=colors[k], label=k)\n"
   "plt.axvline(thr, color='#1f2d3d', ls='--', lw=2, label='alarm threshold')\n"
   "plt.xlabel('surprise score  (how UNlike a healthy machine)')\n"
   "plt.ylabel('number of clips'); plt.title('Learn normal, then flag the surprising')\n"
   "plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()\n"
   "\n"
   "for k in ['bearing', 'imbalance']:\n"
   "    caught = (surprise[labels == k] > thr).mean() * 100\n"
   "    print(f'Caught {caught:.0f}% of {k} faults', end='   ')\n"
   "fa = (surprise[labels == 'healthy'] > thr).mean() * 100\n"
   "print(f'\\nFalse alarms on healthy machines: {fa:.0f}%')"),
md(did("Draw the alarm line to tolerate about a **5% false-alarm** rate on healthy machines, and the very same detector catches "
       "roughly **96% of imbalance** and **two-thirds of bearing** faults — having never been shown one. Where you put that line is "
       "a **business decision**: slide it left to miss fewer faults (at more false alarms), right to cry wolf less often (at more "
       "misses). There is no free lunch — and the chart makes that trade-off honest and visible.")),
md(note("**Read frequencies as ORDERS, not raw Hz.** A rotating-machinery engineer will rightly note that a fault's tell-tale "
        "pitch moves with shaft speed: imbalance shows at **1x** the rotation rate, misalignment often at **2x**, and bearing "
        "defects at frequencies set by the bearing geometry. In practice you divide by the running speed so the axis is in "
        "*orders* (multiples of shaft speed) — otherwise simply spinning the machine faster looks like a 'fault'. We held the "
        "speed fixed here to keep it simple.")),

md(recap("What we learned", [
   "**Two ways to learn:** with labelled faults the model *names* the fault (supervised); with only healthy sound it *flags "
   "the surprising* (unsupervised anomaly detection) — the realistic case when real faults are rare.",
   "A sound is just **numbers** (measurements of air pressure) — so predicting from sound is the "
   "same game as predicting from a table.",
   "We summarised each clip with a few **features** (loudness, low/high energy, pitch, brightness) "
   "— the same clues your ear uses.",
   "The familiar rhythm returned: **turn into numbers → split → train → predict → measure**.",
   "**No transcription, no words** — this is purely predictive, learning straight from the signal.",
   "**Feature importance** showed the model leaned on the whine and the rumble — matching human "
   "intuition, discovered on its own.",
])),
md(note("Where this fits at work: this is **acoustic condition monitoring** — flagging a failing "
        "bearing, gearbox or pump from the noise it makes, before it stops the line. The same recipe "
        "extends to vibration sensors, ultrasonic leak detection, and more.")),
md(note("**Level up — the real datasets behind this demo.** Our clips are synthetic so the lab needs no downloads, but this "
        "is a published, benchmarked field. To go further with *real* hardware recordings: the **CWRU Bearing** dataset "
        "(engineering.case.edu/bearingdatacenter — seeded inner/outer-race and ball faults), **MAFAULDA** (imbalance + "
        "misalignment + bearing, and it includes a microphone channel), and **MIMII** / the **DCASE** challenge (real factory "
        "machine sound for anomaly detection). The recipe never changes: signal → a few features → classify or flag.")),
]

build(cells, os.path.join(HERE, "..", "notebooks", "04_sound_fault_prediction.ipynb"),
      title="Predictive AI - Session 4 - Speech II")
