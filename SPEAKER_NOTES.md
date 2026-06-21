# Speaker Notes — Predictive AI for Engineers

**The four-session text & speech deck** for HAL Core Engineering — full-day, no-code hands-on lab.
Two text sessions, two speech sessions (~75 min each). Predictive AI only; generative AI (ChatGPT) is explicitly out of scope today.

Deck: `slides.html` · 28 slides. These cues match the `data-note` on each slide, in deck order.
Controls: `→ / ← / Space` advance (bullets reveal one at a time, then the slide turns) · click left/right half of screen · `F` fullscreen · `S` notes overlay · `O` overview grid.

Doctrine reminders: lead with credibility, not hype · name the two mindsets and promise the honest middle · the five-step spine (dataset → split → train → predict → measure) is reused every session · always show honest/imperfect numbers · charts not equations · predictive, not generative.

---

## Part A — Reusable conceptual front

**1 · Title — "Predictive AI for engineers."**
Today is the OTHER half of AI — the predictive half. By the end you will have run real machine-learning models with your own hands and be able to reason about what this technology can and cannot do. The whole day moves text → speech.

**2 · How today works**
Reassure: no programming. The code is pre-written; you press play and watch it work. Short talks plus four Colab notebooks — just a browser, nothing to install. The journey is text first, then speech: one idea, two kinds of messy data.

**3 · The two mindsets**
Name the room honestly. Some believe "AI can do anything"; some believe "AI is nonsense." Both are wrong. The honest middle is more useful — and we earn it with real, imperfect numbers all day.

**4 · What is AI, really (technician analogy)**
The anchor analogy for the whole day. A technician who has inspected thousands of machines calls a bad one on sight — not magic, they have seen the pattern before. The green/red dots in the thought-bubble are that learned pattern. We teach a computer to do exactly that.

**5 · The one idea (icon flow)**
The spine in one diagram: past examples → find the pattern (learning) → predict a new case. Every notebook — text, speech, sound — is just this picture. Keep pointing back to it.

**6 · See the pattern (real chart — `pattern_scatter.svg`)**
The most important picture in the deck. Each dot is a past machine; colour = whether it needed service. The model draws the boundary between the colours; a new machine falls on one side. Every session is a variation of this.

**7 · Predictive vs generative**
Clear up the biggest confusion. ChatGPT is GENERATIVE — it creates content. Today is PREDICTIVE — it makes a call about a case. Different tool, different job. Say plainly: generative AI is out of scope today; it gets its own sessions.

**8 · Already everywhere (4 cards)**
Defuse the "is this even real" skeptic. Predictive AI has quietly run everyday systems for years. The spam filter is the anchor — classical bag-of-words text AI nobody calls magic — and it bridges straight into Session 1.

**9 · Vocab divider + the five-step spine**
Don't front-load a glossary. Introduce five plain words — dataset, feature, label, train/test split, accuracy — then use them relentlessly. Put the spine on the wall: dataset → split → train → predict → measure.

---

## Part A2 — The core words

**10 · Dataset (table)**
Demystify immediately — a dataset is just a spreadsheet. Rows = the machines we recorded; columns = what we measured. No one fears a table.

**11 · Feature vs Label (table + legend)**
The most important distinction of the day. Features = the clues the model sees (input columns). Label column = the answer it learns to predict. Reused in every session: in text the features become word-counts, in sound they become pitches.

**12 · Train/test split (splitbar)**
Why hide data — the exam analogy. If a student studies the exact paper, a top score proves nothing. We judge the model only on cases it has never seen. The Session-1 knob turns this 75/25 ratio.

**13 · Accuracy + the rhythm (flow)**
Every notebook repeats this rhythm: learn → use → measure honestly. Accuracy = fraction right on the hidden set. 100% on real data is usually a red flag, not a triumph — Session 2's header-trap proves it. A gap is a trust signal.

---

## Part B — Words (and sound) become numbers + roadmap

**14 · Words, and even sound, become numbers (two cards + inline illustration)**
The hinge of the whole day. A computer can't read — it can only count, so we turn words into numbers (bag-of-words, TF-IDF). A sound is ALREADY numbers — a microphone records a list of values; the FFT splits them into pitches. Only the first step changes between text and sound; everything after is the same five steps.

**15 · Roadmap (four sessions, two data types)**
The map for the day. Four ~75-min sessions — two text, two speech — building on each other. Foundations live inside Session 1. NOT six modules. Then we open Colab.

---

## Part C — Session 1: Text I

**16 · Session 1 divider (`text_cluewords.svg`) — `notebooks/01_text_analytics.ipynb`**
Open Session 1 — the foundations live here too, taught on a maintenance example. The highlight: the model's own top clue-words per team, in plain English, so it is clearly not a black box.

**17 · Auto-route a snag (inline pipeline)**
oil/pressure/fluid → Hydraulic. TF-IDF turns each report into a row of numbers, then it is ordinary classification: Hydraulic / Electrical / Avionics / Mechanical. Same split → train → predict → measure as the opening table; only the first step (text → numbers) is new. Show the confidence drop on an ambiguous report.

