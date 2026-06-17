import sys; sys.path.insert(0, "/tmp")
from nbbuild import *

OLD_VS_NEW = """
<table style="border-collapse:collapse;width:100%;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:15px;margin:8px 0;">
<tr style="background:#1f2d3d;color:#fff;">
  <th style="padding:10px 14px;text-align:left;">Approach</th>
  <th style="padding:10px 14px;text-align:left;">When you service</th>
  <th style="padding:10px 14px;text-align:left;">The problem</th>
</tr>
<tr style="background:#f8ecec;">
  <td style="padding:10px 14px;font-weight:700;color:#9c2b2b;">Fix-on-break</td>
  <td style="padding:10px 14px;">After it has already failed</td>
  <td style="padding:10px 14px;">Unplanned downtime, emergencies, collateral damage</td>
</tr>
<tr style="background:#fdf2e0;">
  <td style="padding:10px 14px;font-weight:700;color:#b26a00;">Fixed schedule</td>
  <td style="padding:10px 14px;">Every N hours, no matter what</td>
  <td style="padding:10px 14px;">Service healthy machines too early, miss the sick ones</td>
</tr>
<tr style="background:#eaf5ea;">
  <td style="padding:10px 14px;font-weight:700;color:#2e7d32;">Predictive</td>
  <td style="padding:10px 14px;">Just before it would have failed</td>
  <td style="padding:10px 14px;">Needs data and a model &mdash; which is exactly today's skill</td>
</tr>
</table>
"""

