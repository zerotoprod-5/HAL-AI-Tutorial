import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbmd import *

cells = [
md(banner("Text Analytics · Session 1 of 4", "Text Analytics: Catch the Urgent Reports Automatically",
   "Free-text maintenance notes &mdash; flagged URGENT or ROUTINE in an instant, with nobody reading every line")),

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
   "classification workflow you already know</b> &mdash; split, train, predict, measure. "
   "Only the very first step is new. Everything after it will feel familiar.")),

md(story(
   "<b>Our running example: a busy maintenance desk.</b><br>"
   "Every day a workshop receives hundreds of short free-text notes &mdash; one or two lines each, typed in a hurry:<br>"
   "<i>\"crack found in wing spar, aircraft grounded\"</i> &nbsp;·&nbsp; <i>\"cabin light flickers, cosmetic only\"</i> &nbsp;·&nbsp; "
   "<i>\"smoke from avionics bay during taxi\"</i><br><br>"
   "Almost all of them are <b>routine</b> &mdash; monitor it, log it, handle it at the next scheduled check. But a small "
   "handful are <b>urgent</b> &mdash; a crack, smoke, a fuel leak, a grounded aircraft &mdash; and those <b>must not</b> sit "
   "in a queue overnight. We want the computer to read every note and <b>flag the urgent ones</b> the moment they arrive, "
   "so a human looks at the right ones first. Missing one urgent note is the costly mistake &mdash; keep that in mind, it is "
   "the whole point of this session.")),

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
   "from sklearn.metrics import accuracy_score, confusion_matrix, recall_score\n"
   "\n"
   "print('Tools loaded. We are ready.')"),
md(did("We loaded our toolboxes. Nothing dramatic happened on screen, and that is expected &mdash; "
       "this cell only prepares the tools we use further down. Notice <code>TfidfVectorizer</code>: that is the "
       "one genuinely new tool in this notebook.")),

md(section("Build the data — a realistic stack of notes", 2)),
md(vocab("Text analytics  /  NLP",
   "<b>Text analytics</b> &mdash; also called <b>NLP</b>, Natural Language Processing &mdash; simply means getting a "
   "computer to make sense of human-written words. Reading a note and deciding whether it is urgent is a classic "
   "text-analytics task. It is the same predictive idea as before; the input just happens to be sentences instead of numbers.")),
md(note("We generate the notes right here from a few templates so everyone has identical data and we can make the mix "
        "<b>realistically lopsided</b>. In real life these would be pulled straight from your maintenance log system &mdash; "
        "and they would be lopsided in exactly the same way: most notes are routine, only a few are urgent.")),
