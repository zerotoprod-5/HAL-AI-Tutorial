# Predictive AI — Hands-on Lab (Instructor Guide)

A full-day, no-code lab that introduces **predictive AI** to core engineers with no IT
background. Six Google Colab notebooks take a single idea — *learn the pattern from past
examples, then predict the next case* — across three kinds of data: numbers, text, and speech.

- `slides.html` — the **presentation deck** (open fullscreen in a browser to present).
- `index.html` — the session **landing page** (a one-screen overview to project or share).

### Presenting the deck (`slides.html`)

No internet or PowerPoint needed; works in any browser, offline. **Keep `slides.html` and the
`figs/` folder together** — the deck loads its charts from `figs/` by relative path.

- **Navigate:** `→` / `Space` next, `←` previous, or click the right/left half of the screen.
- **`F`** toggles fullscreen. **`S`** toggles a **speaker-notes panel** (a presenter cue per slide).
- 25 slides with illustrations throughout: a technician/analogy line drawing, icon-driven concept
  slides, a real **"find the pattern" scatter** with a decision boundary, and chart previews
  (line of best fit, forecast, feature importance) on the relevant **"Now open Module 0X"** dividers.
  The conceptual half (mindsets, predictive vs generative, the 5 core words, the workflow) sets up
  each hands-on notebook. The deck supports the talk; the notebooks carry the detail.
- The charts in `figs/` are generated from `build/make_figs.py` (same synthetic data as the
  notebooks) — edit and re-run it to change them.

---

## What's in the box

| # | Notebook | What it teaches | Live result |
|---|----------|-----------------|-------------|
| 00 | `00_intro_predictive_ai.ipynb` | The mindset + core vocabulary (dataset, label column, train/test split, accuracy) on a tiny equipment example | Decision tree, ~87% on unseen machines |
| 01 | `01_classification.ipynb` | Sorting into categories; the **accuracy trap**; confusion matrix; precision & recall | 93% acc, catches rare rejects |
| 02 | `02_regression_forecasting.ipynb` | Predicting **numbers** (regression) and **trends over time** (forecasting) | Cost ±₹1,100; 6-month demand forecast |
| 03 | `03_predictive_maintenance.ipynb` | Capstone: catch failures early, **feature importance**, and **anomaly detection** without labels | Flags failures, ranks the sensors |
| 04 | `04_text_analytics.ipynb` | Turning written reports into predictions (words → numbers, TF-IDF) | Auto-routes reports to the right team |
| 05 | `05_speech_analytics.ipynb` | **Speak → transcribe → predict** pipeline (Whisper ASR + text analytics) | Spoken note → category, live |

All six are **self-contained**: synthetic/in-cell data, fixed random seeds (everyone sees the
same numbers), scikit-learn only, no downloads, no API keys, no file uploads. Maths is shown
**conceptually and visually** — never an equation to recall.

Every notebook follows the same rhythm so the audience learns the *shape* of an ML project once:
> **scenario → run a cell → "what just happened" → vocabulary card → "your turn" knob → recap → what's next**

Coloured boxes guide reading: **teal** = new word, **green** = what the cell did,
**amber** = a number to change and re-run, **purple** = recap / coming up.

---

## Distributing to the lab

