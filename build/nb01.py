import sys; sys.path.insert(0, "/tmp")
from nbbuild import *

# A tiny inline legend reminding readers what the coloured boxes mean (same
# language as Notebook 0, so returning attendees feel at home).
LEGEND = """
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:14px;color:#333;line-height:1.7;">
As you scroll, you will meet the same coloured boxes as Notebook 0:
<br><b style="color:#0b6e7a;">Teal — Vocabulary:</b> a new word, in plain English.
<br><b style="color:#2e7d32;">Green — What just happened:</b> what the cell above actually did.
<br><b style="color:#b26a00;">Amber — Your turn:</b> a safe number to change, then re-run.
<br><b style="color:#5b2a86;">Purple — Recap / Coming up:</b> the big picture.
</div>
"""

cells = [
md(banner("Notebook 1 of 6", "Classification: Sorting Things Into Categories",
   "A final quality-control gate that decides PASS vs REJECT on finished parts")),

md("## How to use this notebook\n\n"
   "Same as before: this is **hands-on**, but you never write code. You only **run** the cells "
   "top to bottom and read what comes out.\n\n"
   "- To run a cell: click it, then press **Shift + Enter** (or the &#9654; play button on its left).\n"
   "- Run them **in order**. Each cell builds on the one above it.\n"
   "- If anything looks broken: **Runtime &rarr; Restart and run all**, then start again.\n\n"
   + LEGEND),

md(bigidea(
   "In Notebook 0 we predicted whether a machine would need service &mdash; a yes/no answer. "
   "That kind of task, where the model sorts each case into one of a few <b>categories</b>, is called "
   "<b>classification</b>, and it is the single most common job in predictive AI.<br><br>"
   "This notebook slows right down on it. We will build a working quality-control classifier, and then &mdash; the "
   "important part &mdash; learn to read <i>where</i> and <i>why</i> it makes mistakes. You will see why a high accuracy "
   "score can be completely misleading, and how engineers actually judge a model when the thing it must catch is rare.")),

md(story(
   "<b>Our scenario: the final quality-control gate.</b><br>"
   "A workshop finishes a batch of parts. Before they ship, every part passes through a final <b>quality-control check</b>. "
   "Each part has a few simple measurements taken: how far its size is off target (<b>dimension error</b>), how rough its "
   "<b>surface</b> is, and how far its <b>weight</b> is from spec. Most parts are fine and should <b>PASS</b>. A minority are out "
   "of spec and must be <b>REJECTED</b> before they reach a customer.<br><br>"
   "The question: <b>can the computer look at a part's measurements and predict PASS or REJECT</b>, so good parts flow through "
   "and bad ones get caught? No special domain knowledge needed &mdash; bigger errors, rougher surfaces and larger weight "
   "deviations mean a part is more likely out of spec. That common-sense pattern is all we lean on.")),

md(section("Re-introduce the task by name", 1)),
md(vocab("Classification",
   "<b>Classification</b> is predicting which <b>category</b> a case belongs to. The answer is not a number on a scale &mdash; "
   "it is a choice from a short list of labels. Here the list has two entries: <b>PASS</b> or <b>REJECT</b>. "
   "\"Spam or not spam\", \"approve or decline\", \"defective or fine\" are all classification.")),
md(vocab("Classes",
   "The possible answers are called the <b>classes</b>. Our two classes are <b>PASS</b> (we will store it as <code>0</code>) "
   "and <b>REJECT</b> (stored as <code>1</code>). Computers prefer numbers to words, so we label the category we care about "
   "catching &mdash; REJECT &mdash; as <code>1</code>.")),

md(section("Set up our tools", 2)),
md(vocab("Library",
   "A quick reminder from Notebook 0: a <b>library</b> is a ready-made toolbox of code. <code>pandas</code> handles tables, "
   "<code>scikit-learn</code> is the machine-learning toolbox, <code>matplotlib</code> draws charts. We just borrow them.")),
code(
   "# Import the toolboxes we need. This cell shows no visible output - that is\n"
   "# normal. It only makes the tools available to the cells below.\n"
   "import numpy as np\n"
   "import pandas as pd\n"
   "import matplotlib.pyplot as plt\n"
   "\n"
   "from sklearn.model_selection import train_test_split\n"
   "from sklearn.preprocessing import StandardScaler\n"
   "from sklearn.pipeline import make_pipeline\n"
   "from sklearn.linear_model import LogisticRegression\n"
   "from sklearn.metrics import (accuracy_score, confusion_matrix,\n"
   "                             precision_score, recall_score)\n"
   "\n"
   "print('Tools loaded. We are ready.')"),
md(did("We loaded the toolboxes. Nothing dramatic on screen, and that is expected &mdash; this cell only prepares "
       "the tools the rest of the notebook uses.")),

md(section("Build the data: 400 past parts", 3)),
md(vocab("Dataset and features",
   "Reminder from Notebook 0: a <b>dataset</b> is just a table &mdash; one row per part. The input columns "
   "(<code>dimension_error_mm</code>, <code>surface_roughness</code>, <code>weight_deviation_g</code>) are the "
   "<b>features</b>, the clues the model gets to look at. The answer column is the <b>label</b>.")),
code(
   "# We create 400 past parts that already went through quality control, so we\n"
   "# know each one's real outcome. In real life this table would come from your\n"
   "# inspection logs; here we generate it so everyone sees identical numbers.\n"
   "rng = np.random.default_rng(42)   # fixed seed => same data for everyone\n"
   "n = 400\n"
   "\n"
   "# Three simple measurements per finished part:\n"
   "dimension_error_mm = np.round(np.abs(rng.normal(0.0, 0.05, n)), 3)            # size off target (mm)\n"
   "surface_roughness  = np.round(np.clip(rng.normal(1.2, 0.4, n), 0.2, None), 2) # roughness (Ra microns)\n"
   "weight_deviation_g = np.round(rng.normal(0.0, 4.0, n), 1)                     # weight off target (grams)\n"
   "\n"
   "# The hidden truth we pretend not to know: bigger size errors, rougher\n"
   "# surfaces and larger weight deviations push a part toward being out of spec\n"
   "# (plus a little real-world noise, because inspection is never perfectly clean).\n"
   "risk = (35.0*dimension_error_mm + 2.4*(surface_roughness - 1.2)\n"
   "        + 0.14*np.abs(weight_deviation_g) + rng.normal(0, 0.32, n))\n"
   "status = (risk > 2.95).astype(int)   # 1 = REJECT (out of spec), 0 = PASS\n"
   "\n"
   "df = pd.DataFrame({\n"
   "    'dimension_error_mm': dimension_error_mm,\n"
   "    'surface_roughness':  surface_roughness,\n"
   "    'weight_deviation_g': weight_deviation_g,\n"
   "    'status':             status,\n"
   "})\n"
   "\n"
   "df.head(8)   # show the first 8 parts"),
md(did("There is our <b>dataset</b>: 400 parts, one per row. The first three columns are the <b>features</b> (the "
       "measurements). The last column, <code>status</code>, is the <b>label</b> &mdash; <code>0</code> for PASS, "
       "<code>1</code> for REJECT &mdash; the outcome we want to predict for a new part.")),

md(section("Look at the class balance", 4)),
md("Before any modelling, always look at the data. For classification the most important first question is: "
   "*how many of each class do we have?* The answer changes everything about how we judge the model later."),
code(
   "print('Rows and columns:', df.shape)\n"
   "print()\n"
   "\n"
   "counts = df['status'].value_counts().sort_index()\n"
   "print('How many PASS vs REJECT:')\n"
   "print('  PASS   (0):', counts[0])\n"
   "print('  REJECT (1):', counts[1])\n"
   "print()\n"
   "\n"
   "reject_share = 100 * df['status'].mean()\n"
   "print('REJECT is the minority class:', round(reject_share, 1), '% of all parts.')"),
md(watchout("Only about <b>20%</b> of parts are REJECT &mdash; the class is <b>imbalanced</b>. This is completely "
            "realistic (most finished parts are fine) but it is also a trap waiting to spring. Hold this number in your "
            "head: <b>roughly 4 out of every 5 parts PASS</b>. We will see in Step 7 exactly why that matters.")),

md(section("See the two classes with our own eyes", 5)),
md("Before any maths, let us simply *draw* the parts. We plot two of the measurements against each other and colour "
   "each part green for PASS and red for REJECT. If our common-sense story holds, the colours should sit in different regions."),
code(
   "plt.figure(figsize=(8, 5.5))\n"
   "\n"
   "good = df[df['status'] == 0]   # the parts that PASSED\n"
   "bad  = df[df['status'] == 1]   # the parts that were REJECTED\n"
   "\n"
   "plt.scatter(good['dimension_error_mm'], good['surface_roughness'],\n"
   "            c='#2e7d32', label='PASS',   alpha=0.7, edgecolors='white')\n"
   "plt.scatter(bad['dimension_error_mm'],  bad['surface_roughness'],\n"
   "            c='#9c2b2b', label='REJECT', alpha=0.7, edgecolors='white')\n"
   "\n"
   "plt.xlabel('Dimension error (mm) - how far off target size')\n"
   "plt.ylabel('Surface roughness (Ra microns)')\n"
   "plt.title('Each dot is one finished part')\n"
   "plt.legend()\n"
   "plt.grid(alpha=0.3)\n"
   "plt.show()"),
md(did("Notice two things. First, the red REJECT dots cluster toward the <b>top-right</b> &mdash; larger size error and "
       "rougher surface &mdash; exactly the common-sense pattern. Finding a boundary between the colours is the model's whole "
       "job. Second, look how <b>few</b> red dots there are compared to green. That scarcity is the imbalance from Step 4, "
       "and it is about to matter a great deal.")),

md(section("Split features from label, then hold back a test set", 6)),
md(vocab("X / y and train / test split",
   "Reminders from Notebook 0: we call the feature table <code>X</code> (the clues) and the label column <code>y</code> "
   "(the answers). We then split the parts into a <b>training set</b> the model learns from, and a hidden <b>test set</b> "
   "used only at the end to score it on parts it has never seen. We use <code>stratify=y</code> so the rare REJECT class "
   "appears in the same proportion in both halves.")),
code(
   "X = df[['dimension_error_mm', 'surface_roughness', 'weight_deviation_g']]   # the clues\n"
   "y = df['status']                                                           # the answers\n"
   "\n"
   "X_train, X_test, y_train, y_test = train_test_split(\n"
   "    X, y,\n"
   "    test_size=0.25,    # keep 25% (100 parts) hidden for the final test\n"
   "    random_state=0,    # fixed split so everyone gets the same result\n"
   "    stratify=y,        # keep the same PASS/REJECT mix in both halves\n"
   ")\n"
   "\n"
   "print('Learn from :', X_train.shape[0], 'parts  (training set)')\n"
   "print('Tested on  :', X_test.shape[0],  'parts  (test set, kept hidden)')\n"
   "print('REJECT parts hidden in the test set:', int(y_test.sum()),\n"
   "      'out of', len(y_test))"),
md(did("300 parts go into the training set and 100 are locked away as the test set. Of those 100 hidden parts, only "
       "about 20 are genuine REJECTs &mdash; the rest PASS. Remember that count: it is the heart of the next step.")),

md(section("Train the classifier", 7)),
md(vocab("Model and training (fitting)",
   "A <b>model</b> is the pattern-finder; <b>training</b> &mdash; the method literally called <code>.fit()</code> &mdash; is "
   "where it studies the training parts and discovers the pattern. We use <b>logistic regression</b>, a classic, fast, "
   "well-understood classifier. (The <code>StandardScaler</code> in front just puts the three measurements on a comparable "
   "scale first, since they are in very different units &mdash; thousandths of a mm vs grams.)")),
code(
   "# A pipeline = scale the measurements, then fit the classifier, as one unit.\n"
   "model = make_pipeline(StandardScaler(),\n"
   "                      LogisticRegression(max_iter=1000))\n"
   "\n"
   "model.fit(X_train, y_train)   # <-- the model studies the training parts\n"
   "\n"
   "print('Training done. The model has found its PASS / REJECT pattern.')"),
md(did("That one <code>.fit()</code> call is the entire act of learning. The model has now worked out how the three "
       "measurements combine into a PASS-or-REJECT decision. Next we put it to the test &mdash; and meet the most important "
       "lesson in this notebook.")),

md(section("The accuracy trap: a lazy model that looks great", 8)),
md("Here is the lesson that separates people who really understand classification from those who just quote a score. "
   "Before we even look at our trained model, let us build a deliberately <b>lazy</b> model &mdash; one that does no thinking "
   "at all and simply predicts <b>PASS for every single part</b>. Then we measure its accuracy."),
md(vocab("Accuracy",
   "<b>Accuracy</b> is the simplest score: out of all test parts, what fraction did the model label correctly? "
   "<code>0.80</code> means 80 out of 100 right. It sounds like the obvious way to judge a model &mdash; and for imbalanced "
   "problems it can be dangerously misleading.")),
code(
   "# The lazy model: ignore the measurements, just say PASS (0) for everything.\n"
   "lazy_predictions = np.zeros(len(y_test), dtype=int)   # all zeros = all PASS\n"
   "\n"
   "lazy_accuracy = accuracy_score(y_test, lazy_predictions)\n"
   "print('Lazy model accuracy (always predicts PASS):', round(lazy_accuracy, 3))\n"
   "print('In plain words: about', round(lazy_accuracy*100),\n"
   "      'out of every 100 labelled correctly.')\n"
   "print()\n"
   "\n"
   "# But how many of the genuinely bad parts did this lazy model catch?\n"
   "rejects_caught = int(((lazy_predictions == 1) & (y_test == 1)).sum())\n"
   "rejects_total  = int((y_test == 1).sum())\n"
   "print('REJECT parts it actually caught:', rejects_caught, 'out of', rejects_total)"),
md(watchout("Read that result slowly. A model that does <b>no thinking whatsoever</b> &mdash; it just stamps PASS on "
            "everything &mdash; scores about <b>80% accuracy</b>. It looks like a B-grade student. But it caught <b>ZERO</b> of "
            "the bad parts. Every single out-of-spec part sailed straight through to the customer. On an imbalanced problem, "
            "<b>high accuracy can be worthless</b>: you can ace it by ignoring the very thing you were built to find. "
            "Accuracy alone is not enough &mdash; we need a tool that shows us <i>which kinds</i> of mistakes are happening.")),

md(section("The confusion matrix: where mistakes actually happen", 9)),
md(vocab("Confusion matrix",
   "A <b>confusion matrix</b> is a small table that splits the predictions into four buckets, so we can see not just "
   "<i>how many</i> the model got wrong but <i>which kind</i> of wrong. For a PASS/REJECT problem it is a 2&times;2 grid: "
   "real answer down the side, the model's call across the top.")),
md(vocab("False alarm / Missed fault",
   "Two of the four buckets are the mistakes, and they are <b>not</b> equally serious:<br>"
   "<b>False alarm</b> &mdash; a <i>good</i> part the model wrongly REJECTED. Annoying and wasteful (you scrap a fine part), "
   "but safe. (Statisticians call this a <i>false positive</i>.)<br>"
   "<b>Missed fault</b> &mdash; a <i>bad</i> part the model wrongly PASSED. This is the dangerous one: a defective part reaches "
   "the customer. (A <i>false negative</i>.)")),
code(
   "# Now use our REAL trained model on the hidden test parts.\n"
   "predictions = model.predict(X_test)\n"
   "\n"
   "# confusion_matrix returns the four buckets. We unpack them by name so the\n"
   "# meaning is crystal clear (tn, fp, fn, tp).\n"
   "tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()\n"
   "\n"
   "print('Out of', len(y_test), 'hidden parts, the model produced:')\n"
   "print('  True passes  (good part, correctly PASSED) :', tn)\n"
   "print('  True rejects (bad part,  correctly REJECTED):', tp)\n"
   "print('  False alarms (good part, wrongly REJECTED) :', fp)\n"
   "print('  Missed faults(bad part,  wrongly PASSED)   :', fn)"),
md(did("Unlike the lazy model, our trained classifier <b>actually catches most of the bad parts</b> &mdash; that is the "
       "<i>true rejects</i> number. It is not flawless: it raised a small number of <i>false alarms</i> (good parts it scrapped "
       "needlessly) and, more worryingly, let a few <i>missed faults</i> slip through. Now let us draw the same four numbers as a "
       "labelled grid, which is how engineers usually read them.")),
code(
   "# Draw the confusion matrix as a labelled 2x2 grid.\n"
   "cm = confusion_matrix(y_test, predictions)\n"
   "\n"
   "fig, ax = plt.subplots(figsize=(8, 5.5))\n"
   "ax.imshow(cm, cmap='Blues')\n"
   "\n"
   "# Friendly labels instead of bare 0s and 1s.\n"
   "ax.set_xticks([0, 1]); ax.set_xticklabels(['Model said\\nPASS', 'Model said\\nREJECT'])\n"
   "ax.set_yticks([0, 1]); ax.set_yticklabels(['Really\\nPASS', 'Really\\nREJECT'])\n"
   "ax.set_xlabel('What the model predicted')\n"
   "ax.set_ylabel('The real answer')\n"
   "ax.set_title('Confusion matrix: the four buckets')\n"
   "\n"
   "# Write the count and a plain-English name inside each of the four cells.\n"
   "names = [['True passes', 'False alarms'],\n"
   "         ['Missed faults', 'True rejects']]\n"
   "for i in range(2):\n"
   "    for j in range(2):\n"
   "        shade = 'white' if cm[i, j] > cm.max()/2 else '#1f2d3d'\n"
   "        ax.text(j, i, f'{cm[i, j]}\\n{names[i][j]}',\n"
   "                ha='center', va='center', color=shade, fontsize=13, fontweight='bold')\n"
   "\n"
   "plt.tight_layout()\n"
   "plt.show()"),
md(did("This single grid tells the whole story. The two cells on the <b>diagonal</b> (top-left and bottom-right) are the "
       "correct calls &mdash; true passes and true rejects. The two <b>off-diagonal</b> cells are the mistakes: top-right is the "
       "false alarms (good parts wrongly rejected), bottom-left is the missed faults (bad parts wrongly passed). For a safety "
       "gate, that bottom-left number is the one that should worry you most.")),

md(section("Precision and recall: two honest scores", 10)),
md(vocab("Precision and recall",
   "Two numbers that say far more than accuracy, in plain words &mdash; no formula to memorise:<br>"
   "<b>Precision</b> answers: <i>\"when the model shouts REJECT, how often is it actually right?\"</i> Low precision means "
   "lots of false alarms &mdash; you scrap good parts.<br>"
   "<b>Recall</b> answers: <i>\"of all the genuinely bad parts, how many did the model actually catch?\"</i> Low recall means "
   "lots of missed faults &mdash; bad parts escape.")),
code(
   "precision = precision_score(y_test, predictions)   # of the REJECT calls, how many were right\n"
   "recall    = recall_score(y_test, predictions)      # of the truly bad parts, how many we caught\n"
   "accuracy  = accuracy_score(y_test, predictions)\n"
   "\n"
   "print('Our trained model on the hidden test parts:')\n"
   "print('  Accuracy :', round(accuracy, 3), ' (overall fraction labelled correctly)')\n"
   "print('  Precision:', round(precision, 3),\n"
   "      ' -> when it says REJECT, it is right', round(precision*100), '% of the time')\n"
   "print('  Recall   :', round(recall, 3),\n"
   "      ' -> it caught', round(recall*100), '% of all the truly bad parts')"),
md(note("Precision and recall usually pull against each other &mdash; this is the central <b>trade-off</b> in "
        "classification. If you make the model quicker to shout REJECT, it catches more bad parts (recall up) but also "
        "scraps more good ones (precision down), and vice-versa. <b>Which one matters more depends entirely on the "
        "cost of each mistake.</b> For a final safety gate, a missed fault (a defective part reaching a customer) is far "
        "more costly than a false alarm (scrapping a good part), so here we would care most about <b>recall</b> &mdash; catching "
        "the bad parts &mdash; even if it costs us a few extra false alarms.")),
md(did("Notice that accuracy and recall tell different stories. The lazy model and our real model have fairly similar "
       "<i>accuracy</i>, but their <i>recall</i> is worlds apart &mdash; the lazy model's recall is zero, ours catches most bad "
       "parts. That gap is exactly why engineers report precision and recall, not just accuracy, on any problem where the "
       "thing they must catch is rare.")),

md(section("Use it on brand-new parts", 11)),
md("This is the payoff. Three new parts come off the line. We have their three measurements but no idea of the verdict. "
   "We hand each to the trained model and get an instant call, plus a <b>confidence</b> &mdash; the model's own probability "
   "that the part should be rejected."),
code(
   "# Three new parts: one clearly good, one clearly bad, one genuinely borderline.\n"
   "new_parts = pd.DataFrame([\n"
   "    {'dimension_error_mm': 0.010, 'surface_roughness': 0.70, 'weight_deviation_g': 1.5},  # clearly good\n"
   "    {'dimension_error_mm': 0.090, 'surface_roughness': 2.10, 'weight_deviation_g': 9.0},  # clearly bad\n"
   "    {'dimension_error_mm': 0.050, 'surface_roughness': 1.55, 'weight_deviation_g': 5.0},  # borderline\n"
   "])\n"
   "\n"
   "calls       = model.predict(new_parts)              # 0 = PASS, 1 = REJECT\n"
   "confidences = model.predict_proba(new_parts)[:, 1]  # probability of REJECT\n"
   "\n"
   "labels = ['clearly good', 'clearly bad', 'borderline']\n"
   "for i in range(len(new_parts)):\n"
   "    verdict = 'REJECT' if calls[i] == 1 else 'PASS'\n"
   "    print(f'{labels[i]:13s} -> {verdict:6s}   '\n"
   "          f'(confidence it is a REJECT: {round(confidences[i]*100)}%)')"),
md(did("The model clears the clearly-good part, rejects the clearly-bad one with near-total confidence, and lands the "
       "borderline part close to a coin-flip &mdash; which is honest, because that part really is on the fence. The confidence "
       "number is useful in practice: you might auto-PASS very low scores, auto-REJECT very high ones, and send only the "
       "uncertain middle to a human inspector.")),

md(turn(
   "Make it your own. Edit a number, then press <b>Shift + Enter</b> to re-run that cell (and the cells below it):<br>"
   "1. In Step 11, push the borderline part toward the bad corner &mdash; set <code>surface_roughness</code> to "
   "<code>1.9</code> and <code>dimension_error_mm</code> to <code>0.08</code>. Watch the verdict flip and the confidence climb.<br>"
   "2. In Step 3, change the REJECT threshold <code>2.95</code> to <code>2.5</code> (more parts become REJECT), then "
   "<b>Runtime &rarr; Restart and run all</b>. Watch the confusion matrix and the recall move.<br>"
   "3. In Step 5, plot a different pair of features &mdash; swap <code>surface_roughness</code> for "
   "<code>weight_deviation_g</code> on the y-axis &mdash; and see whether the colours still separate.")),

md(recap("What we learned in Notebook 1", [
   "<b>Classification</b> predicts a <b>category</b> (a <b>class</b>) &mdash; here PASS vs REJECT &mdash; not a number.",
   "When one class is rare (<b>imbalanced</b> data), <b>accuracy can lie</b>: a do-nothing model that always says PASS scored ~80% yet caught zero bad parts.",
   "A <b>confusion matrix</b> splits results into four buckets: true passes, true rejects, <b>false alarms</b> (good part wrongly rejected) and <b>missed faults</b> (bad part wrongly passed).",
   "<b>Precision</b> = when we flag REJECT, how often we are right. <b>Recall</b> = of all truly bad parts, how many we caught.",
   "Precision and recall <b>trade off</b>; for a safety gate, missed faults hurt most, so <b>recall</b> usually matters more.",
   "The model gives a <b>confidence</b> with each call, so uncertain parts can be sent to a human.",
])),
md(nextup(
   "<b>Notebook 2 &mdash; Regression &amp; Forecasting.</b> So far our answers have been categories (PASS / REJECT, "
   "needs-service / fine). Next we predict an actual <b>number</b> on a scale &mdash; a cost, a measurement, a quantity &mdash; "
   "and learn how we judge a model when the answer is no longer a simple yes or no.")),
]

build(cells, "/Users/flam/Desktop/HAL_AI/notebooks/01_classification.ipynb",
      title="Predictive AI 01 - Classification")