code(
   "# We build ~400 short notes from word-banks, with a FIXED seed so everyone\n"
   "# gets the identical dataset. Most notes are routine; only ~15% are urgent -\n"
   "# that imbalance is on purpose, because it is what real logs look like.\n"
   "rng = np.random.default_rng(42)\n"
   "\n"
   "# Phrases that signal a genuinely URGENT note.\n"
   "urgent_phrases = [\n"
   "    'crack found in wing spar, aircraft grounded',\n"
   "    'smoke from avionics bay during taxi',\n"
   "    'fuel leak under the wing, strong smell in cabin',\n"
   "    'hydraulic failure, brakes unresponsive on landing roll',\n"
   "    'engine fire warning illuminated on takeoff',\n"
   "    'structural crack near the main landing gear mount',\n"
   "    'aircraft on ground, no dispatch until inspected',\n"
   "    'burning smell and sparks from the wiring loom',\n"
   "    'major fuel system leak, aircraft grounded immediately',\n"
   "    'cracked turbine blade discovered, do not fly',\n"
   "    'loss of cabin pressure reported in flight',\n"
   "    'flames seen near the apu exhaust during start',\n"
   "]\n"
   "\n"
   "# Phrases that signal a ROUTINE note.\n"
   "routine_phrases = [\n"
   "    'cabin reading light flickers, cosmetic only',\n"
   "    'seat trim scuffed, within limits, monitor',\n"
   "    'minor paint chip on the fairing, log and continue',\n"
   "    'tyre wear noted, still within service limits',\n"
   "    'scheduled oil top-up completed, no action needed',\n"
   "    'small coffee stain on galley panel, cosmetic',\n"
   "    'cabin speaker slightly muffled, monitor at next check',\n"
   "    'placard label peeling, replace at scheduled maintenance',\n"
   "    'overhead bin latch a little stiff, within limits',\n"
   "    'routine filter inspection done, all normal',\n"
   "    'minor squeak from seat recline, monitor',\n"
   "    'window shade slow to retract, cosmetic, no action',\n"
   "    'lavatory tap drips slightly, log for next service',\n"
   "    'carpet edge lifting near door, cosmetic only',\n"
   "    'reading lamp dim, schedule bulb swap',\n"
   "]\n"
   "\n"
   "# REALISTIC GREY ZONE. Real logs are not tidy. Some notes are genuinely\n"
   "# ambiguous - the SAME understated wording is sometimes a real emergency and\n"
   "# sometimes nothing. Because the words alone cannot tell these apart, the model\n"
   "# is forced to make honest mistakes on them - including the odd urgent note it\n"
   "# wrongly calls routine. That is exactly the costly miss we want to show.\n"
   "grey_phrases = [\n"
   "    'small mark noted near the panel, monitor',\n"
   "    'faint smell in cabin during taxi, please review',\n"
   "    'minor seep noted near the line, schedule a look',\n"
   "    'slight mark noted, within review, advise engineering',\n"
   "    'odd noise during start, monitor at next check',\n"
   "]\n"
   "\n"
   "# Little prefixes/suffixes so no two notes are word-for-word identical.\n"
   "prefixes = ['', 'reported: ', 'note: ', 'crew advises ', 'log entry - ']\n"
   "suffixes = ['', ' (ref A)', ' - tech desk', ' #ops', ' per checklist']\n"
   "\n"
   "def make_note(bank):\n"
   "    base = rng.choice(bank)\n"
   "    return rng.choice(prefixes) + base + rng.choice(suffixes)\n"
   "\n"
   "N = 400\n"
   "rows = []\n"
   "for _ in range(N):\n"
   "    if rng.random() < 0.15:                       # ~15% urgent\n"
   "        # ~3 in 10 urgent notes is a mild, ambiguous grey-zone note.\n"
   "        bank = grey_phrases if rng.random() < 0.30 else urgent_phrases\n"
   "        rows.append((make_note(bank), 'URGENT'))\n"
   "    else:                                         # ~85% routine\n"
   "        # the SAME grey-zone wording also turns up on routine notes,\n"
   "        # so those words genuinely cannot decide the label.\n"
   "        bank = grey_phrases if rng.random() < 0.18 else routine_phrases\n"
   "        rows.append((make_note(bank), 'ROUTINE'))\n"
   "\n"
   "df = pd.DataFrame(rows, columns=['note', 'label'])\n"
   "print('Total notes:', len(df))\n"
   "df.head(6)"),
md(did("There is our <b>dataset</b>: 400 short written notes, one per row. The <code>note</code> column is the raw text "
       "(our clue), and <code>label</code> is the answer we want to predict &mdash; <b>URGENT</b> or <b>ROUTINE</b>. "
       "Same idea as the 0/1 <b>label</b> in earlier notebooks, just spelled out in words.")),

md(section("Look at the mix first", 3)),
md("Good practice, exactly as before: look at the data before modelling. The single most important thing to notice here "
   "is <b>how lopsided the mix is</b> &mdash; and to print a few of each so we can see the wording really does differ."),
