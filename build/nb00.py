import sys; sys.path.insert(0, "/tmp")
from nbbuild import *

COMPARE_TABLE = """
<table style="border-collapse:collapse;width:100%;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:15px;margin:8px 0;">
<tr style="background:#1f2d3d;color:#fff;">
  <th style="padding:10px 14px;text-align:left;">&nbsp;</th>
  <th style="padding:10px 14px;text-align:left;">Predictive AI &nbsp;(today's session)</th>
  <th style="padding:10px 14px;text-align:left;">Generative AI &nbsp;(ChatGPT, etc.)</th>
</tr>
<tr style="background:#eef4f5;">
  <td style="padding:10px 14px;font-weight:700;">What it does</td>
  <td style="padding:10px 14px;">Looks at past records and predicts a fact about a new case</td>
  <td style="padding:10px 14px;">Creates new content — text, images, audio</td>
</tr>
<tr>
  <td style="padding:10px 14px;font-weight:700;">Typical answer</td>
  <td style="padding:10px 14px;">"This machine will likely need service" / "Cost = 4.2 lakh"</td>
  <td style="padding:10px 14px;">"Here is a 200-word summary / a picture / a song"</td>
</tr>
<tr style="background:#eef4f5;">
  <td style="padding:10px 14px;font-weight:700;">How old is it</td>
  <td style="padding:10px 14px;">Decades. Runs quietly in banks, factories, airlines today</td>
  <td style="padding:10px 14px;">Newer — the recent wave everyone talks about</td>
</tr>
<tr>
  <td style="padding:10px 14px;font-weight:700;">This session</td>
  <td style="padding:10px 14px;font-weight:700;color:#0b6e7a;">Our entire focus</td>
  <td style="padding:10px 14px;">Covered later, by other speakers</td>
</tr>
</table>
"""

LEGEND = """
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:14px;color:#333;line-height:1.7;">
As you scroll, you will meet four kinds of coloured boxes:
<br><b style="color:#0b6e7a;">Teal — Vocabulary:</b> a new word, in plain English.
<br><b style="color:#2e7d32;">Green — What just happened:</b> what the cell above actually did.
<br><b style="color:#b26a00;">Amber — Your turn:</b> a safe number to change, then re-run.
<br><b style="color:#5b2a86;">Purple — Recap / Coming up:</b> the big picture.
</div>
"""

