# Predictive AI — Hands-on Session · Planned Coverage

*This is the short coverage note. For the full per-session teaching plan — minute-by-minute timings, the exact demos, case studies with sources and honest caveats, discussion prompts and skeptic-handling — see `LESSON_PLAN.md` (and its shareable `Predictive-AI-Lesson-Plan.pdf`). The text Session 2 demos run in the new `notebooks/04b_text_predict_extract.ipynb`.*

## Purpose & focus

A six-hour (09:30–15:30) **hands-on introduction to predictive AI** for engineers at HAL,
taught in **four parts** through the two kinds of data they work with most — written
**text** and spoken **speech**. The session deliberately covers the **predictive and
analytical** side of AI — machine learning that *learns a pattern from past data and
predicts the next case*. A recurring goal is to give participants a **grounded, realistic
picture** of what predictive AI can and cannot do — showing, step by step, that it is
neither magic nor hype, but an honest, understandable engineering tool with measurable limits.

## Who it is for

core engineers, **no IT/programming background assumed**. The whole session is
conversational and application-oriented; the examples are drawn from equipment,
maintenance and quality-control so they map directly onto the participants' own work.

## Format — a no-code lab

- **No coding required.** All code is pre-written. Participants only **run** prepared
  cells (Shift + Enter) and read the output; in each part they edit **one highlighted
  number** and re-run to see the result change.
- Runs in **Google Colab** in a web browser — nothing to install, works on any lab machine.
- A mix of **concept and practice**: a short slide-led framing, then a guided notebook.
- Notebooks are **self-contained** (built-in data, fixed seeds so everyone sees the same
  numbers) and use honest, realistic results — never a misleading "100% accurate" demo.

## What participants will be able to do by the end

- Recognise the standard shape of a predictive-AI project: **dataset → split → train →
  predict → measure**.
- Use the core vocabulary correctly: **dataset, feature, label, label column, training
  set vs. test set, model, prediction, accuracy** (and why accuracy alone can mislead).
- Tell **predicting a category** (classification) from **predicting a number** (regression),
  and know which questions each answers.
- Ask the right questions of any AI claim: *What did it learn from? How was it tested on
  unseen cases? How confident is it, and where does it get things wrong?*

## The day in four parts (6 hours, 09:30–15:30)

The foundations of predictive AI — what it is, the core vocabulary, the train/test idea —
are introduced at the **start of Part 1**, then reused throughout. Text fills the morning,
speech the afternoon.

| Time | Part | What it covers |
|------|------|----------------|
| 09:30 | **Part 1 · Text — foundations & sorting** | Introduction and the core vocabulary (dataset, label, label column, train/test split, accuracy); turning words into numbers (TF-IDF); auto-routing free-text reports to the right team |
| 11:00 | **Part 2 · Text — predicting & extracting** | Predicting urgency and likely downtime from a report's wording; sentiment/tone; pulling out part numbers; spotting duplicate and recurring faults |
| 12:40 | **Part 3 · Speech — voice to text to decision** | Speech-to-text: transcribe a spoken report and route it automatically; honest about recognition limits |
| 13:50 | **Part 4 · Speech — predicting from the sound** | Turning audio into numbers (energy, pitch, frequency); acoustic condition monitoring; abnormal-noise detection; urgency from voice tone |
| 15:05 | **Wrap-up & Q&A (~25 min)** | The single idea behind all four; where predictive AI fits, and its honest limits |

*(Total 6 hours, 09:30–15:30. Morning break ~10:50, lunch ~12:00, afternoon break ~13:40. Timings are approximate and flexible.)*

## What each part can do (worked examples)

**Part 1 · Text — reading & sorting.** How a computer turns words into numbers
(bag-of-words, TF-IDF, dropping common "stop" words), then classifies — taught alongside
the predictive foundations. What it enables:

- Auto-routing free-text snags / defect reports to the right team (Electrical, Mechanical, Hydraulic, Avionics)
- Tagging documents and logs by system / subsystem
- Separating actionable reports from noise; categorising operator complaints

**Part 2 · Text — predicting & extracting.** Going beyond sorting — into numbers and
information pulled from the words. What it enables:

- Predicting **urgency / severity** of a report from its wording
- Predicting **expected downtime or repair effort** from a defect description (text → a number)
- **Sentiment / tone** on operator feedback and incident language
- **Extracting** part numbers and component names (keyword & entity extraction)
- Detecting **duplicate or recurring** defects and emerging fault **trends** over time

**Part 3 · Speech — voice to text to decision.** Speech-to-text (ASR), then the same text
analysis routes it. What it enables:

- Spoken maintenance notes and shift handovers → transcribed and routed automatically
- Inspection voice memos → searchable, categorised text
- Hands-free reporting on the shop floor

**Part 4 · Speech — predicting from the sound itself.** Turning audio into numbers (energy,
pitch, dominant frequency) and predicting — with no transcription. The most strongly
predictive of the four. What it enables:

- **Acoustic condition monitoring**: a bearing / gearbox / engine's sound → healthy vs. fault type
- Detecting **abnormal machine noise** (anomaly detection on audio)
- Reading **urgency / stress** from a voice's energy and pitch
- Simple **keyword spotting** without full speech-to-text

## How mathematics is handled

Maths is shown **conceptually and visually only** — a confusion-matrix grid, bar charts of
the words (or sounds) a model keyed on, a feature-importance chart, and simple plots of
text or audio turned into numbers. The underlying statistics and linear algebra are named
where useful but **no equations and no recall are expected** of participants.

## What the lab needs (please confirm)

- A computer lab with **internet access**, one machine per participant (pairs also fine).
- Lab machines able to reach **Google Colab**; for the **speech parts** only, a one-time
  ~1-minute download of speech tools (we have an offline fallback if the network blocks it).
- A **Google account** per participant (a personal account works), or we use the
  upload-the-notebook fallback.
- A projector for the slides.
