# Predictive AI — Hands-on Session · Planned Coverage

*Short coverage note for the organising committee — purpose, format, and what each of the four sessions covers. A detailed per-session teaching plan (timings, demos, case studies with sources, discussion prompts and skeptic-handling) accompanies it.*

## Purpose & focus

A **hands-on introduction to predictive AI** for engineers at HAL, run as **four sessions across a six-hour day** (09:30–15:30, breaks included) through the two kinds of data they work with most — written **text** and spoken **speech**. It deliberately covers the **predictive / analytical** side of AI — machine learning that *learns a pattern from past data and predicts the next case*. **Generative AI (ChatGPT and the like) is explicitly out of scope** here — a different tool for a different job, covered by other speakers. A recurring goal is to give participants a **grounded, realistic picture** of what predictive AI can and cannot do — neither magic nor hype, but an honest, understandable engineering tool with measurable limits.

## Who it is for

Core engineers, **no IT / programming background assumed**. The whole day is conversational and application-oriented; every example is drawn from equipment, maintenance, MRO and quality so it maps directly onto the participants' own work.

## Format — a no-code lab

- **No coding required.** All code is pre-written. Participants only **run** prepared cells (Shift + Enter) and read the output; in each session they edit **one highlighted value** and re-run to see the result move.
- Runs in **Google Colab** in a browser — nothing to install.
- A mix of **concept and practice**: a short slide-led framing, then a guided notebook.
- Notebooks are **self-contained** (built-in data, fixed seeds so everyone sees the same numbers) and use **honest, realistic results** — never a misleading "100% accurate" demo.

## Scope — exactly four notebooks, one per session

The workshop is **four notebooks, one per session.** The foundations of predictive AI (the five-step shape, the core vocabulary, the train/test idea) are **introduced inside Session 1 and reused all day** — no separate prerequisite. Text fills the first half, speech the second.

> The same five-step ideas apply to **numeric sensor data** too (classification, regression, predictive maintenance), but this workshop is exactly the four notebooks above — text and speech.

## What participants will be able to do by the end

- Recognise the standard shape of a predictive-AI project: **dataset → split → train → predict → measure**.
- Use the core vocabulary correctly: **dataset, feature, label, label column, training vs. test set, model, accuracy** (and why accuracy alone can mislead — the *confusion matrix*).
- Tell **predicting a category** (classification) from **predicting a number** (regression), and know which questions each answers.
- Ask the right questions of any AI claim: *What did it learn from? How was it tested on unseen cases? How confident is it, and where does it get things wrong?*

## The day in four sessions

| Time | Session | What it covers |
|------|---------|----------------|
| 09:30–10:45 | **Session 1 · Text — foundations & sorting** | The core vocabulary (dataset, feature, label, label column, train/test split, accuracy) and the five-step shape; turning words into numbers (bag-of-words, stop words, **TF-IDF**); auto-routing free-text snags to the right team; the model's **top clue-words** per team; a deliberately ambiguous report to show honest confidence |
| 11:00–12:15 | **Session 2 · Text — predict, extract & recurring faults** | Predicting **urgency** (classification) and **downtime hours** (regression) from the same wording; the **confusion matrix** and the **accuracy trap**; **recurring/duplicate-fault detection** (cosine similarity); **grouping snags into families** (embeddings + k-means clustering, with a 2-D map); **part-number extraction** (auditable); *bonus:* topic discovery (LDA) and the honest-test / data-leakage trap on a real public corpus |
| 12:45–14:00 | **Session 3 · Speech — voice → text → decision** | Speech-to-text (ASR): transcribe a spoken report and route it with the Session-1 classifier; **Word Error Rate (WER)** and why a low error rate can still get the one critical word wrong; **keyword spotting**; honest ASR limits and domain adaptation |
| 14:15–15:30 | **Session 4 · Speech — predicting from the sound** | Turning audio into numbers (energy, frequency bands, dominant pitch via **FFT**); classify a machine fault from its sound; **feature importance**; **unsupervised anomaly detection** ("learn normal, flag the surprising"); named real datasets; closes with the day's wrap-up & Q&A |

*(Six hours total, 09:30–15:30, **breaks included** — a 15-minute break after Sessions 1 and 3, and a ~30-minute lunch after Session 2. Each session is **≈75 minutes** of teaching. Timings approximate and flexible.)*

## What each session can do (worked examples)

**Session 1 · Text — foundations & sorting.** Introduces the vocabulary, then how a computer turns words into numbers (bag-of-words, TF-IDF, dropping "stop" words) and classifies. Enables:

- Auto-routing free-text snags / defect reports to the right team (Electrical, Mechanical, Hydraulic, Avionics, Structures)
- Tagging maintenance work orders / squawks by system or ATA chapter
- Separating actionable reports from noise — and seeing, in plain words, *why* the model decided

**Session 2 · Text — predict, extract & find recurring faults.** Beyond sorting — into numbers, structured data and repeats pulled from the words. Enables:

- Predicting **urgency / severity** (a category) from wording — with a confusion matrix and the accuracy trap
- Predicting **expected downtime / repair effort** (a number) from a defect description — same words-to-numbers front end
- **Recurring / duplicate-defect detection**: the same chronic fault, worded differently, flagged automatically (no labels)
- **Grouping into families**: embedding reports as points and **clustering** them into families with no labels — auto-organising a logbook with no categories defined in advance
- **Extracting** part numbers and component names from prose (auditable, line by line)
- *Bonus:* discovering themes with no labels (topic modelling), and spotting the "too-perfect" score (data leakage)

**Session 3 · Speech — voice to text to decision.** Speech-to-text (ASR), then the Session-1 text analysis routes it. Enables:

- Spoken maintenance notes and shift handovers → transcribed and routed automatically
- Inspection voice memos → searchable, categorised text; hands-free reporting on the shop floor
- An **honest** view of recognition: WER, where it breaks (accents, jargon, noise), and why a small fixed **keyword** vocabulary is more reliable than full transcription when stakes are high

**Session 4 · Speech — predicting from the sound itself.** Turning audio into numbers and predicting a fault — no transcription. The most strongly predictive of the four. Enables:

- **Acoustic condition monitoring**: a bearing / gearbox / engine's sound → healthy vs. fault type
- **Unsupervised anomaly detection**: learn only "normal," then flag the unusual — the realistic case when faults are rare
- Reading **which part of the sound** drove the call (feature importance) — and checking it against engineering intuition

## How mathematics is handled

Maths is shown **conceptually and visually only** — a confusion-matrix grid, a similarity heatmap, bar charts of the words (or sound bands) a model keyed on, a feature-importance chart, a predicted-vs-actual scatter, a spectrum/spectrogram. The underlying statistics and signal processing are **named** where useful (TF-IDF, logistic regression, FFT) but **no equations and no recall are expected** of participants.

## Real-world grounding

Each session is anchored in **real, named programmes and public datasets** (e.g. Airbus Skywise, ATC speech recognition, helicopter HUMS, the CWRU/MIMII/MAFAULDA machine-sound benchmarks, NASA's ASRS narratives) — all **fact-checked**, with vendor-claimed, self-reported, simulated or draft figures flagged as such, modelling the exact "where did this number come from?" discipline the workshop teaches. Full sources accompany the detailed plan.

## What the lab needs (please confirm)

- A computer lab with **internet access**, one machine per participant (pairs also fine).
- Lab machines able to reach **Google Colab**; for **Session 3** only, a one-time ~1-minute download of speech tools (offline fallback available if the network blocks it).
- A **Google account** per participant (a personal account works), or the upload-the-notebook fallback.
- A projector for the slides.