cells = [
md(banner("Notebook 3 of 6", "Predictive Maintenance: Catch Failures Before They Happen",
   "A whole fleet of machines, watched by sensors &mdash; and a model that flags the ones about to fail")),

md("## How to use this notebook\n\n"
   "Same as before: this is **hands-on**, but you only **run** the cells, top to bottom, and read what comes out. "
   "You do not need to write any code.\n\n"
   "- To run a cell: click it, then press **Shift + Enter** (or the &#9654; play button on its left).\n"
   "- Run them **in order**. Each cell builds on the one above it.\n"
   "- If something looks broken, use the menu: **Runtime &rarr; Restart and run all**, then start again.\n\n"
   "This is the **capstone** of the supervised-learning notebooks. We pull together everything from "
   "Notebook 0 (data &rarr; split &rarr; train &rarr; predict &rarr; measure) and Notebook 1 "
   "(confusion matrix, precision/recall, missed faults vs false alarms) on one realistic problem &mdash; "
   "and then we step into a brand-new idea at the end."),

md(bigidea(
   "Every engineering organisation runs equipment that eventually fails. The big shift of the last decade is this: "
   "instead of waiting for a machine to break, or blindly servicing on a fixed calendar, we can <b>predict which "
   "machines are about to fail</b> and service exactly those, exactly in time.<br><br>"
   "<b>That is predictive maintenance, and it is the single most common use of predictive AI in industry.</b> "
   "Today we build it end to end: assemble a sensor dataset, train a model to flag at-risk machines, then &mdash; the part "
   "engineers love &mdash; ask the model <i>which sensor mattered most</i>. Finally we meet the other half of AI: "
   "what to do when we have sensor readings but <b>no record of what failed</b>.")),

md(story(
   "<b>Our scenario: a fleet of similar machines.</b><br>"
   "Picture a plant floor with hundreds of similar machines, each fitted with sensors. Every machine reports a few "
   "numbers &mdash; running <b>temperature</b>, <b>vibration</b>, <b>pressure</b>, <b>oil quality</b>, and "
   "<b>hours since its last service</b>. For our historical machines we also know the outcome: did it "
   "<b>fail soon</b> afterwards (within the next maintenance window), or did it keep running fine?<br><br>"
   "The question: <b>given a machine's recent sensor readings, can we predict whether it will fail soon &mdash; "
   "in time to service it on our terms instead of in an emergency?</b> No deep machinery knowledge required; the "
   "common-sense story is enough: hot, shaky, badly-pressured machines running on dirty oil that are overdue for "
   "service are the ones to worry about.")),

md(section("The old way vs. predictive maintenance", 1)),
md(vocab("Predictive maintenance",
   "<b>Predictive maintenance</b> means using a machine's data to predict failure <i>before</i> it happens, so the "
   "fix is <b>planned</b>, not an emergency. It sits between two older habits: <b>fix-on-break</b> (wait for failure) "
   "and <b>fixed-schedule</b> (service everything every N hours whether it needs it or not). Predictive maintenance "
   "services the right machine at the right time.")),
md(OLD_VS_NEW),
md(vocab("Remaining useful life",
   "A closely related idea you will hear is <b>remaining useful life</b> &mdash; roughly, <i>how much life a machine "
   "has left before it fails</i>. Today we answer the simpler yes/no version (\"will it fail soon?\"), but it is the "
   "same family of question, and the same sensor data feeds both.")),

md(section("Build the fleet's data", 2)),
md(vocab("Quick reminders",
   "From Notebook 0: a <b>dataset</b> is a table (rows = machines, columns = measurements); the input columns are "
   "<b>features</b>; the answer column is the <b>label</b>. We will not re-teach these &mdash; just watch them in action "
   "on a richer, five-sensor table.")),
code(
   "# Set up our toolboxes. This cell prints nothing - that is normal.\n"
   "import numpy as np\n"
   "import pandas as pd\n"
   "import matplotlib.pyplot as plt\n"
   "\n"
   "from sklearn.model_selection import train_test_split\n"
   "from sklearn.ensemble import RandomForestClassifier, IsolationForest\n"
   "from sklearn.metrics import accuracy_score, recall_score, confusion_matrix\n"
   "\n"
   "print('Tools loaded. We are ready to build the fleet.')"),
md(did("We loaded our toolboxes. Two new names to notice: <code>RandomForestClassifier</code> "
       "(the model we train first) and <code>IsolationForest</code> (the surprise at the end). "
       "More on both when we reach them.")),

code(
   "# Create 600 historical machines. In real life this table is your sensor logs;\n"
   "# here we generate it so every attendee has identical numbers.\n"
   "rng = np.random.default_rng(42)   # fixed seed => everyone sees the same data\n"
   "n = 600\n"
   "\n"
   "# Five sensor readings per machine:\n"
   "temperature        = np.round(rng.normal(70, 9, n), 1)                       # running temp (deg C)\n"
   "vibration          = np.round(np.clip(rng.normal(3.0, 1.0, n), 0.2, None), 2) # mm/s\n"
   "pressure           = np.round(rng.normal(5.0, 0.8, n), 2)                     # bar (normal is ~5)\n"
   "oil_quality        = np.round(np.clip(rng.normal(75, 12, n), 5, 100), 0)      # 0-100, higher = cleaner\n"
   "hours_since_service= rng.integers(50, 2000, n)                               # hours since last service\n"
   "\n"
   "# The hidden truth we pretend not to know. Failure risk goes UP with:\n"
   "#   high temperature, high vibration, abnormal pressure (far from 5 bar in EITHER\n"
   "#   direction), LOW oil quality (dirty oil), and many hours since service.\n"
   "risk = ( 0.060*(temperature - 70)\n"
   "       + 0.95 *(vibration - 3.0)\n"
   "       + 0.55 *np.abs(pressure - 5.0)\n"
   "       + 0.045*(75 - oil_quality)\n"
   "       + 0.0013*(hours_since_service - 1000)\n"
   "       + rng.normal(0, 0.35, n) )        # real-world noise: the world is not tidy\n"
   "\n"
   "will_fail_soon = (risk > 1.55).astype(int)   # 1 = failed soon after, 0 = kept running\n"
   "\n"
   "fleet = pd.DataFrame({\n"
   "    'temperature':         temperature,\n"
   "    'vibration':           vibration,\n"
   "    'pressure':            pressure,\n"
   "    'oil_quality':         oil_quality,\n"
   "    'hours_since_service': hours_since_service,\n"
   "    'will_fail_soon':      will_fail_soon,\n"
   "})\n"
   "\n"
   "fleet.head(8)   # peek at the first 8 machines"),
md(did("There is our fleet: 600 machines, one per row. The first five columns are the <b>features</b> "
       "(the sensor readings); the last column, <code>will_fail_soon</code>, is the <b>label</b> &mdash; the outcome "
       "we want to predict. Notice <code>oil_quality</code> runs the other way: a <i>higher</i> number means "
       "<i>cleaner</i> oil, so <i>low</i> oil quality is the worrying one.")),

md(section("How often do machines actually fail?", 3)),
md("Before modelling, always look at the balance of the label. If failures are rare, a lazy model could score well "
   "just by saying \"everything is fine\" &mdash; so we need to know the failure rate up front."),
code(
   "print('Fleet size (machines, columns):', fleet.shape)\n"
   "print()\n"
   "counts = fleet['will_fail_soon'].value_counts().sort_index()\n"
   "print('Outcome counts:')\n"
   "print('  kept running (0):', counts.get(0, 0))\n"
   "print('  failed soon  (1):', counts.get(1, 0))\n"
   "print()\n"
   "fail_rate = fleet['will_fail_soon'].mean()\n"
   "print('Failure rate:', round(fail_rate*100, 1), '% of the fleet failed soon')"),
md(did("Only about <b>one machine in five</b> fails soon &mdash; failures are the <b>minority</b>. That single fact "
       "shapes everything that follows: a model that lazily declares every machine healthy would still be right "
       "~80% of the time, yet would catch <b>zero</b> real failures. That is why, in a moment, accuracy alone will "
       "not be enough to trust the model.")),

md(section("Split features from label, then hold back a test set", 4)),
md(note("Same rhythm as Notebook 0: separate the feature table <code>X</code> from the label column <code>y</code>, "
        "then hide a quarter of the machines as a <b>test set</b> so we can judge the model on cases it never saw. "
        "We keep <code>stratify=y</code> so the test set has the same ~20% failure rate as the whole fleet.")),
code(
   "feature_cols = ['temperature', 'vibration', 'pressure', 'oil_quality', 'hours_since_service']\n"
   "X = fleet[feature_cols]      # the clues  (five sensors)\n"
   "y = fleet['will_fail_soon']  # the answer (failed soon or not)\n"
   "\n"
   "X_train, X_test, y_train, y_test = train_test_split(\n"
   "    X, y,\n"
   "    test_size=0.25,     # keep 25% hidden for the final test\n"
   "    random_state=0,     # fixed split so everyone matches\n"
   "    stratify=y,         # keep the same failure rate in both halves\n"
   ")\n"
   "\n"
   "print('Learn from :', X_train.shape[0], 'machines  (training set)')\n"
   "print('Tested on  :', X_test.shape[0],  'machines  (test set, kept hidden)')\n"
   "print('Failures in the hidden test set:', int(y_test.sum()))"),
md(did("450 machines go to training, 150 are locked away for the final test. Thanks to "
       "<code>stratify</code>, both halves carry the same ~20% failure rate, so the test is fair.")),

md(section("Train the model: a random forest", 5)),
md(vocab("Random forest",
   "In Notebook 0 we trained a single <b>decision tree</b> &mdash; one chain of yes/no questions. A <b>random forest</b> "
   "is simply <b>many small decision trees voting together</b>. Each tree sees a slightly different slice of the data "
   "and casts a vote; the forest goes with the majority. Many modest opinions combined beat one opinion &mdash; the "
   "same reason a review panel beats a lone reviewer. It is a workhorse of predictive maintenance.")),
code(
   "# Build a forest of 200 trees and let it study the training machines.\n"
   "model = RandomForestClassifier(\n"
   "    n_estimators=200,           # 200 trees vote\n"
   "    max_depth=8,                # let each tree learn a bit more detail\n"
   "    class_weight='balanced',    # value rare failures more, so we catch them\n"
   "    random_state=0,             # fixed so everyone gets the same forest\n"
   ")\n"
   "\n"
   "model.fit(X_train, y_train)   # <-- the learning happens here\n"
   "\n"
   "print('Training done. 200 trees have studied the fleet and are ready to vote.')"),
md(did("That one <code>.fit()</code> call trained all 200 trees at once. The forest has now learned, on its own, "
       "how the five sensors combine into failure risk. One deliberate choice: <code>class_weight='balanced'</code> "
       "tells the forest to take the <i>rare</i> failures seriously rather than ignore them &mdash; the exact knob you "
       "turn when missing a fault is far costlier than a false alarm. Next we check &mdash; honestly &mdash; how good it is.")),

md(section("Evaluate honestly: accuracy is not enough", 6)),
md(vocab("Quick reminders from Notebook 1",
   "<b>Recall</b> = of the machines that truly failed, what fraction did we catch? A <b>missed fault</b> is a real "
   "failure the model called healthy (dangerous &mdash; the machine breaks anyway). A <b>false alarm</b> is a healthy "
   "machine the model flagged (wasteful &mdash; we service it for nothing). The <b>confusion matrix</b> lays all four "
   "outcomes in one square. For rare, costly failures, <b>recall matters more than raw accuracy</b>.")),
code(
   "predictions = model.predict(X_test)   # the forest's vote for each hidden machine\n"
   "\n"
   "acc    = accuracy_score(y_test, predictions)\n"
   "recall = recall_score(y_test, predictions)   # fraction of real failures we caught\n"
   "\n"
   "print('Accuracy :', round(acc, 3),  '-> fraction of all machines called correctly')\n"
   "print('Recall   :', round(recall, 3), '-> fraction of REAL failures we actually caught')"),
md(did("Accuracy is high (~0.9), but the number that should hold your attention is <b>recall</b>: it tells us how "
       "many of the genuinely failing machines we caught in time. On rare failures you can have great accuracy and "
       "still miss faults &mdash; so we always read recall alongside it.")),
code(
   "# The confusion matrix: all four outcomes in one square.\n"
   "cm = confusion_matrix(y_test, predictions)   # rows = truth, cols = prediction\n"
   "tn, fp, fn, tp = cm.ravel()\n"
   "\n"
   "print('Confusion matrix (rows = truth, columns = prediction):')\n"
   "print('                     said FINE   said WILL FAIL')\n"
   "print(f'  truly fine         {tn:>6}        {fp:>6}')\n"
   "print(f'  truly will fail    {fn:>6}        {tp:>6}')\n"
   "print()\n"
   "print(f'Caught failures (good)        : {tp}')\n"
   "print(f'MISSED faults  (dangerous)    : {fn}   <- these break anyway')\n"
   "print(f'False alarms   (wasteful)     : {fp}   <- serviced for nothing')"),
md(did("Read it in plain words: of the real failures, the forest <b>caught most and missed only a few</b> &mdash; the "
       "missed ones are the dangerous corner (they fail anyway), and the false alarms are merely wasteful "
       "(we service a healthy machine). In real maintenance you would tune the model to push missed faults toward "
       "zero, even at the cost of a few more false alarms &mdash; a missed fault on the plant floor costs far more "
       "than an extra inspection.")),

md(section("Which sensor mattered most?", 7)),
md(vocab("Feature importance",
   "A model does not have to be a black box. <b>Feature importance</b> is a number, one per feature, telling you "
   "<b>how much the model leaned on each sensor</b> when making its calls. Bigger bar = the model found that sensor "
   "more useful. This is where predictive AI stops being a yes/no oracle and starts giving <b>engineers insight</b>: "
   "it points at <i>which signal</i> is driving failures across the fleet.")),
code(
   "# Every trained forest exposes how much it relied on each feature.\n"
   "importances = model.feature_importances_\n"
   "\n"
   "ranking = (pd.Series(importances, index=feature_cols)\n"
   "             .sort_values(ascending=True))   # ascending so the biggest bar lands on top\n"
   "\n"
   "print('How much the model leaned on each sensor (higher = more):')\n"
   "for name, val in ranking[::-1].items():\n"
   "    print(f'  {name:<20} {val:.3f}')"),
code(
   "# Draw it as a horizontal bar chart - the ranking is easier to read this way.\n"
   "plt.figure(figsize=(8, 5.5))\n"
   "plt.barh(ranking.index, ranking.values, color='#0b6e7a', edgecolor='white')\n"
   "plt.xlabel('Importance (share of the decision the model gave this sensor)')\n"
   "plt.title('Which sensor drove the failure predictions?')\n"
   "plt.grid(alpha=0.3, axis='x')\n"
   "plt.tight_layout()\n"
   "plt.show()"),
md(did("The forest tells us, in its own words, which sensors it trusted most &mdash; with <b>vibration</b> and "
       "<b>temperature</b> near the top, matching the common-sense story we started with. This is the payoff "
       "engineers love: the model is not just saying \"this machine will fail,\" it is saying <b>which signal to "
       "watch</b>. If vibration dominates across your fleet, that is a direct hint about where to focus inspections "
       "&mdash; insight you can act on, discovered automatically from the data rather than assumed.")),

md(section("Score three specific machines", 8)),
md("The whole point: a new machine reports its sensors, and we get an instant call plus a confidence. "
   "Let us run one clearly healthy machine, one clearly at-risk, and one genuinely borderline."),
code(
   "# Three machines with very different sensor profiles.\n"
   "new_machines = pd.DataFrame([\n"
   "    # cool, smooth, normal pressure, clean oil, recently serviced -> should look healthy\n"
   "    {'temperature': 64, 'vibration': 2.1, 'pressure': 5.0, 'oil_quality': 90, 'hours_since_service': 200},\n"
   "    # hot, shaky, off-pressure, dirty oil, long overdue -> should look at-risk\n"
   "    {'temperature': 88, 'vibration': 5.2, 'pressure': 6.6, 'oil_quality': 35, 'hours_since_service': 1900},\n"
   "    # middling on everything -> genuinely borderline\n"
   "    {'temperature': 73, 'vibration': 3.1, 'pressure': 5.2, 'oil_quality': 68, 'hours_since_service': 950},\n"
   "], index=['Machine A (healthy?)', 'Machine B (at-risk?)', 'Machine C (borderline?)'])\n"
   "\n"
   "guesses     = model.predict(new_machines)\n"
   "confidences = model.predict_proba(new_machines)[:, 1]   # probability of 'will fail soon'\n"
   "\n"
   "for name, guess, conf in zip(new_machines.index, guesses, confidences):\n"
   "    verdict = 'WILL FAIL SOON' if guess == 1 else 'looks fine'\n"
   "    print(f'{name:<26} -> {verdict:<16} (failure confidence {round(conf*100):>3} %)')"),
md(did("The forest clears the cool/smooth machine, flags the hot/shaky/overdue one with high confidence, and lands "
       "the middling machine near the middle &mdash; exactly what an experienced engineer would say. The difference: "
       "the model does this for the whole fleet in a heartbeat, consistently, every shift. That confidence number is "
       "also how you <b>prioritise</b>: service the 92%-risk machines before the 55%-risk ones.")),

md(section("What if we have NO failure labels?", 9)),
md(note("Everything above needed a <code>will_fail_soon</code> column &mdash; a record of what failed. But often you "
        "install sensors on a new fleet and have <b>only the readings, with no failure history at all</b>. You cannot "
        "train the model we just built, because there are no answers to learn from. So is AI useless here? Not at all "
        "&mdash; this is where the <i>other half</i> of machine learning begins.")),
md(vocab("Supervised vs unsupervised",
   "Everything so far was <b>supervised</b> learning: we learned from labelled examples (each machine came with its "
   "known answer). <b>Unsupervised</b> learning has <b>no labels at all</b> &mdash; the model gets only the readings "
   "and must find structure on its own. No answer key, no teacher; just the data.")),
md(vocab("Anomaly detection",
   "One powerful unsupervised tool is <b>anomaly detection</b>: find the machines that look <b>unusual compared to the "
   "normal crowd</b>, without ever being told what failure looks like. The idea is simple &mdash; most machines behave "
   "normally, so the few that sit far from the pack are the ones worth a closer look.")),
code(
   "# Hand the model ONLY the sensors - we deliberately ignore will_fail_soon now,\n"
   "# pretending we never had failure labels in the first place.\n"
   "X_unlabelled = fleet[feature_cols]\n"
   "\n"
   "detector = IsolationForest(\n"
   "    contamination=0.08,   # assume ~8% of machines are unusual enough to flag\n"
   "    random_state=0,\n"
   ")\n"
   "flag = detector.fit_predict(X_unlabelled)   # -1 = anomaly (unusual), 1 = normal\n"
   "\n"
   "fleet_view = fleet.copy()\n"
   "fleet_view['anomaly'] = (flag == -1)\n"
   "\n"
   "n_flagged = int(fleet_view['anomaly'].sum())\n"
   "print('Machines flagged as unusual:', n_flagged, 'out of', len(fleet_view))\n"
   "print()\n"
   "print('A few of the flagged (unusual) machines:')\n"
   "print(fleet_view[fleet_view['anomaly']][feature_cols].head(6).to_string())"),
md(did("With <b>no labels whatsoever</b>, the model picked out the ~8% of machines that look least like the normal "
       "crowd. Glance at their numbers: they tend to sit at extremes &mdash; very hot, very shaky, very off-pressure. "
       "The model was never told what \"bad\" means; it simply found the <b>odd ones out</b>.")),
code(
   "# See it: temperature vs vibration, normal machines green, flagged ones red X.\n"
   "normal  = fleet_view[~fleet_view['anomaly']]\n"
   "unusual = fleet_view[ fleet_view['anomaly']]\n"
   "\n"
   "plt.figure(figsize=(8, 5.5))\n"
   "plt.scatter(normal['temperature'], normal['vibration'],\n"
   "            c='#2e7d32', alpha=0.6, edgecolors='white', label='Normal machine')\n"
   "plt.scatter(unusual['temperature'], unusual['vibration'],\n"
   "            c='#9c2b2b', marker='X', s=90, label='Flagged as unusual')\n"
   "\n"
   "plt.xlabel('Temperature (deg C)')\n"
   "plt.ylabel('Vibration (mm/s)')\n"
   "plt.title('Anomaly detection found the odd machines on its own')\n"
   "plt.legend()\n"
   "plt.grid(alpha=0.3)\n"
   "plt.tight_layout()\n"
   "plt.show()"),
md(did("The red X marks sit out at the <b>edges</b> of the cloud &mdash; the extreme corners of temperature and "
       "vibration &mdash; while the green normal machines fill the middle. The model drew that boundary with no "
       "labels at all.")),
md(watchout("An anomaly is <b>not a guaranteed failure</b>. A machine can be unusual for innocent reasons (a new "
            "model, a cold-start reading, a sensor glitch). What anomaly detection gives you is a <b>short, ranked "
            "list of machines worth a human inspection</b> &mdash; a way to point your limited attention at the few "
            "machines most likely to surprise you, instead of checking all 600 by hand.")),

md(turn(
   "Make it your own. Edit a number, press <b>Shift + Enter</b>, and watch what changes:<br>"
   "1. In <b>Step 8</b>, take Machine C and raise <code>vibration</code> to <code>5.5</code> and "
   "<code>temperature</code> to <code>90</code>. Re-run &mdash; watch the confidence climb toward 'will fail soon'.<br>"
   "2. In <b>Step 9</b>, change <code>contamination=0.08</code> to <code>0.20</code> to flag more machines, or "
   "<code>0.03</code> to flag fewer. Re-run the scatter and see the red X marks spread or shrink.<br>"
   "3. In <b>Step 4</b>, drop <code>oil_quality</code> from <code>feature_cols</code>, then re-run Steps 4&ndash;7. "
   "Watch the feature-importance chart re-shuffle now that one clue is gone.")),

md(recap("What we learned in Notebook 3", [
   "<b>Predictive maintenance</b> beats fix-on-break and fixed-schedule: service the right machine, just in time.",
   "A <b>random forest</b> is many small decision trees voting together &mdash; a workhorse for this job.",
   "Failures are rare, so <b>recall</b> (did we catch the real failures?) matters more than raw accuracy; the "
   "<b>confusion matrix</b> separates dangerous missed faults from merely wasteful false alarms.",
   "<b>Feature importance</b> turns the model into engineer insight &mdash; it tells you <i>which sensor</i> drives "
   "failures, not just yes/no.",
   "<b>Supervised vs unsupervised</b>: with labels we predict; with none, we still find structure.",
   "<b>Anomaly detection</b> flags the unusual machines with no labels at all &mdash; a ranked shortlist for "
   "human inspection.",
])),
md(nextup(
   "<b>Notebook 4 &mdash; Text Analytics.</b> So far every clue has been a <i>number</i> from a sensor. But a huge "
   "amount of maintenance knowledge lives in <b>written reports</b> &mdash; the free-text notes a technician types after "
   "a job. Next we turn that messy text into something a model can predict from, and the supervised rhythm you now "
   "know carries straight over.")),
]

build(cells, "/Users/flam/Desktop/HAL_AI/notebooks/03_predictive_maintenance.ipynb",
      title="Predictive AI 03 - Predictive Maintenance")