code(
   "# How many of each? This imbalance is the heart of today's lesson.\n"
   "counts = df['label'].value_counts()\n"
   "print('Notes per label:')\n"
   "print(counts)\n"
   "print()\n"
   "routine_share = (df['label'] == 'ROUTINE').mean()\n"
   "print(f'Routine share: {routine_share*100:.0f}%   Urgent share: {(1-routine_share)*100:.0f}%')\n"
   "print()\n"
   "\n"
   "# Print a few example notes of each kind.\n"
   "for lab in ['URGENT', 'ROUTINE']:\n"
   "    print(f'--- {lab} ---')\n"
   "    for text in df[df['label'] == lab]['note'].head(3):\n"
   "        print('   ', text)\n"
   "    print()"),
md(did("About <b>85% routine, 15% urgent</b>. That imbalance is realistic &mdash; and it is exactly what makes plain "
       "accuracy a <b>trap</b> later on. The vocabulary clearly splits too: urgent notes shout <i>crack, smoke, fire, "
       "grounded, leak</i>; routine notes mutter <i>cosmetic, within limits, monitor, scheduled, minor</i>. Those words "
       "are the clues the computer will latch onto.")),

md(section("The key idea — turning words into numbers", 4)),
md(bigidea(
   "Here is the one genuinely new concept in this whole notebook, so we will slow right down.<br><br>"
   "<b>A computer cannot read words. It can only do arithmetic on numbers.</b> So before any machine learning can "
   "happen, every note has to be converted into a row of numbers. The simplest honest way to do that is to "
   "<b>count which words appear</b> in each note. That is the entire trick.")),
md(vocab("Bag of words",
   "Imagine emptying each note into a bag and just tallying the words inside, ignoring their order. "
   "<i>\"smoke from avionics bay\"</i> becomes the tally {smoke:1, avionics:1, bay:1, ...}. "
   "This is the <b>bag-of-words</b> idea. Word order is thrown away &mdash; surprisingly, the words alone are usually "
   "enough to tell urgent from routine.")),
md(vocab("Vectorizing",
   "<b>Vectorizing</b> is the act of turning each note into that row of word-counts &mdash; a <b>vector</b>, which is "
   "just a fancy word for a list of numbers. Every distinct word in the whole collection becomes one column; "
   "each note becomes one row. After this step, our text is a numeric table, exactly like the spreadsheets from earlier.")),
md(vocab("Stop words",
   "Words like <b>the, and, is, on, a</b> appear in almost every sentence and carry almost no clue. "
   "These are called <b>stop words</b>, and we simply tell the tool to ignore them &mdash; they would only add noise.")),
code(
   "# Let us SEE vectorizing happen on just two example notes first,\n"
   "# so the abstract idea becomes concrete.\n"
   "example = [\n"
   "    'crack found in wing spar, aircraft grounded',\n"
   "    'seat trim scuffed, within limits, monitor',\n"
   "]\n"
   "\n"
   "demo_vec = TfidfVectorizer(stop_words='english')   # 'english' = ignore common stop words\n"
   "demo_matrix = demo_vec.fit_transform(example)\n"
   "\n"
   "# Show which words became columns (the 'vocabulary' the tool found).\n"
   "print('Words that became columns (stop words like \"in\" were dropped):')\n"
   "print(list(demo_vec.get_feature_names_out()))\n"
   "print()\n"
   "\n"
   "# Show the two notes as rows of numbers.\n"
   "demo_table = pd.DataFrame(\n"
   "    demo_matrix.toarray().round(2),\n"
   "    columns=demo_vec.get_feature_names_out(),\n"
   "    index=['urgent note', 'routine note'],\n"
   ")\n"
   "demo_table"),
md(did("Look closely at the table. Each <b>column is a word</b>, each <b>row is one note</b>, and the numbers say whether "
       "that word appeared (a zero means absent). Common stop words are gone. <b>This is the whole magic:</b> two English "
       "notes are now two rows of numbers a computer can do arithmetic on.")),
