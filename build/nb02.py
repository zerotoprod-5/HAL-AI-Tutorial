import sys; sys.path.insert(0, "/tmp")
from nbbuild import *

CLASSIFY_VS_REGRESS = """
<table style="border-collapse:collapse;width:100%;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:15px;margin:8px 0;">
<tr style="background:#1f2d3d;color:#fff;">
  <th style="padding:10px 14px;text-align:left;">&nbsp;</th>
  <th style="padding:10px 14px;text-align:left;">Classification &nbsp;(notebooks 0 &amp; 1)</th>
  <th style="padding:10px 14px;text-align:left;">Regression &nbsp;(this notebook)</th>
</tr>
<tr style="background:#eef4f5;">
  <td style="padding:10px 14px;font-weight:700;">The answer is</td>
  <td style="padding:10px 14px;">A <b>category</b> &mdash; a label from a short list</td>
  <td style="padding:10px 14px;">A <b>number</b> &mdash; on a sliding scale</td>
</tr>
<tr>
  <td style="padding:10px 14px;font-weight:700;">Examples</td>
  <td style="padding:10px 14px;">Needs service / fine &nbsp;&middot;&nbsp; pass / reject</td>
  <td style="padding:10px 14px;">Monthly cost in rupees &nbsp;&middot;&nbsp; power used &nbsp;&middot;&nbsp; hours left</td>
</tr>
<tr style="background:#eef4f5;">
  <td style="padding:10px 14px;font-weight:700;">We score it with</td>
  <td style="padding:10px 14px;"><b>Accuracy</b> &mdash; what fraction we got right</td>
  <td style="padding:10px 14px;"><b>Average error</b> &mdash; how far off, on average</td>
</tr>
<tr>
  <td style="padding:10px 14px;font-weight:700;">Same idea?</td>
  <td style="padding:10px 14px;font-weight:700;color:#0b6e7a;" colspan="2">Yes &mdash; learn a pattern from past examples, apply it to a new case. Only the <i>kind</i> of answer differs.</td>
</tr>
</table>
"""

