# Predictive AI — Hands-on Lab (Instructor Guide)

A full-day, no-code lab that introduces **predictive AI** to core engineers with no IT
background. Six Google Colab notebooks take a single idea — *learn the pattern from past
examples, then predict the next case* — across three kinds of data: numbers, text, and speech.

**For the presenter:**
- `slides.html` — the **presentation deck** (open fullscreen in a browser to present).
- `SPEAKER_NOTES.md` — printable per-slide presenter script (also built into the deck; press **S**).
- `index.html` — the session **landing page** (a one-screen overview to project or share).

**For the participants (take-home):**
- `Predictive-AI-Field-Guide.pdf` — a **12-page illustrated reference** to keep: the ideas, the
  charts, a glossary, and "where to use this" notes. Rendered from `reference_guide.html`.
- `handout.html` — a one-page quick-reference cheat-sheet (print it).

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

| # | Notebook | What it teaches | Live result | Open |
|---|----------|-----------------|-------------|------|
| 00 | `00_intro_predictive_ai.ipynb` | The mindset + core vocabulary (dataset, label column, train/test split, accuracy) on a tiny equipment example | Decision tree, ~87% on unseen machines | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zerotoprod-5/HAL-AI-Tutorial/blob/main/notebooks/00_intro_predictive_ai.ipynb) |
| 01 | `01_classification.ipynb` | Sorting into categories; the **accuracy trap**; confusion matrix; precision & recall | 93% acc, catches rare rejects | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zerotoprod-5/HAL-AI-Tutorial/blob/main/notebooks/01_classification.ipynb) |
| 02 | `02_regression_forecasting.ipynb` | Predicting **numbers** (regression) and **trends over time** (forecasting) | Cost ±₹1,100; 6-month demand forecast | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zerotoprod-5/HAL-AI-Tutorial/blob/main/notebooks/02_regression_forecasting.ipynb) |
| 03 | `03_predictive_maintenance.ipynb` | Capstone: catch failures early, **feature importance**, and **anomaly detection** without labels | Flags failures, ranks the sensors | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zerotoprod-5/HAL-AI-Tutorial/blob/main/notebooks/03_predictive_maintenance.ipynb) |
| 04 | `04_text_analytics.ipynb` | Turning written reports into predictions (words → numbers, TF-IDF) | Auto-routes reports to the right team | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zerotoprod-5/HAL-AI-Tutorial/blob/main/notebooks/04_text_analytics.ipynb) |
| 05 | `05_speech_analytics.ipynb` | **Speak → transcribe → predict** pipeline (Whisper ASR + text analytics) | Spoken note → category, live | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zerotoprod-5/HAL-AI-Tutorial/blob/main/notebooks/05_speech_analytics.ipynb) |

All six are **self-contained**: synthetic/in-cell data, fixed random seeds (everyone sees the
same numbers), scikit-learn only, no downloads, no API keys, no file uploads. Maths is shown
**conceptually and visually** — never an equation to recall.

Every notebook follows the same rhythm so the audience learns the *shape* of an ML project once:
> **scenario → run a cell → "what just happened" → vocabulary card → "your turn" knob → recap → what's next**

Coloured boxes guide reading: **teal** = new word, **green** = what the cell did,
**amber** = a number to change and re-run, **purple** = recap / coming up.

---

## Distributing to the lab

**One click: the Colab badges above.** Once this repo is public, each badge opens that notebook
straight from GitHub in Colab — no download, no upload. Participants click, sign in with any Google
account, and run top to bottom with **Shift + Enter**.

> While the repo is still **private**, the badges open only for you and collaborators — use the
> upload fallback below for attendees until you flip it public (Settings → change visibility).

**Fallback (locked-down network, or repo still private): upload.**
1. Each participant opens [colab.research.google.com](https://colab.research.google.com) and signs in.
2. `File → Upload notebook` → pick the `.ipynb` for the current module.
3. Run top to bottom with **Shift + Enter**.

Share the six `.ipynb` files however is easiest in the lab (USB, shared drive, intranet link, email).

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

## Lab troubleshooting (when a cell misbehaves)

With ~30 non-IT participants on Colab, small hiccups are normal. **One reset fixes almost everything:
`Runtime → Restart and run all`.** Keep that on a slide or say it often. Specific cases:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `NameError: 'X' is not defined` | Cells run out of order, or one was skipped | `Runtime → Restart and run all`, then go top to bottom |
| A cell shows a spinning circle and never finishes | Stuck cell, or waiting on a long step | `Runtime → Interrupt execution`, then re-run the cell |
| No chart appears | The imports cell (or the cell above) didn't run | Re-run from the top of that section |
| "Your session crashed / reconnect" | Idle disconnect (not memory — the data here is tiny) | Click **Reconnect**, then `Runtime → Run all` |
| Module 05 install is slow or errors | First cell downloads gTTS + Whisper over the network | Wait ~1 min; if the network blocks it, demo from your own pre-run copy and move on |
| Can't sign in to Colab | Corporate Google account restrictions | Use a personal Google account, or the upload method |
| Edited a number, results look wrong | Stale state from earlier runs | `Runtime → Restart and run all` |

Have one **pre-run copy of each notebook open on your own machine** as a backup, so if a participant's
cell breaks you can show the expected output and keep moving rather than debugging live.

## Prompts to get the room talking

The brief is conversational and application-oriented — these engineers know their machines far better
than we do, so let them connect each idea to their own work. One prompt per module:

- **After 00 (workflow):** "What records does your team already keep that look like this table — rows of cases, columns of measurements?"
- **After 01 (classification):** "Where do you make a yes/no call from a few measurements today? What would a *missed fault* cost you versus a *false alarm*?"
- **After 02 (regression/forecasting):** "What number would be useful to know a month ahead — a demand, a cost, a wear figure?"
- **After 03 (predictive maintenance):** "Which signals do you already watch that hint a machine is heading for trouble? Would knowing *which sensor mattered* change how you act?"
- **After 04 (text):** "How much useful information sits in free-text logs and reports that no one has time to read?"
- **After 05 (speech):** "Where do people *speak* information that never gets written down — handovers, inspections, calls?"
- **Closing:** "Pick one place from today where *learn from the past, predict the next case* could help. What data would you need to start?"

## Speaker notes

`SPEAKER_NOTES.md` is a printable script of the per-slide presenter cues, in deck order — handy as a
paper copy at the podium. The same notes are built into the deck (press **S** to show them on screen).

## Rebuilding / editing the notebooks

The notebooks are generated from small Python scripts that share one design system
(`nbbuild.py` — the callout boxes, banner, vocabulary cards). To tweak wording or data and
regenerate, edit the matching build script and re-run it. All six were validated by executing
every code cell end-to-end before shipping.