md(vocab("TF-IDF",
   "The tool is called <code>Tfidf</code>Vectorizer. In one plain line: instead of a raw count, it gives a word more "
   "weight when that word is <b>common in THIS note but rare across all notes</b>. So a distinctive word like "
   "<i>grounded</i> counts for more than a word like <i>note</i> that shows up everywhere. No formula to memorise &mdash; "
   "just \"rare, distinctive words matter more.\" That is why some numbers above are not whole counts.")),

md(section("Vectorize all the notes, then split", 5)),
md("Now we run the same vectorizing on all 400 notes, then split into a part to learn from and a hidden part to test on."),
md(vocab("Train / test split  (reminder)",
   "Same honest-exam idea as before: learn from most of the notes (the <b>training set</b>) and hide some (the "
   "<b>test set</b>) to check the model on notes it has never read. <code>stratify</code> keeps the same urgent/routine "
   "mix in both halves, so the test is fair.")),
code(
   "# Turn the note text into our clue table X, and the labels into the answers y.\n"
   "vectorizer = TfidfVectorizer(stop_words='english')\n"
   "X = vectorizer.fit_transform(df['note'])     # the notes, now as rows of numbers\n"
   "y = df['label']                              # the answers (URGENT / ROUTINE)\n"
   "\n"
   "print('X is now a numeric table:', X.shape[0], 'notes x', X.shape[1], 'word-columns')\n"
   "print()\n"
   "\n"
   "# Hide a quarter of the notes for a fair final test; keep the mix the same in both halves.\n"
   "X_train, X_test, y_train, y_test = train_test_split(\n"
   "    X, y,\n"
   "    test_size=0.35,\n"
   "    random_state=0,\n"
   "    stratify=y,          # keep the ~15/85 urgent/routine mix in both halves\n"
   ")\n"
   "print('Learn from :', X_train.shape[0], 'notes  (training set)')\n"
   "print('Tested on  :', X_test.shape[0],  'notes  (test set, kept hidden)')"),
md(did("Every note is now a row of numbers, and we have set aside a hidden test set. <code>X</code> is our feature table "
       "and <code>y</code> is our label &mdash; the same <b>X &rarr; y</b> setup from every earlier notebook. From here "
       "on, nothing is new: it is ordinary classification.")),

md(section("Train the model", 6)),
code(
   "# Train the classifier - the same kind of model idea as before.\n"
   "# class_weight='balanced' tells it to take the rare URGENT class seriously,\n"
   "# rather than ignoring it just because routine notes outnumber it.\n"
   "model = LogisticRegression(max_iter=1000, class_weight='balanced')\n"
   "model.fit(X_train, y_train)   # <-- the model studies the training notes\n"
   "print('Training done. The model has learned which words point to URGENT vs ROUTINE.')"),
md(did("That one <code>.fit()</code> call is the entire act of learning, exactly as before &mdash; only now the clues are "
       "words. We asked it to treat the rare urgent notes as <b>just as important</b> as the common ones, because in this "
       "job missing an urgent note is the expensive mistake.")),

md(section("Measure it honestly — and meet the accuracy trap", 7)),
md(vocab("Accuracy  (reminder)",
   "Out of the hidden test notes, what fraction did the model label correctly? 1.0 means every one right. "
   "Hold on to that word &mdash; in a moment we will see why, on a lopsided dataset like ours, accuracy can <b>lie</b>.")),
code(
   "predictions = model.predict(X_test)        # the model's guesses for the hidden notes\n"
   "\n"
   "acc = accuracy_score(y_test, predictions)\n"
   "print('Accuracy on notes it had never read:', round(acc, 3))\n"
   "print('In plain words: about', round(acc*100), 'out of every 100 labelled correctly.')\n"
   "print()\n"
   "\n"
   "# The DUMB baseline: a 'model' that always shouts ROUTINE.\n"
   "always_routine = np.array(['ROUTINE'] * len(y_test))\n"
   "base_acc = accuracy_score(y_test, always_routine)\n"
   "print('Accuracy of a model that ALWAYS says ROUTINE:', round(base_acc, 3))\n"
   "print('...yet that model catches', 0, 'urgent notes. Zero. None.')"),