cells = [
md(banner("Notebook 2 of 6", "Regression &amp; Forecasting: Predicting Numbers",
   "When the answer is not a category but a quantity &mdash; a cost, an amount, a trend over time")),

md("## How to use this notebook\n\n"
   "Same as before. You do not write any code &mdash; you only **run** the cells, top to bottom, and read what comes out.\n\n"
   "- To run a cell: click it, then press **Shift + Enter** (or the &#9654; play button on its left).\n"
   "- Run them **in order**. Each cell builds on the one above it.\n"
   "- If anything looks broken, use the menu: **Runtime &rarr; Restart and run all**, then start again.\n\n"
   "The coloured boxes mean the same thing they did in Notebook 0: "
   "<b style=\"color:#0b6e7a;\">teal</b> is a new word, "
   "<b style=\"color:#2e7d32;\">green</b> is what the cell just did, "
   "<b style=\"color:#b26a00;\">amber</b> is a number for you to change and re-run, "
   "<b style=\"color:#5b2a86;\">purple</b> is the big picture."),

md(bigidea(
   "In the first two notebooks every answer was a <b>category</b>: needs service or fine, pass or reject. "
   "But a huge share of real questions ask for a <b>number</b> instead. "
   "How much will this machine cost to run next month? How many spare parts will we need? How many hours of life are left?<br><br>"
   "Predicting a number is called <b>regression</b>. Predicting a number as it moves over <b>time</b> is called <b>forecasting</b>. "
   "It is the very same idea you already know &mdash; <i>learn a pattern from past examples, then apply it to a new case</i> &mdash; "
   "only now the answer slides along a scale instead of landing in a box.<br><br>"
   "This notebook has two short parts. <b>Part A</b> predicts a machine's monthly running cost. "
   "<b>Part B</b> forecasts next year's spare-parts demand. Two clear pictures will do the teaching: "
   "a straight line drawn through a cloud of dots, and that same line continuing past today into the future.")),

# =====================================================================
# PART A
# =====================================================================
md(section("Set up our tools", 1)),
md("A quick reminder of words you already met in Notebook 0: a <b>library</b> is a ready-made toolbox of code. "
   "<code>pandas</code> handles tables, <code>scikit-learn</code> is the machine-learning toolbox, "
   "<code>matplotlib</code> draws charts. We just borrow them again."),
code(
   "# Import the toolboxes. Running this cell shows no output - that is normal.\n"
   "import numpy as np\n"
   "import pandas as pd\n"
   "import matplotlib.pyplot as plt\n"
   "\n"
   "from sklearn.model_selection import train_test_split\n"
   "from sklearn.linear_model import LinearRegression\n"
   "from sklearn.metrics import mean_absolute_error\n"
   "\n"
   "print('Tools loaded. We are ready.')"),
md(did("We loaded the same kind of toolboxes as before. The one new face is "
       "<code>LinearRegression</code> &mdash; the model that predicts a <b>number</b> instead of a category. "
       "We meet it properly in Step 4.")),

md(banner("Part A", "Regression &mdash; predict a number",
   "Predict a machine's monthly running cost from its load level and its age")),

md(vocab("Regression",
   "<b>Regression</b> is predicting a <b>number on a sliding scale</b> rather than a category. "
   "\"Will this machine need service?\" (yes / no) was classification. "
   "\"What will this machine cost to run next month?\" (could be Rs 5,000 or Rs 14,732 or anything between) is regression. "
   "Same learn-from-the-past machinery &mdash; the answer is just a quantity now.")),
md(vocab("Continuous value",
   "A <b>continuous value</b> is a number that can land anywhere on a scale, with no gaps &mdash; "
   "like a temperature, a weight, or a rupee cost. It is the opposite of a category, which only has a few fixed options. "
   "Regression predicts continuous values.")),
md(CLASSIFY_VS_REGRESS),

md(story(
   "<b>Part A scenario: the monthly running-cost estimate.</b><br>"
   "A workshop runs many machines. Each one costs money every month &mdash; electricity, wear, upkeep. "
   "The finance team would love to <b>estimate that monthly cost up front</b> from two simple facts they always know about a machine: "
   "how hard it is worked (its <b>load level</b>, as a percentage) and how old it is (its <b>age in years</b>).<br><br>"
   "Common sense says a heavily-loaded, older machine costs more to run than a lightly-used new one. "
   "We will let the computer learn exactly <i>how much</i> more, from past cost records.")),

md(section("Build the cost records", 2)),
md(vocab("Label (for regression)",
   "Same word as Notebook 0, new flavour. The <b>label</b> is still the answer we want to predict &mdash; "
   "but here it is a <b>number</b> (<code>monthly_cost</code> in rupees), not a 1-or-0 category. "
   "The two input columns, <code>load_percent</code> and <code>age_years</code>, are still the <b>features</b> (the clues).")),
code(
   "# We create 250 past machine cost records. In real life this would come from\n"
   "# your accounts; here we generate it so everyone has identical data.\n"
   "rng = np.random.default_rng(42)   # fixed seed => everyone sees the same numbers\n"
   "n = 250\n"
   "\n"
   "load_percent = rng.uniform(20, 100, n).round(1)   # how hard it is worked (%)\n"
   "age_years    = rng.uniform(0, 15, n).round(1)      # how old it is (years)\n"
   "\n"
   "# The hidden truth we pretend not to know: cost rises with both load and age,\n"
   "# plus real-world noise (no two machines are ever identical).\n"
   "monthly_cost = (3000 + 95*load_percent + 480*age_years\n"
   "                + rng.normal(0, 1400, n)).round(0)   # rupees per month\n"
   "\n"
   "df = pd.DataFrame({\n"
   "    'load_percent': load_percent,\n"
   "    'age_years':    age_years,\n"
   "    'monthly_cost': monthly_cost,\n"
   "})\n"
   "\n"
   "df.head(8)   # show the first 8 machines"),
md(did("There is our <b>dataset</b>: 250 machines, one per row. The first two columns are the "
       "<b>features</b> (load and age, the clues). The last column, <code>monthly_cost</code>, is the "
       "<b>label</b> &mdash; the rupee number we want to predict. Notice it is a full number, not just 0 or 1.")),
code(
   "# A quick look at typical values - the rupee costs span a wide range.\n"
   "print('Rows and columns:', df.shape)\n"
   "print()\n"
   "print('Typical values per column:')\n"
   "df.describe().round(0)"),
md(did("Monthly cost runs from a few thousand rupees up to around twenty thousand, depending on the machine. "
       "That wide spread is exactly why a single average would be a poor guess &mdash; "
       "a young, lightly-loaded machine and an old, hard-worked one are nowhere near the same cost.")),

md(section("See the trend with our own eyes", 3)),
md("Before any modelling, let us simply <i>draw</i> the data. We plot <b>age</b> against <b>cost</b>, "
   "one dot per machine. If our common-sense story holds, the dots should drift upward as we move right."),
code(
   "plt.figure(figsize=(8, 5.5))\n"
   "plt.scatter(df['age_years'], df['monthly_cost'],\n"
   "            c='#0b6e7a', alpha=0.6, edgecolors='white')\n"
   "\n"
   "plt.xlabel('Age of machine (years)')\n"
   "plt.ylabel('Monthly running cost (Rs)')\n"
   "plt.title('Each dot is one machine: older machines tend to cost more')\n"
   "plt.grid(alpha=0.3)\n"
   "plt.show()"),
md(did("The cloud of dots clearly <b>slopes upward</b> to the right: older machines tend to cost more to run. "
       "It is not a perfect straight march &mdash; the dots scatter, because load and plain randomness also matter &mdash; "
       "but the upward <b>trend</b> is unmistakable. That trend is the pattern a regression model will capture.")),

md(section("Fit a line through the dots", 4)),
md(vocab("Line of best fit",
   "Imagine laying a single straight ruler across that cloud of dots so it sits as <b>close as possible to all of them at once</b> &mdash; "
   "not touching every dot, but balanced through the middle of the crowd. "
   "That ruler is the <b>line of best fit</b>. The model's whole job in regression is to find the one best position for it. "
   "Once placed, the line gives a cost estimate for <i>any</i> age you point to.")),
md(vocab("Fit (training, for regression)",
   "Same <code>.fit()</code> you already know. For regression, <b>fitting</b> means sliding and tilting that line until it sits as "
   "close as possible to the past dots. One line of code does it.")),
code(
   "# For the picture, we first learn the line using ONE feature: age.\n"
   "age_only = LinearRegression()\n"
   "age_only.fit(df[['age_years']], df['monthly_cost'])   # find the best line\n"
   "\n"
   "# Build the line's height across the full age range, to draw it.\n"
   "age_grid  = pd.DataFrame({'age_years': np.linspace(0, 15, 100)})\n"
   "line_cost = age_only.predict(age_grid)\n"
   "\n"
   "plt.figure(figsize=(8, 5.5))\n"
   "plt.scatter(df['age_years'], df['monthly_cost'],\n"
   "            c='#0b6e7a', alpha=0.5, edgecolors='white', label='Past machines')\n"
   "plt.plot(age_grid['age_years'], line_cost, c='#9c2b2b', linewidth=3, label='Line of best fit')\n"
   "\n"
   "plt.xlabel('Age of machine (years)')\n"
   "plt.ylabel('Monthly running cost (Rs)')\n"
   "plt.title('The model finds the straight line closest to all the dots')\n"
   "plt.legend()\n"
   "plt.grid(alpha=0.3)\n"
   "plt.show()"),
md(did("There it is &mdash; the first big picture of this notebook. The red <b>line of best fit</b> runs straight "
       "through the middle of the dot cloud, rising with age. The computer was not told where to put it; "
       "it <b>slid the line into the position that sits closest to every dot at once</b>. "
       "Point at any age on the bottom axis, read the red line, and you have a cost estimate.")),

md(section("Train the real model and measure its error", 5)),
md("The picture used age alone so we could see it on a flat chart. The real model uses <b>both</b> clues &mdash; "
   "load and age &mdash; together. We train it the usual way: split off a hidden test set, fit on the rest, "
   "then check it on machines it never saw."),
md(vocab("Error (MAE)",
   "For categories we used <b>accuracy</b>. For numbers, accuracy makes no sense &mdash; we will almost never hit the cost to the exact rupee. "
   "Instead we ask: <b>on average, how far off are we?</b> The <b>Mean Absolute Error (MAE)</b> answers exactly that. "
   "An MAE of Rs 1,100 means: <i>typically, our estimate is off by about eleven hundred rupees</i> &mdash; high or low. "
   "Lower is better. It is in the same rupees as the thing we predict, so it reads in plain money.")),
code(
   "# Use BOTH clues now. X = the features, y = the number we predict.\n"
   "X = df[['load_percent', 'age_years']]   # the two clues\n"
   "y = df['monthly_cost']                   # the number to predict\n"
   "\n"
   "X_train, X_test, y_train, y_test = train_test_split(\n"
   "    X, y, test_size=0.25, random_state=0)   # hide 25% for an honest test\n"
   "\n"
   "model = LinearRegression()\n"
   "model.fit(X_train, y_train)   # <-- the model finds the best fit on past data\n"
   "\n"
   "predictions = model.predict(X_test)   # estimate cost for the hidden machines\n"
   "mae = mean_absolute_error(y_test, predictions)\n"
   "\n"
   "print('Tested on', X_test.shape[0], 'machines the model had never seen.')\n"
   "print('Average error (MAE): about Rs', round(mae))\n"
   "print('In plain words: our cost estimate is typically off by ~Rs', round(mae), 'either way.')"),
md(did("On machines it had never seen, the model's cost estimate is typically off by only "
       "<b>around Rs 1,100</b> &mdash; against costs that run to twenty thousand. "
       "That is a genuinely useful estimate, and the small error is healthy: real costs have surprises, "
       "and a model that claimed zero error would be cheating somehow.")),
code(
   "# A second way to SEE how good it is: plot predicted cost against the real cost.\n"
   "# Perfect predictions would land exactly on the diagonal line.\n"
   "plt.figure(figsize=(8, 5.5))\n"
   "plt.scatter(y_test, predictions, c='#2e7d32', alpha=0.6, edgecolors='white',\n"
   "            label='Test machines')\n"
   "\n"
   "lo = min(y_test.min(), predictions.min())\n"
   "hi = max(y_test.max(), predictions.max())\n"
   "plt.plot([lo, hi], [lo, hi], c='#9c2b2b', linewidth=2, linestyle='--',\n"
   "         label='Perfect prediction')\n"
   "\n"
   "plt.xlabel('Actual monthly cost (Rs)')\n"
   "plt.ylabel('Predicted monthly cost (Rs)')\n"
   "plt.title('Points hug the diagonal => predictions are close to reality')\n"
   "plt.legend()\n"
   "plt.grid(alpha=0.3)\n"
   "plt.show()"),
md(did("Each green dot is one test machine: its true cost across the bottom, our estimate up the side. "
       "The dots <b>cluster tightly along the dashed diagonal</b>, which is where a perfect estimate would land. "
       "Close to the line means a good estimate; the small scatter around it is exactly the ~Rs 1,100 average error in picture form.")),

md(section("Estimate the cost of two brand-new machines", 6)),
md("This is the payoff. Two new machines arrive and we want their monthly cost <i>before</i> the bills come in. "
   "We hand each one's two numbers to the trained model and read back an instant rupee estimate."),
code(
   "# A light, new machine: low load, almost brand new.\n"
   "light_new = pd.DataFrame([{'load_percent': 30, 'age_years': 1}])\n"
   "est1 = model.predict(light_new)[0]\n"
   "print('Light + new machine :', light_new.to_dict('records')[0])\n"
   "print('  Estimated monthly cost: about Rs', round(est1))\n"
   "print()\n"
   "\n"
   "# A heavy, old machine: high load, well-aged.\n"
   "heavy_old = pd.DataFrame([{'load_percent': 95, 'age_years': 13}])\n"
   "est2 = model.predict(heavy_old)[0]\n"
   "print('Heavy + old machine :', heavy_old.to_dict('records')[0])\n"
   "print('  Estimated monthly cost: about Rs', round(est2))"),
md(did("The model estimates the light, new machine at roughly <b>Rs 6,000</b> a month and the heavy, old one at around "
       "<b>Rs 18,000</b> &mdash; about three times as much. That ordering matches plain common sense, "
       "but now we have an actual rupee figure for each, produced in an instant and consistent across thousands of machines.")),

# =====================================================================
# PART B
# =====================================================================
md(banner("Part B", "Forecasting &mdash; predict over time",
   "Forecast next year's spare-parts demand so the workshop can stock up in advance")),

md(story(
   "<b>Part B scenario: planning the spare-parts shelf.</b><br>"
   "The workshop's store keeps spare parts on the shelf. Order too few and machines sit idle waiting; "
   "order too many and cash is tied up gathering dust. To plan well, the store manager wants to know: "
   "<b>roughly how many parts will we use each month over the coming year?</b><br><br>"
   "All they have is the past &mdash; three years of monthly usage records. "
   "We will read the shape of that history and <b>project it forward</b>.")),

md(vocab("Forecasting",
   "<b>Forecasting</b> is regression where the main clue is <b>time</b>. "
   "Instead of \"given this machine's numbers, what is its cost?\", we ask "
   "\"given how demand has moved month after month, what comes <i>next</i>?\" "
   "The answer is still a number; the input is the calendar.")),
md(vocab("Trend",
   "A <b>trend</b> is the overall direction the numbers drift over time &mdash; slowly rising, slowly falling, or flat. "
   "If spare-parts usage creeps up a little every year as the fleet ages, that steady climb is the trend.")),
md(vocab("Seasonality",
   "<b>Seasonality</b> is a pattern that <b>repeats on a calendar</b> &mdash; the same bump at the same time, "
   "year after year. Maybe usage rises every monsoon, or before an annual overhaul. "
   "It is the regular wiggle that rides on top of the overall trend.")),

md(section("Build and plot the demand history", 7)),
code(
   "# We create 36 months (3 years) of past spare-parts demand.\n"
   "# In real life this is your store's issue register; here we generate it.\n"
   "rng2 = np.random.default_rng(42)\n"
   "months      = 36\n"
   "month_index = np.arange(months)          # 0, 1, 2, ... 35\n"
   "month_of_year = month_index % 12          # 0..11, the calendar position\n"
   "\n"
   "# Hidden truth: a gentle upward TREND + a repeating SEASONAL wiggle + noise.\n"
   "trend  = 120 + 4.2 * month_index\n"
   "season = 22*np.sin(2*np.pi*month_of_year/12) + 12*np.cos(2*np.pi*month_of_year/12)\n"
   "noise  = rng2.normal(0, 13, months)\n"
   "demand = (trend + season + noise).round(0)   # parts used that month\n"
   "\n"
   "hist = pd.DataFrame({'month_index': month_index, 'demand': demand})\n"
   "print('First 6 months of history:')\n"
   "print(hist.head(6).to_string(index=False))"),
md(did("We now have three years of monthly demand, with two ingredients baked in: a slow upward "
       "<b>trend</b> (the fleet uses a little more each year) and a repeating <b>seasonal</b> wiggle. "
       "The numbers below are what the store actually issued each month &mdash; let us plot them.")),
code(
   "plt.figure(figsize=(8, 5.5))\n"
   "plt.plot(hist['month_index'], hist['demand'],\n"
   "         c='#0b6e7a', linewidth=2, marker='o', markersize=4)\n"
   "\n"
   "plt.xlabel('Month number (0 = three years ago)')\n"
   "plt.ylabel('Spare parts used')\n"
   "plt.title('Three years of monthly spare-parts demand')\n"
   "plt.grid(alpha=0.3)\n"
   "plt.show()"),
md(did("Two things jump out. The line <b>drifts upward</b> over the three years &mdash; that is the <b>trend</b>. "
       "And it <b>wiggles up and down in a repeating rhythm</b> rather than climbing smoothly &mdash; that is the "
       "<b>seasonality</b>, the same calendar bump returning each year. A good forecast has to capture both.")),

md(section("Teach a model the trend and the season", 8)),
md("We use the same <code>LinearRegression</code> from Part A &mdash; no new tool. "
   "We give it three clues about each month: the <b>month number</b> (which carries the rising trend) and two "
   "<b>seasonal markers</b> that tell the model where we are in the yearly cycle. With those, one straight-line model "
   "can ride both the climb and the repeating wiggle."),
md(note("The two seasonal markers are just a standard way to hand the model a calendar position as numbers "
        "(a sine and cosine of the month). You do not need the maths &mdash; think of them as a dial that tells the "
        "model \"we are <i>here</i> in the yearly cycle\", so it can add the right seasonal bump.")),
code(
   "# Turn a list of month numbers into the three clues the model reads.\n"
   "def make_features(idx):\n"
   "    moy = idx % 12                                   # position in the year (0..11)\n"
   "    return np.column_stack([\n"
   "        idx,                                          # month number  -> the trend\n"
   "        np.sin(2*np.pi*moy/12),                       # seasonal marker 1\n"
   "        np.cos(2*np.pi*moy/12),                       # seasonal marker 2\n"
   "    ])\n"
   "\n"
   "X_time = make_features(month_index)\n"
   "\n"
   "ts_model = LinearRegression()\n"
   "ts_model.fit(X_time, demand)   # learn trend + season from the 36 past months\n"
   "\n"
   "fitted = ts_model.predict(X_time)\n"
   "fit_mae = mean_absolute_error(demand, fitted)\n"
   "print('The model has learned the history.')\n"
   "print('On the past months it is off by only ~', round(fit_mae), 'parts on average.')"),
md(did("The model learned the shape of the past in one <code>.fit()</code>: it captured both the upward trend "
       "and the repeating seasonal bump, matching the historical months to within about <b>8 parts</b> on average. "
       "Now the interesting part &mdash; we ask it about months it has never seen: the future.")),

md(section("Forecast the next 6 months", 9)),
md(vocab("Forecast horizon",
   "The <b>forecast horizon</b> is how far ahead we predict. Here it is the next <b>6 months</b> "
   "(month numbers 36 to 41). We simply ask the trained model for those future months &mdash; "
   "it continues the trend and keeps applying the seasonal rhythm.")),
code(
   "# The next 6 months carry on from where history stopped.\n"
   "future_index = np.arange(months, months + 6)        # 36, 37, ... 41\n"
   "future_X     = make_features(future_index)\n"
   "forecast     = ts_model.predict(future_X).round(0)   # the projected demand\n"
   "\n"
   "for m, f in zip(future_index, forecast):\n"
   "    print('Month', m, '(future)  ->  forecast', int(f), 'parts')"),
md(did("The model projects demand for each of the next six months, carrying the upward trend forward and still "
       "applying the seasonal wiggle. These are the numbers the store manager would stock against. "
       "One picture makes it land &mdash; let us draw history and forecast on the same chart.")),
code(
   "plt.figure(figsize=(8, 5.5))\n"
   "\n"
   "# History: solid teal line.\n"
   "plt.plot(month_index, demand, c='#0b6e7a', linewidth=2, marker='o',\n"
   "         markersize=4, label='History (what happened)')\n"
   "\n"
   "# Forecast: dashed amber line, starting where history ends.\n"
   "bridge_x = np.append(month_index[-1], future_index)\n"
   "bridge_y = np.append(demand[-1],      forecast)\n"
   "plt.plot(bridge_x, bridge_y, c='#b26a00', linewidth=2.5, linestyle='--',\n"
   "         marker='s', markersize=5, label='Forecast (next 6 months)')\n"
   "\n"
   "plt.axvline(month_index[-1], color='#9c2b2b', linewidth=1, alpha=0.5)\n"
   "plt.text(month_index[-1]-0.3, demand.min(), 'today', color='#9c2b2b',\n"
   "         ha='right', fontsize=11)\n"
   "\n"
   "plt.xlabel('Month number')\n"
   "plt.ylabel('Spare parts used')\n"
   "plt.title('Forecast continues the trend past today')\n"
   "plt.legend()\n"
   "plt.grid(alpha=0.3)\n"
   "plt.show()"),
md(did("There is the second big picture of the notebook. The solid teal line is the real past; "
       "the dashed amber line is the model's <b>forecast</b>, picking up exactly where history stops "
       "and <b>carrying the same rising, wiggling pattern into the future</b>. "
       "That visual continuation is the whole idea of forecasting: project tomorrow from the shape of yesterday.")),
md(note("An honest caveat. A forecast is a <b>best guess, not a promise</b>. The further out we look, "
        "the less certain it gets &mdash; a sudden new contract or a supplier delay can bend the real line away "
        "from our dashed one. That is why real planners never order the forecast exactly; they add a "
        "<b>safety margin</b> on top, larger for months further ahead.")),

# =====================================================================
# WRAP-UP
# =====================================================================
md(turn(
   "Make it your own. Edit a number, press <b>Shift + Enter</b> to re-run, and watch what changes:<br>"
   "1. In Step 6, change the new machine to <code>load_percent: 100, age_years: 15</code> "
   "(maxed out and oldest). Does the estimated cost climb as you would expect?<br>"
   "2. In Step 9, change <code>months + 6</code> to <code>months + 18</code> to forecast a year and a half ahead. "
   "Re-run the plot cell too. Notice the dashed line stretching further &mdash; and remember the caveat: "
   "the far end is a weaker guess.<br>"
   "3. In Step 7, change the noise from <code>0, 13</code> to <code>0, 45</code> (a much shakier history). "
   "Re-run everything in Part B. The history gets jagged and the fit error grows &mdash; messier data, less certain forecast.")),

md(recap("What we learned in Notebook 2", [
   "<b>Regression</b> predicts a <b>number on a sliding scale</b> (a cost, an amount) &mdash; classification predicted a category. Same learn-from-the-past idea, different kind of answer.",
   "The <b>line of best fit</b> is the straight line placed as close as possible to all the past dots at once; <code>.fit()</code> finds its position.",
   "For numbers we score with <b>average error (MAE)</b>, read in plain rupees &mdash; \"typically off by about Rs X\" &mdash; not accuracy.",
   "<b>Forecasting</b> is regression where the clue is <b>time</b>: capture the <b>trend</b> (overall drift) and the <b>seasonality</b> (the repeating calendar wiggle), then project forward.",
   "A forecast is a best guess that weakens the further out it reaches &mdash; real planners add a <b>safety margin</b>.",
])),
md(nextup(
   "<b>Notebook 3 &mdash; Predictive Maintenance.</b> We bring the threads together on a whole fleet: "
   "classification to flag which machines are at risk, the number-prediction ideas from today for things like "
   "remaining life, and a first look at <i>which signal matters most</i> &mdash; so you can tell not just "
   "<i>that</i> a machine needs attention, but <i>why</i>.")),
]

build(cells, "/Users/flam/Desktop/HAL_AI/notebooks/02_regression_forecasting.ipynb",
      title="Predictive AI 02 - Regression and Forecasting")
