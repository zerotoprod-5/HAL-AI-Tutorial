# Predictive AI — Hands-on Lab (Instructor Guide)

A full-day, no-code lab that introduces **predictive AI** to core engineers with no IT
background. Four Google Colab notebooks take a single idea — *learn the pattern from past
examples, then predict the next case* — across the two kinds of messy data engineers handle
daily: written **text** (Sessions 1–2) and spoken **speech** (Session 3 sound, Session 4
speech-to-text).

> **Running the text + speech day?** `LESSON_PLAN.md` is the detailed **four-session** teaching plan (~75 min per session)
> — per-session timings, demos, case studies (with honest caveats and sources),
> discussion prompts and skeptic-handling — rendered to **`Predictive-AI-Lesson-Plan.pdf`** for sharing.

**For the presenter:**
- `slides.html` — the **presentation deck** (open fullscreen in a browser to present).
- `SPEAKER_NOTES.md` — printable per-slide presenter script (also built into the deck; press **S**).
- `index.html` — the session **landing page** (a one-screen overview to project or share).

**For the participants (take-home):**
- `Predictive-AI-Field-Guide.pdf` — an **illustrated reference** to keep, one part per session: the
  ideas, the charts, a glossary, and "where to use this" notes. Rendered from `reference_guide.html`
  (light-theme charts from `build/make_print_figs_textspeech.py`).
- `handout.html` — a one-page quick-reference cheat-sheet (print it).

### Presenting the deck (`slides.html`)

No internet or PowerPoint needed; works in any browser, offline. **Keep `slides.html` and the
`figs/` folder together** — the deck loads its charts from `figs/` by relative path.

- **Navigate:** `→` / `Space` next, `←` previous, or click the right/left half of the screen.
- **`F`** toggles fullscreen. **`S`** toggles a **speaker-notes panel** (a presenter cue per slide).
- 28 slides with illustrations throughout: a technician/analogy line drawing, icon-driven concept
  slides, a real **"find the pattern" scatter** with a decision boundary, and chart previews
  (clue-words, similarity heatmap, sound clusters, anomaly histogram) on the relevant
  **"Now open — Session N"** dividers. The conceptual half (mindsets, predictive vs generative,
  the core words, the five-step workflow) sets up each hands-on notebook. The deck supports the
  talk; the notebooks carry the detail.
- The charts in `figs/` are generated from `build/make_figs_textspeech.py` (same synthetic data as
  the notebooks) — edit and re-run it to change them.

---

## What's in the box

Four notebooks, one per session — **two text, then two speech** (Session 3 is sound,
Session 4 speech-to-text is the finale):

| # | Session | Notebook | What it teaches | Live result | Open |
|---|---------|----------|-----------------|-------------|------|
| 1 | Text I | `01_text_analytics.ipynb` | Words → numbers (bag-of-words, **TF-IDF**), then classify free-text notes as **URGENT vs ROUTINE**; **URGENT recall** as the number that matters; top clue-words per class | Flags the urgent reports; ~95% URGENT recall | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zerotoprod-5/HAL-AI-Tutorial/blob/main/notebooks/01_text_analytics.ipynb) |
| 2 | Text II | `02_text_predict_extract.ipynb` | Predict urgency (class) & downtime (regression); **recurring-fault detection**; embeddings + **k-means clustering**; part-number extraction; LDA topics; the header-trap | Similarity heatmap flags the same chronic fault, worded three different ways | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zerotoprod-5/HAL-AI-Tutorial/blob/main/notebooks/02_text_predict_extract.ipynb) |
| 3 | Speech I | `03_sound_fault_prediction.ipynb` | Sound → numbers (**FFT**, spectrogram); classify a machine fault from its sound; **feature importance**; **unsupervised anomaly detection** without labels | Three faults separate by sound; anomaly AUC ~0.94 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zerotoprod-5/HAL-AI-Tutorial/blob/main/notebooks/03_sound_fault_prediction.ipynb) |
| 4 | Speech II | `04_speech_analytics.ipynb` | **Speak → transcribe → predict** pipeline (Whisper ASR + text analytics); **Word Error Rate (WER)** and why a low error rate can still get the one critical word wrong; keyword spotting | Spoken note → category, live; a low-WER transcript that still gets one part number wrong | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zerotoprod-5/HAL-AI-Tutorial/blob/main/notebooks/04_speech_analytics.ipynb) |