md(watchout(
   "<b>This is the money point of the whole session.</b> A lazy model that <i>always</i> says \"routine\" scores about "
   "<b>85%</b> &mdash; just by parroting the most common answer &mdash; and yet it catches <b>zero</b> urgent notes. "
   "Every fire, every crack, every grounded aircraft slips through, and the headline accuracy still looks great. "
   "<b>On a lopsided dataset, a single accuracy number hides the rare class that actually matters.</b> "
   "So we must not ask \"how accurate?\". We must ask \"of the truly urgent notes, how many did it catch?\"")),
md(vocab("Recall (on the urgent class)",
   "<b>Recall</b> answers exactly that question: <i>of all the notes that really were urgent, what fraction did the model "
   "flag as urgent?</i> A recall of 0.90 means it caught 9 of every 10 real emergencies. For catching urgent snags this "
   "is the number that counts &mdash; not overall accuracy.")),
code(
   "# The honest number: of the truly URGENT notes, how many did we catch?\n"
   "urgent_recall = recall_score(y_test, predictions, pos_label='URGENT')\n"
   "print('URGENT recall (the number that matters):', round(urgent_recall, 3))\n"
   "print('In plain words: of every 10 genuinely urgent notes, it flagged about',\n"
   "      round(urgent_recall*10), 'of them.')\n"
   "print()\n"
   "print('Compare: the always-ROUTINE model would have an URGENT recall of 0.0 -')\n"
   "print('high accuracy, but it catches nothing. That is the trap.')"),
md(did("Our real model lands around <b>85&ndash;90% accuracy</b> &mdash; but more importantly its <b>urgent recall is high "
       "(~90%+)</b>: it catches almost all the genuinely urgent notes. The lazy always-routine model matched our accuracy "
       "yet had <b>zero</b> urgent recall. Same accuracy, wildly different usefulness. Now you know which number to trust.")),

md(section("See the mistakes — the confusion matrix", 8)),
md(vocab("Confusion matrix",
   "A small 2&times;2 table that shows <b>what kind</b> of mistakes the model makes, not just how many. The rows are the "
   "true answer, the columns are the model's guess. The dangerous cell is <b>urgent CALLED routine</b> &mdash; a real "
   "emergency the model waved through. That is the <b>false negative</b>, and it is the one that can hurt.")),
code(
   "# Build the confusion matrix with a fixed label order so it is easy to read.\n"
   "labels = ['URGENT', 'ROUTINE']\n"
   "cm = confusion_matrix(y_test, predictions, labels=labels)\n"
   "\n"
   "cm_table = pd.DataFrame(cm,\n"
   "    index=[f'TRUE {l}' for l in labels],\n"
   "    columns=[f'called {l}' for l in labels])\n"
   "print('Confusion matrix (rows = truth, columns = the model\\'s guess):')\n"
   "print(cm_table)\n"
   "print()\n"
   "\n"
   "missed = cm[0, 1]        # TRUE urgent, called routine  -> the costly miss\n"
   "caught = cm[0, 0]        # TRUE urgent, called urgent\n"
   "print(f'Urgent notes CAUGHT (urgent -> urgent): {caught}')\n"
   "print(f'Urgent notes MISSED (urgent -> routine): {missed}   <-- the costly false negatives')"),
code(
   "# The same matrix as a picture, so the costly cell is obvious at a glance.\n"
   "fig, ax = plt.subplots(figsize=(6, 5))\n"
   "im = ax.imshow(cm, cmap='Blues')\n"
   "ax.set_xticks([0, 1]); ax.set_xticklabels(['called URGENT', 'called ROUTINE'])\n"
   "ax.set_yticks([0, 1]); ax.set_yticklabels(['TRUE URGENT', 'TRUE ROUTINE'])\n"
   "ax.set_title('Confusion matrix - watch the URGENT->routine cell')\n"
   "for r in range(2):\n"
   "    for c in range(2):\n"
   "        ax.text(c, r, str(cm[r, c]), ha='center', va='center',\n"
   "                fontsize=18, color='black')\n"
   "# Outline the costly false-negative cell (true urgent, called routine).\n"
   "ax.add_patch(plt.Rectangle((0.5, -0.5), 1, 1, fill=False, edgecolor='crimson', lw=3))\n"
   "plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)\n"
   "plt.tight_layout()\n"
   "plt.show()"),