**Recommended (zero setup): upload.**
1. Each participant opens [colab.research.google.com](https://colab.research.google.com) and signs in.
2. `File → Upload notebook` → pick the `.ipynb` for the current module.
3. Run top to bottom with **Shift + Enter**.

Share the six `.ipynb` files however is easiest in the lab (USB, shared drive, intranet link, email).

**Optional (one-click badges): host on GitHub.**
Push the `notebooks/` folder to a repo, then a *Open in Colab* link is:
```
https://colab.research.google.com/github/<org>/<repo>/blob/main/notebooks/00_intro_predictive_ai.ipynb
```

---

## Pre-flight checklist (do this the day before)

- [ ] Run **Module 05** end-to-end yourself once. Its first cell `!pip install -q gTTS openai-whisper`
      takes ~1 minute and downloads the Whisper "tiny" model on first transcription — confirm the
      lab's network allows it. (Everything else needs no install.)
- [ ] Confirm the lab machines can reach Google Colab and `pypi.org` / model downloads.
- [ ] Have the six files ready on a shared location, named in order so people don't get lost.
- [ ] Decide your fallback: if a participant's cell errors after editing, the reset is
      **Runtime → Restart and run all**.

---

## Suggested full-day flow

Adjust freely — the modules are independent after 00. Keep 00 first; it installs the vocabulary
everything else leans on.

| Time | Block | Notes |
|------|-------|-------|
| 09:30 | Director: *What is AI?* | The framing intro |
| 10:00 | **Module 00 — What is Predictive AI?** (~45 min) | Slow and careful; this is the vocabulary foundation |
| 10:50 | Break | |
| 11:05 | **Module 01 — Classification** (~45 min) | Spend time on the accuracy trap + confusion matrix |
| 11:55 | **Module 02 — Regression & Forecasting** (~40 min) | The two "aha" visuals: the fitted line and the forecast |
| 12:35 | Lunch | |
| 13:45 | **Module 03 — Predictive Maintenance** (~50 min) | The payoff module; feature-importance chart lands well |
| 14:40 | **Module 04 — Text Analytics** (~40 min) | The new idea is "words become numbers" |
| 15:25 | Break | |
| 15:40 | **Module 05 — Speech Analytics** (~40 min) | The showpiece; let people edit the spoken sentence |
| 16:25 | Wrap-up + Q&A | Tie all six to one idea; point to the generative-AI sessions to come |

---

## Talking points per module

**00 — What is Predictive AI?**
Open by naming the two mindsets in the room — "AI can do anything" and "AI is nonsense" — and
promise that the truth is more ordinary and more useful than either. The anchor analogy: a seasoned
technician who has inspected thousands of machines and can call a bad one on sight — not magic, just
*pattern from experience*. The big reveal is `export_text` printing the if-then rules the tree wrote
**by itself**: nobody programmed them. Stress *predictive vs generative* here so nobody confuses this
with ChatGPT.

**01 — Classification.**
The lesson that earns the day: a "lazy" model that always says PASS scores 80% accuracy yet catches
**zero** bad parts. Let that land before showing the real model. Then the confusion matrix in plain
words — *false alarm* (good part rejected) vs *missed fault* (bad part passed) — and why, for safety,
the missed fault (recall) is the number that matters. This reframes "accuracy" as not enough.

**02 — Regression & Forecasting.**
Point: prediction isn't only yes/no — often you predict a *number*. The fitted line *through* the dot
cloud makes "the model learned the relationship" visible. For forecasting, the dashed line continuing
past "today" is the moment. Be honest: forecasts get fuzzier further out — planners add a safety margin.

**03 — Predictive Maintenance.**
This is the one they'll remember as "useful for us." Old way = fix-on-break or fixed schedule; new way
= service the machines the data says are at risk. The feature-importance bar chart is gold for engineers:
the model doesn't just say *will fail* — it says *vibration mattered most*, which they can sanity-check
against intuition. The anomaly-detection coda answers the obvious objection "but we don't have failure
labels" — show AI finding the weird machines with no labels at all.

**04 — Text Analytics.**
The only genuinely new concept is *turning words into numbers* — show the actual word-columns appear,
with common words ("the", "and") dropped. After that it's the same classify-workflow from 01. The
per-team top words (oil/pressure/fluid → Hydraulic) prove the model learned something human-readable.

**05 — Speech Analytics.**
The finale and the crowd-pleaser. gTTS fabricates a spoken report so no microphone is needed; Whisper
transcribes it; the text classifier routes it. The invitation in *Your turn* — change the spoken
sentence and watch speak → transcribe → categorize run again — is the most "wow" moment. Close the
whole day on the one consistent idea: whether the data was numbers, text, or speech, AI did the same
thing — *learned the pattern from past examples, then predicted the next case.*

---

## Handling the skeptics (and the over-believers)

- **"This is just if-then rules / statistics."** Yes — and that's the point. Predictive AI *is*
  disciplined pattern-finding. Module 00's printed tree rules make this concrete and disarm the hype.
- **"Why isn't it 100% accurate?"** Because real data has surprises. A model claiming 100% is usually
  cheating (it saw the test answers). Honest, imperfect numbers are a feature of these notebooks.
- **"Can it replace our engineers?"** Module 03's feature importance reframes it: AI gives engineers a
  *prioritized list and a reason*, then a human decides. It scales judgment, it doesn't replace it.
- **"AI can do anything."** Point at the missed faults in Module 01 and the forecast caveat in 02 — it
  is a tool with limits you can measure, which is exactly why it's trustworthy.

---

## Rebuilding / editing the notebooks

The notebooks are generated from small Python scripts that share one design system
(`nbbuild.py` — the callout boxes, banner, vocabulary cards). To tweak wording or data and
regenerate, edit the matching build script and re-run it. All six were validated by executing
every code cell end-to-end before shipping.