All are **self-contained**: synthetic/in-cell data, fixed random seeds (everyone sees the
same numbers), scikit-learn only — with one exception, `02`, which can also fetch a small public
corpus (20 Newsgroups, ~14 MB, one line) to prove the method holds on real data. No API keys, no
file uploads (Session 4 installs gTTS + Whisper once, ~1 min). Maths is shown **conceptually and
visually** — never an equation to recall.

Every notebook follows the same rhythm so the audience learns the *shape* of an ML project once:
> **scenario → run a cell → "what just happened" → vocabulary card → "your turn" knob → recap → what's next**

The notebooks are **Colab-safe**: callouts use emoji + blockquotes (no reliance on colour),
so they render correctly in Google Colab. Emoji cues guide reading — new word, what the cell did,
a number to change and re-run, recap / coming up.

---

## Distributing to the lab

**One click: the Colab badges above.** Once this repo is public, each badge opens that notebook
straight from GitHub in Colab — no download, no upload. Participants click, sign in with any Google
account, and run top to bottom with **Shift + Enter**.

> While the repo is still **private**, the badges open only for you and collaborators — use the
> upload fallback below for attendees until you flip it public (Settings → change visibility).

**Fallback (locked-down network, or repo still private): upload.**
1. Each participant opens [colab.research.google.com](https://colab.research.google.com) and signs in.
2. `File → Upload notebook` → pick the `.ipynb` for the current session.
3. Run top to bottom with **Shift + Enter**.

Share the four `.ipynb` files however is easiest in the lab (USB, shared drive, intranet link, email).

---

## Pre-flight checklist (do this the day before)

- [ ] Run **Session 4** (`04_speech_analytics.ipynb`) end-to-end yourself once. Its first cell
      `!pip install -q gTTS openai-whisper` takes ~1 minute and downloads the Whisper "tiny" model
      on first transcription — confirm the lab's network allows it. (Everything else needs no install.)
- [ ] Confirm the lab machines can reach Google Colab and `pypi.org` / model downloads.
- [ ] Have the four files ready on a shared location, named in order so people don't get lost.
- [ ] Decide your fallback: if a participant's cell errors after editing, the reset is
      **Runtime → Restart and run all**.

---

## Suggested full-day flow

Six hours, **09:30–15:30**, breaks included. The foundations (vocabulary + the five-step shape)
live inside Session 1 and are reused all day — no separate prerequisite module. Text fills the
first half, speech the second.

| Time | Block | Notes |
|------|-------|-------|
| 09:30–10:45 | **Session 1 · Text I — flagging the urgent** | Opens with the framing (predictive vs generative; the two mindsets) + the core vocabulary and five-step shape; spend time on the **accuracy trap** — always-"routine" scores ~85% yet catches no urgent report |
| 10:45–11:00 | Break | |
| 11:00–12:15 | **Session 2 · Text II — predict, extract & recurring faults** | Classification + regression from the same words; cosine recurring-fault detection; embeddings + k-means (honest ~0.22); part-number extraction |
| 12:15–12:45 | Lunch | |
| 12:45–14:00 | **Session 3 · Speech I — predicting from the sound** | The most predictive of the four; classify the fault ~0.88, feature importance, and label-free **anomaly detection** (AUC ~0.94) |
| 14:00–14:15 | Break | |
| 14:15–15:30 | **Session 4 · Speech II — voice → text → decision** *(finale)* | ASR → route with the Session-1 classifier; **WER** honesty; keyword spotting; closes with the day's wrap-up & Q&A |

---

## Talking points per session

**Session 1 · Text I — flagging the urgent.**
Open by naming the two mindsets in the room — "AI can do anything" and "AI is nonsense" — and
promise the truth is more ordinary and more useful than either. The anchor analogy: a seasoned
inspector who flags the worrying report on sight — not magic, just *pattern from experience*.
Foundations live here: *dataset → split → train → predict → measure* and the core words. The lesson
that earns the day is the **accuracy trap** — a "lazy" model that calls everything ROUTINE scores
~85% accuracy yet catches **zero** urgent reports. Let that land, then the confusion matrix in plain
words and why **URGENT recall** (20 of 21 caught, 1 missed) is the number that matters. Stress
*predictive vs generative* so nobody confuses this with ChatGPT. End on the model's **top clue-words**
per class — proof it learned something human-readable.

**Session 2 · Text II — predict, extract & recurring faults.**
Beyond sorting. The same words-to-numbers front end now predicts a *category* (urgency) and a *number*
(downtime hours — the fitted line *through* the dot cloud makes "it learned the relationship" visible).
Then the unsupervised half: **cosine similarity** flags the same chronic fault worded three different
ways with no labels; **embeddings + k-means** group a logbook into families — be honest, agreement is
a modest **~0.22**: Mechanical pops cleanly, the rest blend. Close with auditable **part-number
extraction**, and if time, LDA topics and the "too-perfect score" data-leakage trap.

**Session 3 · Speech I — predicting from the sound.**
The most strongly predictive of the four, and the one engineers call "useful for us." Throw the words
away — a sound is already numbers, and the **FFT** splits it into pitches like a prism. Five features
separate three fault types; classify healthy / bearing / imbalance at **~0.88**. The
**feature-importance** chart is gold: the model leans on the whine and the rumble — the cues a
technician's ear already uses, checkable against intuition. The **anomaly-detection** coda answers
"but we have no failure labels": learn "normal" only, flag the surprising (**AUC ~0.94**). Name the
public benchmarks (CWRU / MIMII / MAFAULDA) — real AUCs run ~0.54–0.96, so a flawless demo is the
thing to distrust.

**Session 4 · Speech II — voice → text → decision (the finale).**
The crowd-pleaser. gTTS fabricates a spoken report so no microphone is needed; **Whisper** transcribes
it; this morning's text classifier routes it — audio in, text out, then it's text analytics again. The
honesty that makes it believable: **WER** is the speech version of accuracy, and the "cleaner" 8%
transcript still swapped one part number — so numbers and serials get a human's eyes. **Keyword
spotting** (a small fixed vocabulary) is robust where full dictation isn't. Agree ASR struggles with
accents, jargon and noise, then show domain adaptation (ATC reached >95% controllers, ~97% callsigns).
Close the whole day on the one idea: numbers, text, or sound, AI did the same thing — *learned the
pattern from past examples, then predicted the next case.*

---

## Handling the skeptics (and the over-believers)

- **"This is just if-then rules / statistics."** Yes — and that's the point. Predictive AI *is*
  disciplined pattern-finding. Session 1's top clue-words and the plain-words confusion matrix make
  this concrete and disarm the hype.
- **"Why isn't it 100% accurate?"** Because real data has surprises. A model claiming 100% is usually
  cheating (it saw the test answers — Session 2's data-leakage trap). Honest, imperfect numbers are a
  feature of these notebooks.
- **"Can it replace our engineers?"** Session 3's feature importance reframes it: AI gives engineers a
  *prioritized list and a reason*, then a human decides. It scales judgment, it doesn't replace it.
- **"AI can do anything."** Point at the one missed urgent report in Session 1 and the low-WER
  transcript that still got a part number wrong in Session 4 — it is a tool with limits you can
  measure, which is exactly why it's trustworthy.

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
| Session 4 install is slow or errors | First cell downloads gTTS + Whisper over the network | Wait ~1 min; if the network blocks it, demo from your own pre-run copy and move on |
| Can't sign in to Colab | Corporate Google account restrictions | Use a personal Google account, or the upload method |
| Edited a number, results look wrong | Stale state from earlier runs | `Runtime → Restart and run all` |

Have one **pre-run copy of each notebook open on your own machine** as a backup, so if a participant's
cell breaks you can show the expected output and keep moving rather than debugging live.

## Prompts to get the room talking

The brief is conversational and application-oriented — these engineers know their machines far better
than we do, so let them connect each idea to their own work. One prompt per session:

- **After Session 1 (text — flag the urgent):** "How much useful signal sits in free-text snags and reports no one has time to read — and what would a *missed* urgent one cost you versus a false alarm?"
- **After Session 2 (predict / extract / recurring):** "What number would help to know from a description — downtime, severity? And how often does the *same* chronic fault get logged five different ways?"
- **After Session 3 (sound):** "Which machines do you already diagnose by ear? Would knowing *which part of the sound* the model used change how much you trust it?"
- **After Session 4 (speech):** "Where do people *speak* information that never gets written down — handovers, inspections, calls?"
- **Closing:** "Pick one place from today where *learn from the past, predict the next case* could help. What data would you need to start?"

## Speaker notes

`SPEAKER_NOTES.md` is a printable script of the per-slide presenter cues, in deck order — handy as a
paper copy at the podium. The same notes are built into the deck (press **S** to show them on screen).

## Rebuilding / editing the notebooks

The notebooks are generated from small Python scripts (`build/nb01.py`–`build/nb04.py`) that share
one **Colab-safe** design system (`build/nbmd.py` — emoji + blockquote callouts, banner, vocabulary
cards; no reliance on colour). To tweak wording or data and regenerate, edit the matching build
script and re-run it. All four were validated by executing every code cell end-to-end before shipping
(Session 4's gTTS/Whisper install cells run in Colab, not in the offline validator).