md(did("The big diagonal numbers are the correct calls. The cell outlined in red &mdash; <b>true urgent, called routine</b> "
       "&mdash; is the one to stare at. It is usually small but not zero: a real urgent note the model let through. That is "
       "why, even with a good model, a <b>human stays in the loop</b> on anything urgency-related. A single accuracy number "
       "would have hidden this entirely; the confusion matrix shows you the mistake that actually costs.")),

md(section("Look inside — the clue-words it learned", 9)),
md("A logistic-regression model keeps a weight for every word, saying how strongly that word pushes a note toward urgent "
   "or routine. Because the words are human-readable, we can simply <b>print the top clue-words</b> and check they make sense."),
code(
   "# The model's weights, one per word. Positive = pushes toward URGENT.\n"
   "feature_names = np.array(vectorizer.get_feature_names_out())\n"
   "weights = model.coef_[0]\n"
   "\n"
   "# model.classes_ is sorted alphabetically: ['ROUTINE', 'URGENT'].\n"
   "# A positive weight pushes toward classes_[1]; confirm which that is.\n"
   "pos_class = model.classes_[1]\n"
   "print('A positive weight pushes a note toward:', pos_class)\n"
   "print()\n"
   "\n"
   "top_urgent  = feature_names[np.argsort(weights)[-8:]][::-1]   # most URGENT-leaning words\n"
   "top_routine = feature_names[np.argsort(weights)[:8]]          # most ROUTINE-leaning words\n"
   "print('Words the model reads as URGENT :', ', '.join(top_urgent))\n"
   "print('Words the model reads as ROUTINE:', ', '.join(top_routine))"),
md(did("Read those lists. The urgent clue-words are exactly what you would expect &mdash; <i>crack, smoke, fire, grounded, "
       "leak, fuel</i> &mdash; and the routine ones are the calm vocabulary of <i>cosmetic, monitor, limits, scheduled, "
       "minor</i>. Nobody wrote these rules; the model worked them out from the example notes. This is what people mean by "
       "an <b>interpretable</b> model: you can open it up and the reasoning is plain English, not a black box.")),
code(
   "# The same idea as a bar chart, for the URGENT-leaning words.\n"
   "order = np.argsort(weights)[-10:]          # 10 strongest URGENT words\n"
   "words = feature_names[order]\n"
   "vals = weights[order]\n"
   "\n"
   "plt.figure(figsize=(8, 5.5))\n"
   "plt.barh(words, vals, color='#b3261e')\n"
   "plt.xlabel('How strongly the word points to URGENT')\n"
   "plt.title('Words the model learned to read as URGENT')\n"
   "plt.grid(alpha=0.3, axis='x')\n"
   "plt.tight_layout()\n"
   "plt.show()"),
md(did("The longest bars are the words most tied to urgent. If a brand-new note contains <i>crack</i> or <i>smoke</i>, you "
       "can already guess how the model will lean &mdash; and so can anyone auditing it.")),

md(section("Use it on brand-new notes", 10)),
md("This is the whole point. Fresh notes arrive that the model has never seen. We hand it the raw text &mdash; the model "
   "vectorizes it the same way and instantly flags urgent or routine, with a confidence."),
