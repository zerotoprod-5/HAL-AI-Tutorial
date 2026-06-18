import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbbuild import *

LEGEND = """
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:14px;color:#333;line-height:1.7;">
As you scroll, you will meet four kinds of coloured boxes:
<br><b style="color:#0b6e7a;">Teal — Vocabulary:</b> a new word, in plain English.
<br><b style="color:#2e7d32;">Green — What just happened:</b> what the cell above actually did.
<br><b style="color:#b26a00;">Amber — Your turn:</b> a safe thing to change, then re-run.
<br><b style="color:#5b2a86;">Purple — Recap / Coming up:</b> the big picture.
</div>
"""

cells = [
md(banner("Text Analytics &middot; Session 1 of 4", "Text Analytics: Teaching the Computer to Read Reports",
   "Free-text maintenance and defect logs &mdash; sorted automatically, no human reading required")),

md("## How to use this notebook\n\n"
   "This is a **hands-on** notebook. You do not need to write any code. "
   "You only **run** the cells, top to bottom, and read what comes out.\n\n"
   "- To run a cell: click it, then press **Shift + Enter** (or the &#9654; play button on its left).\n"
   "- Run them **in order**. Each cell builds on the one above it.\n"
   "- If something looks broken, use the menu: **Runtime &rarr; Restart and run all**, then start again.\n\n"
   + LEGEND),

md(bigidea(
   "So far every example used neat <b>columns of numbers</b> &mdash; hours, temperature, vibration. "
   "But a huge amount of real information at any workshop is not numbers at all. It is <b>written text</b>: "
   "maintenance logs, defect reports, operator complaints, handwritten-then-typed notes.<br><br>"
   "<b>Predictive AI can read that text and sort it automatically.</b> The trick is one new step: "
   "first we turn the <i>words</i> into <i>numbers</i>. Once the words are numbers, it becomes the <b>exact same "
   "classification workflow you already know</b> from the earlier notebooks &mdash; split, train, predict, measure. "
   "Only the very first step is new. Everything after it will feel familiar.")),

md(story(
   "<b>Our running example: a busy maintenance desk.</b><br>"
   "Every day a workshop receives dozens of short free-text reports &mdash; one or two lines each, typed in a hurry:<br>"
   "<i>\"Oil leaking near the gearbox\"</i> &nbsp;·&nbsp; <i>\"Display flickers on startup\"</i> &nbsp;·&nbsp; "
   "<i>\"Loud grinding noise from the bearing\"</i><br><br>"
   "Right now a person reads each one and forwards it to the right team. That is slow, and at 3 a.m. it does not "
   "happen at all. We want the computer to <b>auto-categorize</b> every report &mdash; Electrical, Mechanical, or "
   "Hydraulic &mdash; so it lands in the correct queue instantly. No domain expertise required: the words themselves "
   "carry the clue.")),

md(section("Set up our tools", 1)),
md(vocab("Library",
   "A quick reminder from earlier: a <b>library</b> is a ready-made toolbox of code. "
   "<code>pandas</code> handles tables, <code>scikit-learn</code> is the machine-learning toolbox. "
   "The one new face today lives inside scikit-learn: <code>TfidfVectorizer</code>, the tool that turns words into numbers.")),
code(
   "# Import the toolboxes we need. Running this cell produces no visible output -\n"
   "# that is normal. It just makes the tools available below.\n"
   "import numpy as np\n"
   "import pandas as pd\n"
   "import matplotlib.pyplot as plt\n"
   "\n"
   "from sklearn.feature_extraction.text import TfidfVectorizer   # turns words into numbers\n"
   "from sklearn.model_selection import train_test_split\n"
   "from sklearn.linear_model import LogisticRegression\n"
   "from sklearn.metrics import accuracy_score\n"
   "\n"
   "print('Tools loaded. We are ready.')"),
md(did("We loaded our toolboxes. Nothing dramatic happened on screen, and that is expected &mdash; "
       "this cell only prepares the tools we use further down. Notice <code>TfidfVectorizer</code>: that is the "
       "one genuinely new tool in this notebook.")),

md(section("Get the data — written reports", 2)),
md(vocab("Text analytics  /  NLP",
   "<b>Text analytics</b> &mdash; also called <b>NLP</b>, Natural Language Processing &mdash; simply means getting a "
   "computer to make sense of human-written words. Reading a report and deciding which team it belongs to is a classic "
   "text-analytics task. It is the same predictive idea as before; the input just happens to be sentences instead of numbers.")),
code(
   "# Our dataset is written by hand here so everyone has identical data.\n"
   "# In real life these would be pulled straight from your maintenance log system.\n"
   "# Each report is one short sentence; each has a category (the team it belongs to).\n"
   "\n"
   "reports = [\n"
   "    # ---- Electrical ----\n"
   "    ('Display flickers on startup',                       'Electrical'),\n"
   "    ('Control panel lights are dim and unstable',         'Electrical'),\n"
   "    ('Wiring near the switch is burnt and smells hot',    'Electrical'),\n"
   "    ('Circuit breaker keeps tripping under load',         'Electrical'),\n"
   "    ('Sensor gives no signal to the controller',          'Electrical'),\n"
   "    ('Battery voltage drops and the unit shuts off',      'Electrical'),\n"
   "    ('Fuse blew again on the lighting circuit',           'Electrical'),\n"
   "    ('Motor controller throws an electrical fault code',  'Electrical'),\n"
   "    ('Loose terminal connection causing a short',         'Electrical'),\n"
   "    ('Touchscreen is unresponsive and the display blanks','Electrical'),\n"
   "    ('Indicator lamp does not light when powered on',     'Electrical'),\n"
   "    ('Cable insulation is frayed near the junction box',  'Electrical'),\n"
   "    ('Power supply is overheating and the fan stopped',   'Electrical'),\n"
   "    ('Relay clicks but no voltage reaches the motor',     'Electrical'),\n"
   "    ('Grounding wire disconnected from the panel',        'Electrical'),\n"
   "    ('Charger does not deliver current to the battery',   'Electrical'),\n"
   "\n"
   "    # ---- Mechanical ----\n"
   "    ('Loud grinding noise from the bearing',              'Mechanical'),\n"
   "    ('Gearbox makes a knocking sound under load',         'Mechanical'),\n"
   "    ('Belt is worn and slipping on the pulley',           'Mechanical'),\n"
   "    ('Bearing is overheating and seized',                 'Mechanical'),\n"
   "    ('Excessive vibration from the rotating shaft',       'Mechanical'),\n"
   "    ('Coupling is loose and the gears rattle',            'Mechanical'),\n"
   "    ('Cracked gear tooth found during inspection',        'Mechanical'),\n"
   "    ('Fan blade is bent and scrapes the housing',         'Mechanical'),\n"
   "    ('Chain is stretched and jumps off the sprocket',     'Mechanical'),\n"
   "    ('Shaft alignment is off and the bearing wears fast', 'Mechanical'),\n"
   "    ('Worn brake pads make a squealing noise',            'Mechanical'),\n"
   "    ('Broken mounting bolt lets the motor shift',         'Mechanical'),\n"
   "    ('Pulley wobbles and the belt keeps coming off',      'Mechanical'),\n"
   "    ('Grinding metal sound when the gear engages',        'Mechanical'),\n"
   "    ('Rotor is unbalanced causing heavy shaking',         'Mechanical'),\n"
   "    ('Loose flywheel rattles at high speed',              'Mechanical'),\n"
   "\n"
   "    # ---- Hydraulic ----\n"
   "    ('Oil leaking near the gearbox',                      'Hydraulic'),\n"
   "    ('Hydraulic pressure drops during operation',         'Hydraulic'),\n"
   "    ('Fluid leak under the cylinder seal',                'Hydraulic'),\n"
   "    ('Pump is not building enough pressure',              'Hydraulic'),\n"
   "    ('Hose is cracked and dripping hydraulic oil',        'Hydraulic'),\n"
   "    ('Cylinder moves slowly due to low fluid',            'Hydraulic'),\n"
   "    ('Valve is stuck and pressure will not release',      'Hydraulic'),\n"
   "    ('Oil level is low and the pump is noisy',            'Hydraulic'),\n"
   "    ('Seal failure causes fluid to spray out',            'Hydraulic'),\n"
   "    ('Hydraulic ram drifts down on its own',              'Hydraulic'),\n"
   "    ('Contaminated oil clogs the hydraulic filter',       'Hydraulic'),\n"
   "    ('Pressure gauge reads zero at the pump outlet',      'Hydraulic'),\n"
   "    ('Leaking fitting sprays oil near the actuator',      'Hydraulic'),\n"
   "    ('Reservoir is low and the system loses pressure',    'Hydraulic'),\n"
   "    ('Hydraulic fluid is foaming and overheating',        'Hydraulic'),\n"
   "    ('Cylinder seal weeps oil at full extension',         'Hydraulic'),\n"
   "]\n"
   "\n"
   "df = pd.DataFrame(reports, columns=['report', 'category'])\n"
   "print('Total reports:', len(df))\n"
   "df.head(6)"),
md(did("There is our <b>dataset</b>: 48 short written reports, one per row. The <code>report</code> column is the "
       "raw text (our clue), and <code>category</code> is the answer we want to predict &mdash; the same idea as the "
       "<b>label</b> in earlier notebooks, just a word instead of a 0 or 1.")),

md(section("Look at a few from each category", 3)),
md("Good practice, exactly as before: look at the data first. Let us print a couple of reports from each "
   "category so we can see, with our own eyes, that the wording really does differ by team."),
code(
   "# How many reports per category? We want them roughly balanced.\n"
   "print('Reports per category:')\n"
   "print(df['category'].value_counts())\n"
   "print()\n"
   "\n"
   "# Print three example reports from each category.\n"
   "for cat in ['Electrical', 'Mechanical', 'Hydraulic']:\n"
   "    print(f'--- {cat} ---')\n"
   "    for text in df[df['category'] == cat]['report'].head(3):\n"
   "        print('   ', text)\n"
   "    print()"),
md(did("Sixteen reports in each of the three categories &mdash; nicely <b>balanced</b>, so the computer will see plenty "
       "of every kind. And the vocabulary clearly splits: Electrical reports talk about <i>voltage, circuit, wiring</i>; "
       "Mechanical ones about <i>bearing, gear, belt</i>; Hydraulic ones about <i>oil, pressure, fluid</i>. Those words "
       "are exactly the clues the computer will latch onto.")),

md(section("The key idea — turning words into numbers", 4)),
md(bigidea(
   "Here is the one genuinely new concept in this whole notebook, so we will slow right down.<br><br>"
   "<b>A computer cannot read words. It can only do arithmetic on numbers.</b> So before any machine learning can "
   "happen, every report has to be converted into a row of numbers. The simplest honest way to do that is to "
   "<b>count which words appear</b> in each report. That is the entire trick.")),
md(vocab("Bag of words",
   "Imagine emptying each report into a bag and just tallying the words inside, ignoring their order. "
   "<i>\"Oil leaking near the gearbox\"</i> becomes the tally {oil:1, leaking:1, gearbox:1, ...}. "
   "This is called the <b>bag-of-words</b> idea. Word order is thrown away &mdash; surprisingly, the words alone are "
   "usually enough to tell which team a report belongs to.")),
md(vocab("Vectorizing",
   "<b>Vectorizing</b> is the act of turning each report into that row of word-counts &mdash; a <b>vector</b>, which is "
   "just a fancy word for a list of numbers. Every distinct word in the whole collection becomes one column; "
   "each report becomes one row of numbers. After this step, our text is a numeric table, exactly like the spreadsheets "
   "from earlier notebooks.")),
md(vocab("Stop words",
   "Words like <b>the, and, is, on, a</b> appear in almost every sentence and carry almost no clue about the category. "
   "These are called <b>stop words</b>, and we simply tell the tool to ignore them &mdash; they would only add noise.")),
code(
   "# Let us SEE vectorizing happen on just two example sentences first,\n"
   "# so the abstract idea becomes concrete.\n"
   "example = [\n"
   "    'Oil leaking near the gearbox',\n"
   "    'Hydraulic pressure drops during operation',\n"
   "]\n"
   "\n"
   "demo_vec = TfidfVectorizer(stop_words='english')   # 'english' = ignore common stop words\n"
   "demo_matrix = demo_vec.fit_transform(example)\n"
   "\n"
   "# Show which words became columns (the 'vocabulary' the tool found).\n"
   "print('Words that became columns (stop words like \"the\" were dropped):')\n"
   "print(list(demo_vec.get_feature_names_out()))\n"
   "print()\n"
   "\n"
   "# Show the two sentences as rows of numbers.\n"
   "demo_table = pd.DataFrame(\n"
   "    demo_matrix.toarray().round(2),\n"
   "    columns=demo_vec.get_feature_names_out(),\n"
   "    index=['sentence 1', 'sentence 2'],\n"
   ")\n"
   "demo_table"),
md(did("Look closely at the table. Each <b>column is a word</b>, each <b>row is one sentence</b>, and the numbers say "
       "whether that word appeared (a zero means the word was absent). The words <i>the, near, during</i> are gone &mdash; "
       "those were <b>stop words</b>. <b>This is the whole magic:</b> two English sentences are now two rows of numbers "
       "that a computer can do arithmetic on.")),
md(vocab("TF-IDF",
   "The tool is called <code>Tfidf</code>Vectorizer. In one plain line: instead of a raw count, it gives a word more "
   "weight when that word is <b>common in THIS report but rare across all reports</b>. So a distinctive word like "
   "<i>hydraulic</i> counts for more than a word like <i>noise</i> that shows up everywhere. No formula to memorise &mdash; "
   "just \"rare, distinctive words matter more.\" That is why some numbers above are not whole counts.")),

md(section("Vectorize all the reports", 5)),
md("Now we run the same vectorizing on the full set of 48 reports. The result is a numeric table the model can learn from."),
code(
   "# Turn the report text into our clue table X, and the categories into the answers y.\n"
   "vectorizer = TfidfVectorizer(stop_words='english')\n"
   "\n"
   "X = vectorizer.fit_transform(df['report'])   # the reports, now as rows of numbers\n"
   "y = df['category']                            # the answers (the team for each report)\n"
   "\n"
   "print('X is now a numeric table:', X.shape[0], 'reports x', X.shape[1], 'word-columns')\n"
   "print('Total distinct words the tool found:', len(vectorizer.get_feature_names_out()))\n"
   "print()\n"
   "print('A sample of the word-columns:')\n"
   "print(list(vectorizer.get_feature_names_out())[:25])"),
md(did("Every report is now a row of numbers across roughly 150 word-columns. <code>X</code> is our feature table "
       "and <code>y</code> is our label &mdash; the same <b>X &rarr; y</b> setup from every earlier notebook. "
       "From here on, nothing is new: it is ordinary classification.")),

md(section("Split, then train the model", 6)),
md(vocab("Train / test split  (reminder)",
   "Same honest-exam idea as before: we learn from most of the reports (the <b>training set</b>) and hide a few "
   "(the <b>test set</b>) to check the model on reports it has never read. We keep one report from each category in the "
   "test set so the score means something.")),
md(note("Our dataset is deliberately tiny &mdash; 48 reports &mdash; so the test set is small and the accuracy below is "
        "a <b>rough indicator</b>, not a precise grade. With real maintenance logs you would have thousands of reports "
        "and a far steadier score. The point here is to see the workflow, not to chase a number.")),
code(
   "# Split into a training set (to learn from) and a small hidden test set.\n"
   "# stratify=y keeps each category represented in both halves.\n"
   "X_train, X_test, y_train, y_test = train_test_split(\n"
   "    X, y,\n"
   "    test_size=0.25,      # hide a quarter for the final test\n"
   "    random_state=0,      # fixed split so everyone gets the same result\n"
   "    stratify=y,          # keep all three categories in both halves\n"
   ")\n"
   "\n"
   "print('Learn from :', X_train.shape[0], 'reports  (training set)')\n"
   "print('Tested on  :', X_test.shape[0],  'reports  (test set, kept hidden)')\n"
   "\n"
   "# Train the classifier - the same kind of model idea as before.\n"
   "model = LogisticRegression(max_iter=1000)\n"
   "model.fit(X_train, y_train)   # <-- the model studies the training reports\n"
   "print()\n"
   "print('Training done. The model has learned which words point to which team.')"),
md(did("That one <code>.fit()</code> call is the entire act of learning, exactly as in Notebook 0 &mdash; only now the "
       "clues are words instead of hours and temperature. The model has worked out which words lean toward each team.")),

md(section("Measure how good it is", 7)),
md(vocab("Accuracy  (reminder)",
   "Out of the hidden test reports, what fraction did the model file under the correct team? "
   "1.0 means every one correct. On a dataset this small, treat it as a rough sanity check, not a final grade.")),
code(
   "predictions = model.predict(X_test)        # the model's guesses for the hidden reports\n"
   "\n"
   "score = accuracy_score(y_test, predictions)\n"
   "print('Accuracy on reports it had never read:', round(score, 3))\n"
   "print('In plain words: it got about', round(score*100), 'out of every 100 right.')\n"
   "print()\n"
   "\n"
   "# Show the actual vs predicted team for each hidden report, side by side.\n"
   "check = pd.DataFrame({\n"
   "    'report':    df.loc[y_test.index, 'report'].values,\n"
   "    'actual':    y_test.values,\n"
   "    'predicted': predictions,\n"
   "})\n"
   "check"),
md(did("The model files the hidden reports into the right team. On a 48-report toy set the score is a rough indicator, "
       "but the side-by-side table shows it is genuinely matching reports to teams from the words alone &mdash; nobody "
       "wrote a single rule by hand.")),

md(section("Look inside — the top words per team", 8)),
md("A logistic-regression model keeps a weight for every word, telling us how strongly that word pushes a report toward "
   "each team. Because the words are human-readable, we can simply <b>print the top clue-words the model learned</b> for "
   "each category and check they make sense."),
code(
   "# For each category, pull the words the model weights most heavily toward it.\n"
   "feature_names = np.array(vectorizer.get_feature_names_out())\n"
   "\n"
   "print('Top clue-words the model associates with each team:')\n"
   "print()\n"
   "for i, cat in enumerate(model.classes_):\n"
   "    weights = model.coef_[i]\n"
   "    top = feature_names[np.argsort(weights)[-7:]][::-1]   # 7 strongest words\n"
   "    print(f'{cat:12s}:', ', '.join(top))"),
md(did("Read those lists: the model decided that words like <i>oil, pressure, fluid, leak</i> signal <b>Hydraulic</b>; "
       "<i>bearing, gear, belt, grinding</i> signal <b>Mechanical</b>; <i>voltage, circuit, wiring, display</i> signal "
       "<b>Electrical</b>. That matches exactly what any experienced person would say &mdash; and the computer worked it "
       "out on its own, purely from the example reports.")),
code(
   "# The same idea as a bar chart, for one team (Hydraulic).\n"
   "i = list(model.classes_).index('Hydraulic')\n"
   "weights = model.coef_[i]\n"
   "order = np.argsort(weights)[-8:]          # 8 strongest Hydraulic words\n"
   "words = feature_names[order]\n"
   "vals = weights[order]\n"
   "\n"
   "plt.figure(figsize=(8, 5.5))\n"
   "plt.barh(words, vals, color='#0b6e7a')\n"
   "plt.xlabel('How strongly the word points to \"Hydraulic\"')\n"
   "plt.title('Words the model learned to associate with Hydraulic reports')\n"
   "plt.grid(alpha=0.3, axis='x')\n"
   "plt.tight_layout()\n"
   "plt.show()"),
md(did("The longest bars are the words most tied to Hydraulic &mdash; <i>oil, pressure, fluid</i> and friends. "
       "This is what people mean when they say a model is <b>interpretable</b>: we can open it up and the reasoning is "
       "plain English, not a black box.")),

md(section("Use it on brand-new reports", 9)),
md("This is the whole point. Fresh reports arrive that the model has never seen. We hand it the raw text &mdash; "
   "the model vectorizes it the same way and instantly names the team, with a confidence."),
code(
   "# Four brand-new reports, typed fresh. Note: we feed RAW TEXT;\n"
   "# the vectorizer turns it into numbers automatically, the same way as before.\n"
   "new_reports = [\n"
   "    'Grinding noise from the bearing and the gear sounds worn',  # clearly Mechanical\n"
   "    'Hydraulic oil leaking from the cylinder seal, pressure low',# clearly Hydraulic\n"
   "    'Control panel display and wiring circuit fault on startup', # clearly Electrical\n"
   "    'Pump is overheating and the fan stopped',                   # ambiguous on purpose\n"
   "]\n"
   "\n"
   "new_X = vectorizer.transform(new_reports)     # SAME vectorizer, no re-fitting\n"
   "guesses = model.predict(new_X)\n"
   "probs = model.predict_proba(new_X)\n"
   "\n"
   "for text, guess, p in zip(new_reports, guesses, probs):\n"
   "    confidence = round(max(p) * 100)\n"
   "    print(f'Report : {text}')\n"
   "    print(f'  -> Team: {guess}   (confidence {confidence}%)')\n"
   "    print()"),
md(did("Three reports are sorted cleanly into the obvious team with high confidence. The fourth &mdash; "
       "<i>\"Pump is overheating and the fan stopped\"</i> &mdash; is genuinely ambiguous (a pump sounds Hydraulic, but "
       "<i>fan</i> and <i>overheating</i> pull toward Electrical/Mechanical), so its confidence is lower. That lower "
       "number is the model honestly telling us \"this one is a borderline call\" &mdash; useful information for a "
       "human to double-check.")),

md(turn(
   "Make it your own. Edit the cell just above and press <b>Shift + Enter</b> to re-run:<br>"
   "1. Change the first new report to your own sentence, e.g. <code>'Circuit breaker keeps tripping'</code>. "
   "Watch the predicted team change.<br>"
   "2. Write a deliberately mixed report like <code>'Oil leak is causing an electrical short'</code> and see which "
   "team wins &mdash; and how the confidence drops because the clues disagree.<br>"
   "3. Harder: in Step 2, add a couple of your own reports to a category, then use "
   "<b>Runtime &rarr; Restart and run all</b> to retrain from scratch and watch the top-words list shift.")),

md(recap("What we learned in Notebook 4", [
   "Not all data is numbers &mdash; <b>written reports are data too</b>, and predictive AI can sort them.",
   "Computers cannot read words, so we first turn text into numbers by <b>counting words</b> (<b>bag of words</b> / <b>vectorizing</b>).",
   "<b>Stop words</b> like \"the\" are ignored; <b>TF-IDF</b> just means rare, distinctive words count for more.",
   "Once text is numbers, it is the <b>exact same classification workflow</b>: split &rarr; train &rarr; predict &rarr; measure.",
   "The model is <b>interpretable</b> &mdash; its top words per team read like plain English and match human intuition.",
   "New reports get sorted instantly, with a <b>confidence</b> that flags the borderline ones for a human.",
])),
md(nextup(
   "<b>Notebook 5 &mdash; Speech Analytics.</b> Reports do not always arrive as typed text. Next we will "
   "<i>speak</i> a maintenance report out loud, have the computer <b>transcribe</b> our voice into text, and then feed "
   "that text through exactly this kind of analysis &mdash; closing the loop from spoken words to an automatic decision.")),
]

build(cells, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notebooks", "01_text_analytics.ipynb"),
      title="Predictive AI - Session 1 - Text I")