cells = [
md(banner("Notebook 0 of 6", "What is Predictive AI?",
   "The mindset, and the words everyone keeps using &mdash; on one tiny equipment example")),

md("## How to use this notebook\n\n"
   "This is a **hands-on** notebook. You do not need to write any code. "
   "You only **run** the cells, top to bottom, and read what comes out.\n\n"
   "- To run a cell: click it, then press **Shift + Enter** (or the &#9654; play button on its left).\n"
   "- Run them **in order**. Each cell builds on the one above it.\n"
   "- If something looks broken, use the menu: **Runtime &rarr; Restart and run all**, then start again.\n\n"
   + LEGEND),

md(bigidea(
   "People walk into the word \"AI\" with one of two beliefs: either <b>it can do anything</b>, "
   "or <b>it is all hype</b>. The truth sits in between and is surprisingly ordinary.<br><br>"
   "<b>Predictive AI learns a pattern from past examples, and uses that pattern to make a call about a new case it has never seen.</b> "
   "Think of a seasoned maintenance technician who has inspected thousands of machines. Show them a new one and they say "
   "\"this one will give trouble soon\" &mdash; not by magic, but because they have <i>seen the pattern before</i>. "
   "We are going to teach a computer to do exactly that, and watch it happen step by step.")),

md("## Predictive AI vs. Generative AI\n\n"
   "Most people today meet AI through ChatGPT, which **generates** new text. That is only one half of the field. "
   "The other half &mdash; the older, quieter, workhorse half &mdash; **predicts**. That is what we focus on today.\n\n"
   + COMPARE_TABLE),

md(story(
   "<b>Our running example: equipment servicing.</b><br>"
   "Imagine a workshop that maintains a fleet of identical machines. Over the years they have kept simple records for each machine: "
   "how many <b>hours</b> it has run, its running <b>temperature</b>, and how much it <b>vibrates</b>. "
   "For older records they also know the outcome: did that machine eventually <b>need a service</b>, or not?<br><br>"
   "The question we want answered: <b>given a machine's numbers, can we predict whether it will need servicing &mdash; before it breaks down?</b> "
   "No aircraft or engine knowledge required. Hotter, older, shakier machines tend to need attention. That common-sense pattern is all we rely on.")),

md(section("Set up our tools", 1)),
md(vocab("Library",
   "A <b>library</b> is a ready-made toolbox of code someone else wrote, so we do not start from scratch. "
   "<code>pandas</code> handles tables, <code>scikit-learn</code> is the machine-learning toolbox, "
   "<code>matplotlib</code> draws charts. We just borrow them.")),
code(
   "# Import the toolboxes we need. Running this cell produces no visible output -\n"
   "# that is normal. It just makes the tools available below.\n"
   "import numpy as np\n"
   "import pandas as pd\n"
   "import matplotlib.pyplot as plt\n"
   "\n"
   "from sklearn.model_selection import train_test_split\n"
   "from sklearn.tree import DecisionTreeClassifier, export_text\n"
   "from sklearn.metrics import accuracy_score\n"
   "\n"
   "print('Tools loaded. We are ready.')"),
md(did("We loaded our toolboxes. Nothing dramatic happened on screen, and that is expected &mdash; "
       "this cell only prepares the tools we use further down.")),

md(section("Get the data", 2)),
md(vocab("Dataset",
   "A <b>dataset</b> is just a <b>table</b>. Rows are the things we recorded (here, machines). "
   "Columns are the things we measured about each one. Nothing more exotic than a spreadsheet.")),
md(vocab("Feature",
   "Each input column &mdash; <code>hours_used</code>, <code>temperature</code>, <code>vibration</code> &mdash; is called a "
   "<b>feature</b>. Features are the clues the computer gets to look at. One row of features describes one machine.")),
code(
   "# We create 300 past machine records. In real life this table would come from\n"
   "# your maintenance logs; here we generate it so everyone has identical data.\n"
   "rng = np.random.default_rng(42)   # fixed seed => everyone sees the same numbers\n"
   "n = 300\n"
   "\n"
   "hours_used  = rng.integers(200, 6000, n)                 # running hours\n"
   "temperature = np.round(rng.normal(72, 10, n), 1)          # running temp (deg C)\n"
   "vibration   = np.round(np.clip(rng.normal(3.0, 1.0, n), 0.3, None), 2)  # mm/s\n"
   "\n"
   "# The hidden truth we are pretending not to know: hotter + shakier + older\n"
   "# machines are more likely to need a service (plus a little real-world noise).\n"
   "risk = (0.00022*hours_used + 0.07*(temperature-72) + 0.85*(vibration-3.0)\n"
   "        + rng.normal(0, 0.45, n))\n"
   "needs_service = (risk > 0.55).astype(int)   # 1 = needed service, 0 = did not\n"
   "\n"
   "df = pd.DataFrame({\n"
   "    'hours_used':    hours_used,\n"
   "    'temperature':   temperature,\n"
   "    'vibration':     vibration,\n"
   "    'needs_service': needs_service,\n"
   "})\n"
   "\n"
   "df.head(8)   # show the first 8 rows"),
md(did("There is our <b>dataset</b>: 300 machines, one per row. The first three columns are the "
       "<b>features</b> (the clues). The last column, <code>needs_service</code>, is the outcome we eventually want to predict.")),

md(section("Look before you model", 3)),
md("Good practice: always *look* at the data before doing anything clever with it. "
   "How big is it? Is it balanced? What are typical values?"),
code(
   "print('Rows and columns:', df.shape)        # (machines, columns)\n"
   "print()\n"
   "print('How many needed service vs not:')\n"
   "print(df['needs_service'].value_counts())\n"
   "print()\n"
   "print('Typical values per column:')\n"
   "df.describe().round(1)"),
md(vocab("Label",
   "The outcome we want to predict &mdash; <code>needs_service</code>, which is 1 or 0 &mdash; is called the <b>label</b>. "
   "It is the \"answer\" for each past machine. Because we already know the answer for these old records, the computer can learn from them.")),
md(vocab("Label column",
   "The single column that holds those answers is the <b>label column</b>. "
   "Separating the <b>label column</b> from the <b>feature columns</b> is the first real step of almost every predictive-AI project. "
   "Keep this distinction &mdash; it comes back in every notebook today.")),
md(did("About half the machines needed service and half did not, so the data is nicely <b>balanced</b> &mdash; "
       "the computer will see plenty of both kinds. We also now know the typical hours, temperature and vibration.")),

md(section("See the pattern with our own eyes", 4)),
md("Before any maths, let us simply *draw* the data. We will plot temperature against vibration, "
   "and colour each machine by whether it needed service. If our common-sense story is right, "
   "the two colours should fall in different regions."),
code(
   "plt.figure(figsize=(8, 5.5))\n"
   "ok   = df[df['needs_service'] == 0]\n"
   "fail = df[df['needs_service'] == 1]\n"
   "\n"
   "plt.scatter(ok['temperature'],   ok['vibration'],   c='#2e7d32', label='Did NOT need service', alpha=0.7, edgecolors='white')\n"
   "plt.scatter(fail['temperature'], fail['vibration'], c='#9c2b2b', label='Needed service',        alpha=0.7, edgecolors='white')\n"
   "\n"
   "plt.xlabel('Temperature (deg C)')\n"
   "plt.ylabel('Vibration (mm/s)')\n"
   "plt.title('Each dot is one machine')\n"
   "plt.legend()\n"
   "plt.grid(alpha=0.3)\n"
   "plt.show()"),
md(did("Look at the colours: machines that needed service (red) cluster toward the <b>top-right</b> &mdash; "
       "hotter and shakier. Machines that were fine (green) sit toward the bottom-left. "
       "<b>That separation IS the pattern.</b> The whole job of a predictive model is to find a boundary between the colours, "
       "so that when a new grey dot arrives, it can guess the colour.")),

md(section("Split the features from the label (X and y)", 5)),
md(vocab("X and y",
   "By long-standing convention we call the table of <b>features</b> <code>X</code> (the clues) and the <b>label</b> column "
   "<code>y</code> (the answers). The model's job is to learn the link <b>X &rarr; y</b>.")),
code(
   "X = df[['hours_used', 'temperature', 'vibration']]   # the clues  (features)\n"
   "y = df['needs_service']                               # the answers (label)\n"
   "\n"
   "print('X is the feature table:', X.shape, '-> 300 machines, 3 clues each')\n"
   "print('y is the label column: ', y.shape, '-> 300 answers')"),
md(did("We split the one table into two parts: <code>X</code> holds the three clue columns, "
       "<code>y</code> holds the single answer column. Everything from here on works with these two.")),

md(section("Hold back a test set", 6)),
md(vocab("Training set and test set",
   "We split our 300 machines into two groups. The <b>training set</b> is what the model learns from. "
   "The <b>test set</b> is hidden away and used only at the end, to check the model on machines it has never seen.")),
md(note("Why hide some data? Think of a student. If you let them study the exact exam paper beforehand, "
        "a top score proves nothing. The honest test uses <b>questions they have not seen</b>. "
        "Same here: we judge the model only on the held-back test set.")),
code(
   "X_train, X_test, y_train, y_test = train_test_split(\n"
   "    X, y,\n"
   "    test_size=0.25,    # keep 25% hidden for the final test\n"
   "    random_state=0,    # fixed split so everyone gets the same result\n"
   ")\n"
   "\n"
   "print('Learn from   :', X_train.shape[0], 'machines  (training set)')\n"
   "print('Tested on    :', X_test.shape[0],  'machines  (test set, kept hidden)')"),
md(did("225 machines go into the training set for the model to learn from, and 75 are locked away "
       "as the test set. The model will not see those 75 until the very end.")),

md(section("Train the model", 7)),
md(vocab("Model",
   "A <b>model</b> is the pattern-finder. Before training it knows nothing. We will use a "
   "<b>decision tree</b> &mdash; it learns a set of yes/no questions (\"is vibration above 3?\") that sort machines into "
   "\"needs service\" or \"fine\". It mirrors how a technician actually reasons.")),
md(vocab("Training (fitting)",
   "<b>Training</b> &mdash; the method is literally called <code>.fit()</code> &mdash; is the moment the model studies the training "
   "machines and discovers the pattern. This single line is where the \"learning\" in machine learning happens.")),
code(
   "model = DecisionTreeClassifier(max_depth=3, random_state=0)\n"
   "\n"
   "model.fit(X_train, y_train)   # <-- the model studies the training machines\n"
   "\n"
   "print('Training done. The model has found its pattern.')"),
md(did("That one <code>.fit()</code> call is the entire act of learning. The model has now built its "
       "internal set of questions. Let us actually read them out.")),
code(
   "# A decision tree is rare in that we can print the exact rules it invented.\n"
   "print(export_text(model, feature_names=['hours_used', 'temperature', 'vibration']))"),
md(did("The computer <b>wrote its own if-then rules</b> from the data &mdash; nobody programmed them by hand. "
       "Read the top split: it first checks <code>vibration</code>, then <code>temperature</code>, then "
       "<code>hours_used</code> &mdash; exactly the common-sense clues we expected, discovered automatically.")),

md(section("Predict, and measure how good it is", 8)),
md(vocab("Prediction",
   "A <b>prediction</b> is the model's answer for a case: 1 (will need service) or 0 (fine). "
   "We ask it to predict the 75 hidden test machines, where we secretly know the real answers.")),
md(vocab("Accuracy",
   "<b>Accuracy</b> is the simplest score: out of the test machines, what fraction did the model get right? "
   "0.90 means 9 out of 10 correct. Higher is better, but 100% on real data is usually a red flag, not a triumph.")),
code(
   "predictions = model.predict(X_test)        # the model's guesses for the hidden machines\n"
   "\n"
   "score = accuracy_score(y_test, predictions)\n"
   "print('Accuracy on machines it had never seen:', round(score, 3))\n"
   "print('In plain words: it got about', round(score*100), 'out of every 100 right.')"),
md(did("Around <b>0.87</b> &mdash; roughly 87 out of 100 correct, on machines the model never trained on. "
       "Not perfect, and that is healthy: real equipment has surprises, and a model claiming 100% is usually cheating somehow. "
       "This is an honest, useful result.")),

md(section("Use it on a brand-new machine", 9)),
md("This is the whole point. A new machine arrives. We have its three numbers but no idea whether it will need service. "
   "We hand the numbers to the trained model and get an instant call."),
code(
   "# A clearly worrying machine: old, hot, shaky.\n"
   "new_machine = pd.DataFrame([{'hours_used': 5200, 'temperature': 86, 'vibration': 4.6}])\n"
   "\n"
   "guess = model.predict(new_machine)[0]\n"
   "confidence = model.predict_proba(new_machine)[0][1]   # model's probability of 'needs service'\n"
   "\n"
   "print('New machine:', new_machine.to_dict('records')[0])\n"
   "print('Prediction :', 'NEEDS SERVICE' if guess == 1 else 'looks fine')\n"
   "print('Confidence in needs-service:', round(confidence*100), '%')"),
code(
   "# A clearly healthy machine: young, cool, smooth.\n"
   "healthy = pd.DataFrame([{'hours_used': 900, 'temperature': 65, 'vibration': 2.1}])\n"
   "\n"
   "guess = model.predict(healthy)[0]\n"
   "confidence = model.predict_proba(healthy)[0][1]\n"
   "\n"
   "print('New machine:', healthy.to_dict('records')[0])\n"
   "print('Prediction :', 'NEEDS SERVICE' if guess == 1 else 'looks fine')\n"
   "print('Confidence in needs-service:', round(confidence*100), '%')"),
md(did("The model flags the old/hot/shaky machine and clears the young/cool/smooth one &mdash; "
       "matching exactly what any experienced person would say. Except the computer can now do this for "
       "ten thousand machines in a second, consistently, day and night.")),

md(turn(
   "Make it your own. Edit the numbers in the cells above and press <b>Shift + Enter</b> to re-run:<br>"
   "1. In the new-machine cell, set <code>vibration</code> to <code>3.0</code> and <code>temperature</code> to <code>74</code>. "
   "A borderline machine &mdash; watch the confidence land near 50%.<br>"
   "2. In Step 6, change <code>test_size=0.25</code> to <code>0.5</code> (hide half the data). Re-run from there. Does accuracy change?<br>"
   "3. In Step 7, change <code>max_depth=3</code> to <code>1</code> (allow only one question). Re-read the rules and the accuracy.")),

md(recap("What we learned in Notebook 0", [
   "A <b>dataset</b> is just a table: rows are cases, columns are measurements.",
   "<b>Features</b> are the input clues; the <b>label</b> is the answer; the <b>label column</b> holds those answers.",
   "We split into a <b>training set</b> (to learn from) and a hidden <b>test set</b> (for an honest score).",
   "<b>Training</b> = <code>.fit()</code>: the model finds the pattern by itself.",
   "<b>Prediction</b> = <code>.predict()</code>, and <b>accuracy</b> tells us how often it is right.",
   "This same five-step rhythm &mdash; data &rarr; split &rarr; train &rarr; predict &rarr; measure &mdash; powers every example today.",
])),
md(nextup(
   "<b>Notebook 1 &mdash; Classification.</b> We just did classification without naming it. "
   "Next we slow down on the single most common predictive task &mdash; sorting cases into categories &mdash; "
   "and learn to read <i>where</i> and <i>why</i> a model makes mistakes, not just its overall score.")),
]

build(cells, "/Users/flam/Desktop/HAL_AI/notebooks/00_intro_predictive_ai.ipynb",
      title="Predictive AI 00 - What is Predictive AI")