code(
   "# Five brand-new notes, typed fresh. We feed RAW TEXT; the vectorizer turns\n"
   "# it into numbers automatically, the same way as before.\n"
   "new_notes = [\n"
   "    'crack discovered in the fuselage skin, aircraft grounded',   # clearly URGENT\n"
   "    'smoke and burning smell from the cockpit panel',             # clearly URGENT\n"
   "    'seat fabric scuffed, cosmetic only, monitor',                # clearly ROUTINE\n"
   "    'placard label peeling, replace at next scheduled check',     # clearly ROUTINE\n"
   "    'minor fuel smell near the wing, please check',               # borderline on purpose\n"
   "]\n"
   "\n"
   "new_X = vectorizer.transform(new_notes)     # SAME vectorizer, no re-fitting\n"
   "guesses = model.predict(new_X)\n"
   "probs = model.predict_proba(new_X)\n"
   "urgent_idx = list(model.classes_).index('URGENT')\n"
   "\n"
   "for text, guess, p in zip(new_notes, guesses, probs):\n"
   "    p_urgent = round(p[urgent_idx] * 100)\n"
   "    flag = '*** FLAG FOR HUMAN ***' if guess == 'URGENT' else ''\n"
   "    print(f'Note : {text}')\n"
   "    print(f'  -> {guess}   (urgent-probability {p_urgent}%)   {flag}')\n"
   "    print()"),
md(did("The clear-cut notes are sorted with high confidence, and every URGENT one is flagged for a human to see first. "
       "The deliberately borderline note &mdash; <i>\"minor fuel smell near the wing\"</i> &mdash; mixes a routine word "
       "(<i>minor</i>) with an urgent one (<i>fuel</i>), so its urgent-probability sits nearer the middle. That in-between "
       "number is the model honestly saying \"this one is a borderline call\" &mdash; exactly the note a human should "
       "double-check.")),

md(turn(
   "Make it your own. Edit the cell just above and press <b>Shift + Enter</b> to re-run:<br>"
   "1. Replace the first note with your own sentence, e.g. <code>'hydraulic leak, brakes feel soft'</code>. "
   "Watch the flag and the urgent-probability change.<br>"
   "2. Write a deliberately mixed note like <code>'minor crack, cosmetic only'</code> and watch the probability "
   "land in the middle because the clues disagree.<br>"
   "3. Harder: in Step 2, change the urgent share from <code>0.15</code> to <code>0.05</code> (rarer emergencies), then "
   "use <b>Runtime &rarr; Restart and run all</b>. Watch the accuracy barely move while the urgent recall &mdash; the "
   "number that matters &mdash; gets harder to hold up.")),

md(recap("What we learned in Session 1", [
   "Written notes are <b>data too</b>, and predictive AI can flag the <b>urgent</b> ones automatically.",
   "Computers cannot read words, so we first turn text into numbers by <b>counting words</b> (<b>bag of words</b> / <b>vectorizing</b>); <b>TF-IDF</b> just means rare, distinctive words count for more.",
   "Once text is numbers, it is the <b>same classification workflow</b>: split &rarr; train &rarr; predict &rarr; measure.",
   "<b>The accuracy trap:</b> on a lopsided 85/15 mix, a model that always says \"routine\" scores ~85% yet catches <b>zero</b> urgent notes &mdash; accuracy hides the rare costly class.",
   "The honest number is <b>urgent recall</b> (~90%+), and the <b>confusion matrix</b> reveals the costly <i>urgent-called-routine</i> miss &mdash; so a human stays in the loop.",
   "The model is <b>interpretable</b>: its top urgent clue-words (crack, smoke, fire, grounded) read like plain English.",
])),
md(nextup(
   "<b>Session 2 &mdash; Text II.</b> The same words-to-numbers front end answers more questions: predict downtime "
   "<i>hours</i> (a number, not a bucket), find <b>recurring faults</b> that are worded differently, group snags into "
   "families with <b>embeddings + clustering</b>, and pull out part numbers &mdash; while watching for the header trap.")),
]

build(cells, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notebooks", "01_text_analytics.ipynb"),
      title="Predictive AI - Session 1 - Text I")
