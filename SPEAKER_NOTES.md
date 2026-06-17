# Speaker Notes — Predictive AI Session Deck

_Printable companion to `slides.html`. In the live deck, press **S** to show these on screen. Slide order matches the deck exactly. Navigate with the arrow keys or Space; **F** = fullscreen._


---


**Slide 1 — Predictive AI for engineers.**

> Welcome. Today is about the OTHER half of AI — the predictive half. By the end you will have run real machine-learning models with your own hands and will be able to reason about what this technology can and cannot do.


**Slide 2 — A little theory. A lot of hands-on.**

> Reassure them: no programming. We prepared the code; you press a button and watch it work. A mix of short talks and six hands-on notebooks in Google Colab — just a web browser, nothing to install.


**Slide 3 — Most people hold one of two beliefs.**

> Name the room honestly. Some think AI can do anything; some think it is marketing nonsense. Both are wrong, and the truth is more useful than either. We will earn that claim with real examples today.


**Slide 4 — It learns a pattern from the past.**

> Define it in one plain sentence, then the technician analogy — the anchor for the whole day. A person who has inspected thousands of machines can call a bad one on sight. Not magic: pattern from experience. The dots in the thought-bubble are that learned pattern.


**Slide 5 — From past examples to a prediction.**

> This single diagram is the spine of the entire session. Every notebook — numbers, text, speech — is just this picture. Keep pointing back to it all day.


**Slide 6 — It draws a boundary between good and bad.**

> This is the most important picture in the deck. Each dot is a past machine; colour = whether it needed service. The model draws the boundary between the colours. A new machine simply falls on one side. THIS is what 'finding the pattern' actually looks like — they will build this exact chart in Module 00.


**Slide 7 — Two different jobs.**

> Clear up the biggest confusion. ChatGPT is GENERATIVE — it creates new content. Today is PREDICTIVE — it makes a call about a case. Different tool, different job. Generative AI gets its own sessions later.


**Slide 8 — You already trust it every day.**

> Defuse the 'is this even real' skeptic. Predictive AI has quietly run everyday systems for years. None are sci-fi; all are the same learn-from-the-past idea.


**Slide 9 — The scary words are simple words.**

> Transition. The words that make AI sound intimidating are simple once you see them. We meet five, then use them all day. Each is a plain idea wearing a technical name.


**Slide 10 — A dataset is just a table.**

> A dataset is just a spreadsheet. Rows = the things we recorded (machines). Columns = what we measured. Demystify immediately — no one fears a table.


**Slide 11 — Clues in. Answer out.**

> The most important distinction of the day. Features = the clues we GET. Label = the answer we WANT. The single column of answers is the label column. We separate them before doing anything clever.


**Slide 12 — Learn from most. Judge on the hidden rest.**

> Why hide data? The exam analogy: if a student studies the exact exam paper, a top score proves nothing. The honest test uses unseen questions. So we hide some machines and judge only on those.


**Slide 13 — **

> Every notebook repeats this rhythm. Accuracy = fraction right on the hidden set. Be honest: 100% on real data is usually a red flag, not a triumph — Module 1 shows why.


**Slide 14 — One idea. Three kinds of data.**

> Preview the day. Same idea, three kinds of data. Numbers first (Modules 0-3), then written text (Module 4), then the spoken word (Module 5). Each just feeds the same picture from earlier.


**Slide 15 — Real jobs it does.**

> Ground it in outcomes an engineering org cares about. These are the case studies the notebooks dramatise. Keep framing generic — the value is the same whatever the machine.


**Slide 16 — The roadmap.**

> The map for the rest of the day. Six modules building on each other. 00 is the foundation; do it carefully. Then we open Colab.


**Slide 17 — Module 00: What is Predictive AI?**  — *module divider, open the notebook*

> Open Module 00 now. Go slow — this installs the vocabulary everything else leans on. The highlight: the model prints the if-then rules it wrote by itself.


**Slide 18 — Module 01: Classification**  — *module divider, open the notebook*

> Module 01. The lesson that earns the day: a lazy model that always says PASS can score 80% and catch zero bad parts. Spend time on the confusion matrix — false alarm vs missed fault.


**Slide 19 — Module 02: Regression & Forecasting**  — *module divider, open the notebook*

> Module 02. Prediction is not only yes/no — sometimes it is a number. The two visuals: the fitted line through the dots (regression) and the forecast continuing past today (forecasting). These charts are exactly what they will produce.


**Slide 20 — Module 03: Predictive Maintenance**  — *module divider, open the notebook*

> Module 03, the payoff. Feature importance is the slide engineers love — the model says WHICH signal mattered most, not just yes/no. The anomaly coda answers 'but we have no failure labels'.


**Slide 21 — Module 04: Text Analytics**  — *module divider, open the notebook*

> Module 04. The only new concept is 'words become numbers' — show the word-columns appear. After that it is the same classification workflow from Module 01.


**Slide 22 — Module 05: Speech Analytics**  — *module divider, open the notebook*

> Module 05, the finale. The showpiece: change the spoken sentence, re-run, and watch speak→transcribe→categorise happen live. End the day on the one idea tying all six together.


**Slide 23 — Powerful. Not magic.**

> The honesty slide — this builds trust with a technical, skeptical audience. Say it plainly: it learns only from the data you give it; it is not perfect; it ranks and flags, a human decides.


**Slide 24 — It was always the same picture.**

> Tie the bow. Whatever the data — numbers, text, speech — the model did the same thing: learned the pattern, predicted the next case. They can now reason about AI instead of believing or dismissing it.


**Slide 25 — Thank you. Questions?**

> Close and hand off. Generative AI — the ChatGPT half — comes in later sessions from other speakers. Thank them and open the floor.
