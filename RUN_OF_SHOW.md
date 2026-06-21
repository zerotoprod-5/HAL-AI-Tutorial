# Run of Show — Predictive AI (Text & Speech), one-day lab

*The presenter's "what to open, when" guide. Follow it top to bottom on the day. Six hours,
**09:30–15:30**, four sessions (two text, two speech), breaks included.*

The model is simple: **you project a deck; participants watch and run their own Colab notebook.**
Nothing is shared to their screens — interaction is **presenter-driven widgets + room votes** (cards or
show-of-hands, **no phones / no wifi polls**). The slides are handed out **as a PDF only at the very
end**, so attention stays on the room, not on a screen they could read ahead.

---

## What you open (two layers)

| Layer | What it is | Who looks at it |
|------|------------|-----------------|
| **The deck** | `deck/index.html` → four per-session decks (`01-text-i` … `04-speech-ii`). Interactive: predict-then-reveal votes, live widgets, a money-shot confusion matrix. **This is what you project.** | You (projected) |
| **The notebooks** | `notebooks/01_text_analytics` · `02_text_predict_extract` · `03_sound_fault_prediction` · `04_speech_analytics` — in **Google Colab**, one per session. | Each participant, on their own machine |
| **Take-homes** | `Predictive-AI-Field-Guide.pdf` (illustrated reference) + `handout.html` (one-page cheat-sheet). **Shared at the end, not before.** | Participants keep |

> **Single-file alternative:** `slides.html` is the whole day in one continuous 28-slide deck
> (press **S** for speaker notes). Use it instead of the season if you prefer one file / a simpler
> setup. Everything below — *which notebook, which cell, when* — is identical either way.

---

## Before the day (do this the day before)

1. **Run Session 4 yourself once.** `04_speech_analytics.ipynb`'s first cell installs gTTS + Whisper
   (~1 min) and downloads a model on first transcription — **confirm the lab network allows it.**
   Every other notebook runs instantly, no install. (Full checklist: `README.md` → Pre-flight.)
2. **Get the four notebooks in front of participants.** Either the Colab badges in `README.md` (if the
   repo is public) or the **upload fallback**: hand out the four `.ipynb` files (USB / shared drive /
   intranet) and have people use *File → Upload notebook* in Colab.
3. **Keep `slides.html` and the `figs/` folder together** if you use the single-file deck — it loads
   its charts by relative path.
4. **Have one pre-run copy of each notebook open on your own machine** as a backup if the wifi sulks.

---

## Where to start (first 5 minutes)

1. Project **`deck/index.html`** (the launcher) — or open `slides.html` fullscreen.
2. Tell the room: **open Colab and sign in, but don't open a notebook yet** — you'll tell them exactly
   when. One reset fixes almost everything all day: **Runtime → Restart and run all.**
3. Click into **`deck/01-text-i.html`** and begin. The foundations (the five-step shape and the core
   words) are taught *inside Session 1* — there is no separate intro module.

---

## The rhythm of every session

Each session is the same loop, ~75 minutes:

1. **You present the deck** — the scenario, the concept, a **predict-then-reveal vote** (cards up
   A/B/C/D; you tally, then advance once to reveal). This is where the room leans in.
2. At the **"Now open — Session N"** divider, say: **"Switch to your Colab tab, open notebook N, and run
   it top to bottom with Shift+Enter."** The deck shows the same output as an offline fallback.
3. At the deck's **one highlighted hands-on cue**, the room runs the payoff cell and reads it with you.
4. **The money slide** (the peak) → a short **consolidation beat** → **recap** → break.

The one hands-on cell to call out per session:

| Session | Notebook | Say "run the…" |
|---------|----------|----------------|
| 1 | `01_text_analytics.ipynb` | **CLUE WORDS** cell |
| 2 | `02_text_predict_extract.ipynb` | **RECURRING FAULTS** cell |
| 3 | `03_sound_fault_prediction.ipynb` | **SOUND MAP** cell |
| 4 | `04_speech_analytics.ipynb` | **WER** cell |

---

## The timetable — what to open, when

| Time | Open | Do |
|------|------|----|
| **09:30** | `deck/01-text-i.html` · notebook **01** | **Session 1 · Text I — flag the urgent.** Foundations + words→numbers (TF-IDF). Vote on the hidden-note accuracy; reveal ~90%. Money shot: the **URGENT/ROUTINE confusion matrix** — caught **20 of 21**, missed **1**; the honest number is **urgent recall ~95%**, not bare accuracy (always-"routine" already scores 85%). |
| 10:45 | — | **Break (15 min).** |
| **11:00** | `deck/02-text-ii.html` · notebook **02** | **Session 2 · Text II — predict, extract & recurring faults.** Predict downtime hours (regression, ±~1.5 h); the **recurring-fault similarity heatmap** (same fault, worded three ways); cluster **300 snags** into families (honest ~0.22); pull part numbers; the leakage/header trap. |
| 12:15 | — | **Lunch (~30 min).** |
| **12:45** | `deck/03-speech-i.html` · notebook **03** | **Session 3 · Speech I — predicting from the sound.** Post-lunch wake-up. FFT turns sound into numbers; vote, reveal **~0.88** classify; **feature importance** (the whine + the rumble); **anomaly detection** with no labels (**AUC ~0.94**). |
| 14:00 | — | **Break (15 min).** |
| **14:15** | `deck/04-speech-ii.html` · notebook **04** | **Session 4 · Speech II — voice → text → decision (the finale).** Speak → transcribe (Whisper) → route. **WER**: a "cleaner" transcript still swapped one digit of a part number (MS21042→MS21052) — numbers get a human's eyes. **Closes the whole day with the wrap-up & Q&A.** |
| **15:30** | Field Guide PDF + handout | **Hand out the take-homes.** Close on the one idea: text, sound, or speech — *learn the pattern from past examples, then predict the next case.* |

---

## If the wifi or Colab fails

- The deck shows every key chart as a **built-in offline copy**, so you can keep teaching without the
  notebook. Narrate from the slide and move on.
- A participant's cell errors after they edited a value → **Runtime → Restart and run all.**
- Colab won't sign in (corporate account) → use a personal Google account, or the upload fallback.
- Full troubleshooting table: `README.md` → *Lab troubleshooting*.

---

## The two things to land

- **It's honest.** Every number was real and imperfect — one missed crack, a ~0.22 clustering score, a
  low WER that still got the one word wrong. That's the credibility, especially with skeptics.
- **It's one idea, four times.** Numbers in, pattern out, prediction checked — whether the input was
  written text, a machine's sound, or the spoken word.