**18 · Top clue-words + honest accuracy (`text_cluewords.svg`)**
Auditability is the selling point. Each team's top words are exactly what an engineer expects. Cite ~83% Naive Bayes / ~91% linear on the standard public corpus to set honest expectations; small-set demo scores wobble — that's why the knob matters. A human stays in the loop.

---

## Part D — Session 2: Text II

**19 · Session 2 divider (`cosine_heatmap.svg` + `cluster_scatter.svg`) — `notebooks/02_text_predict_extract.ipynb`**
The same words-to-numbers front end answers many questions — just swap the final step: predict a category, predict a number, find repeat faults, group into families, extract part numbers. Money shots: the heatmap and the cluster map.

**20 · Confusion matrix + the accuracy trap (`confusion_urgency.svg`)**
For engineers, visible errors are a trust signal. Demand the confusion matrix, not a single accuracy number. ~81% on urgency; mistakes mostly Low↔Medium; caught 10 of 15 High and slipped High→Low only once — rare, but it happened, so High keeps a human's eyes. The accuracy trap: always say "routine," score high, catch zero urgent snags.

**21 · Classification vs regression (`downtime_scatter.svg`)**
The classification-vs-regression "aha." Classification = which bucket; regression = how many hours. Same TF-IDF front end, different last step. Off by ~1.5 h on ~6 h jobs, R² ≈ 0.6 — honest about the big-job misses.

**22 · Recurring / duplicate faults (`cosine_heatmap.svg`)**
No labels needed. Cosine similarity scores 0–1 how much two reports share distinctive words; the heatmap lights up blocks of recurring faults. This is the unsupervised pairwise view; clustering next is its whole-set companion. Aviation MRO does this commercially — those figures are vendor-claimed, so lead with the capability.

**23 · Embeddings + clustering (`cluster_scatter.svg`)**
Unsupervised: no answer key. Each snag becomes a point (an embedding); k-means (n_clusters=5) sorts them into families; read each cluster's top words to name it. The notebook's seeded code yields ~0.22 adjusted-Rand agreement with the true systems — modest but real structure; Mechanical pops out cleanly, others blend. Stay honest: it found structure, not a perfect map. (Note: the brief prose said ~0.45; the reproduced seed-0 code gives ~0.22, so the deck cites ~0.22 to stay honest.)

---

## Part E — Session 3: Speech I / Sound

**24 · Session 3 divider (`sound_clusters.svg` + `anomaly_hist.svg`) — `notebooks/03_sound_fault_prediction.ipynb`**
Throw the words away. A sound is already numbers; the FFT splits it into pitches like a prism. Same five steps, no text at all. Read fault pitches as orders (1× imbalance, 2× misalignment), not raw Hz.

**25 · Sound is numbers — payoff (`sound_clusters.svg` + `anomaly_hist.svg`)**
Five FFT features separate three fault types into clean clusters; classify healthy / bearing / imbalance at ~0.88. Feature importance leans on the whine and the rumble — the very cues a technician's ear uses. With no fault examples, learn "normal" only and flag the surprising — anomaly detection at AUC ≈ 0.94, the realistic aerospace case (lots of healthy sound, few faults). Public benchmarks run AUC ~0.54–0.96; a flawless demo is the thing to distrust.

---

## Part F — Session 4: Speech II / speech-to-text finale

**26 · Session 4 divider + WER table — `notebooks/04_speech_analytics.ipynb`**
The finale. Speak a report, transcribe with Whisper, route with this morning's classifier — ASR is "audio in, text out," then it's text analytics again. Draw the classical→deep line (~2012) so nobody thinks "ChatGPT" — both are predictive. The WER table makes the key point: a low error rate can still get the one safety-critical word wrong.

**27 · WER + keyword spotting + ASR limits**
Honesty about the limit makes the capability believable. WER = wrong + missing + extra words, the speech version of accuracy. The 8% transcript was "cleaner" yet swapped one part number for another — so numbers and serials get a human's eyes. Keyword spotting (a small fixed vocabulary) is robust to stutters — why shop-floor tools use wake-words, not dictation. Agree ASR struggles with accents, then counter with domain adaptation: ATC reached >95% controllers / >90% pilots / ~97% callsigns. Frame as domain-dependent, not guaranteed.

---

## Part G — Honest closing

**28 · Neither magic nor nonsense + handoff**
Tie the bow: same picture every time — dataset → split → train → predict → measure. The numbers were honest all day: urgent recall ~95% (one missed), urgency ~81%, downtime ±1.5 h, clustering ~0.22, sound ~0.88, anomaly AUC ~0.94, and a low WER that still got the one word wrong. Neither magic nor nonsense — a tool you can now reason about and question. Hand off to the generative-AI sessions that follow. Close on "you can now question an AI claim."
