import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbbuild import *

# ---------------------------------------------------------------------------
# A small visual map of the whole pipeline: speak -> transcribe -> categorize.
# Pure HTML so it renders identically in Colab without any extra library.
# ---------------------------------------------------------------------------
PIPELINE = """
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
display:flex;align-items:stretch;gap:10px;margin:14px 0;flex-wrap:wrap;">
  <div style="flex:1;min-width:150px;background:#eef2f6;border-left:5px solid #1f2d3d;border-radius:6px;padding:14px 16px;">
    <div style="font-size:12px;letter-spacing:.5px;color:#1f2d3d;font-weight:700;text-transform:uppercase;">Step A &mdash; Speak</div>
    <div style="font-size:15px;color:#222;margin-top:6px;line-height:1.5;">A technician <b>says</b> a quick report out loud.<br><i>"There is an oil leak near the hydraulic pump."</i></div>
  </div>
  <div style="display:flex;align-items:center;color:#0b6e7a;font-size:26px;font-weight:800;">&rarr;</div>
  <div style="flex:1;min-width:150px;background:#e6f4f6;border-left:5px solid #0b6e7a;border-radius:6px;padding:14px 16px;">
    <div style="font-size:12px;letter-spacing:.5px;color:#0b6e7a;font-weight:700;text-transform:uppercase;">Step B &mdash; Transcribe</div>
    <div style="font-size:15px;color:#222;margin-top:6px;line-height:1.5;">The computer <b>listens</b> and turns the audio into plain <b>text</b>.<br>(Speech-to-text / ASR)</div>
  </div>
  <div style="display:flex;align-items:center;color:#0b6e7a;font-size:26px;font-weight:800;">&rarr;</div>
  <div style="flex:1;min-width:150px;background:#f2eaf7;border-left:5px solid #5b2a86;border-radius:6px;padding:14px 16px;">
    <div style="font-size:12px;letter-spacing:.5px;color:#5b2a86;font-weight:700;text-transform:uppercase;">Step C &mdash; Categorize</div>
    <div style="font-size:15px;color:#222;margin-top:6px;line-height:1.5;">The <b>same text analytics</b> from Notebook 4 sorts it into a category.<br>&rarr; <b>Hydraulic</b></div>
  </div>
</div>
"""

# A tiny "neither magic nor nonsense" recap table tying the six notebooks together.
SERIES_TABLE = """
<table style="border-collapse:collapse;width:100%;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:15px;margin:10px 0;">
<tr style="background:#1f2d3d;color:#fff;">
  <th style="padding:10px 14px;text-align:left;">Notebook</th>
  <th style="padding:10px 14px;text-align:left;">Kind of data</th>
  <th style="padding:10px 14px;text-align:left;">The one idea, every time</th>
</tr>
<tr style="background:#eef4f5;">
  <td style="padding:9px 14px;font-weight:700;">0 &ndash; 3</td>
  <td style="padding:9px 14px;"><b>Numbers</b> &mdash; hours, temperature, vibration, cost</td>
  <td style="padding:9px 14px;" rowspan="3">Learn the pattern from <b>past examples</b>,<br>then make a call on a <b>new case</b>.</td>
</tr>
<tr>
  <td style="padding:9px 14px;font-weight:700;">4</td>
  <td style="padding:9px 14px;"><b>Text</b> &mdash; written maintenance notes</td>
</tr>
<tr style="background:#eef4f5;">
  <td style="padding:9px 14px;font-weight:700;">5 (this one)</td>
  <td style="padding:9px 14px;"><b>Speech</b> &mdash; a spoken report</td>
</tr>
</table>
"""

cells = [

# ---- Banner + how to run -------------------------------------------------
md(banner("Speech Analytics &middot; Session 3 of 4", "Speech Analytics: From Spoken Report to Decision",
   "Turn a technician's spoken maintenance note into an automatic category &mdash; with nobody typing")),

md("## How to use this notebook\n\n"
   "Same as every notebook today: you only **run** the cells, top to bottom, and read what comes out. "
   "You do not write any code.\n\n"
   "- To run a cell: click it, then press **Shift + Enter** (or the &#9654; play button on its left).\n"
   "- Run them **in order** &mdash; each cell builds on the one above it.\n"
   "- If anything looks stuck, use the menu: **Runtime &rarr; Restart and run all**, then start again.\n\n"
   "This notebook needs a one-time setup &mdash; the very first code cell below installs two extra speech tools and takes "
   "about a minute. After that, everything runs as usual."),

# ---- Big idea + scenario -------------------------------------------------
md(bigidea(
   "All session long we predicted from <b>numbers</b> (Notebooks 0&ndash;3) and then from written <b>text</b> (Notebook 4). "
   "There is one last kind of messy data left: <b>spoken words</b>.<br><br>"
   "A technician on the floor would rather <b>speak</b> a quick report than stop and type it. So the question becomes: "
   "can the computer <b>listen</b> to that report and act on it automatically? Yes &mdash; in two moves. "
   "First it <b>transcribes</b> the speech into text. Then it runs the <b>same text analytics</b> you already saw in Notebook 4. "
   "<br><br><b>Speech analytics = speech-to-text + text analytics.</b> Nothing new to fear &mdash; it is two familiar pieces snapped together.")),

md(story(
   "<b>Our scenario.</b> A technician walks up to a machine, presses record on a handheld, and says:<br><br>"
   "<i>\"There is an oil leak near the hydraulic pump and the pressure is dropping.\"</i><br><br>"
   "Nobody types anything. We want the computer to take that <b>audio</b>, figure out the words, and automatically "
   "<b>route</b> the report to the right team &mdash; Electrical, Mechanical, or Hydraulic &mdash; so it lands on the correct desk in seconds. "
   "Here is the whole pipeline we are about to build, end to end:")),

md(PIPELINE),

# ---- Step 1: setup / install --------------------------------------------
md(section("One-time setup (this is the slow cell)", 1)),
md(vocab("Library (a quick reminder)",
   "A <b>library</b> is a ready-made toolbox someone else wrote so we do not start from scratch. "
   "This notebook borrows two new ones: <code>gTTS</code> to <b>make</b> a demo audio clip, and "
   "<code>openai-whisper</code> to <b>listen</b> to audio and turn it into text.")),
md(note("This first cell is the <b>only</b> setup in the entire six-notebook series, and it takes about a minute "
        "as Colab downloads the two tools. A wall of install text scrolling by is completely normal &mdash; wait for it to "
        "finish (the &#9654; spinner stops) before running the next cell.")),
code(
   "# One-time install for Colab. The -q flag just means 'quiet' (less text).\n"
   "# This downloads the two extra tools we need. Give it about a minute.\n"
   "!pip install -q gTTS openai-whisper\n"
   "\n"
   "print('Setup finished. The speech tools are installed and ready.')"),
md(did("Colab just downloaded our two speech tools. From here on it behaves like every other notebook today &mdash; "
       "run cells in order and read the output. That slow step is over.")),

# ---- Step 2: make the demo audio with gTTS -------------------------------
md(section("Make a demo spoken report (no microphone needed)", 2)),
md("To keep this notebook fully self-contained &mdash; no microphones, no uploading files &mdash; we will *manufacture* "
   "a spoken report from a written sentence. The computer reads our sentence aloud and saves it as an audio file. "
   "That file then stands in for a real technician's recording."),
md(vocab("Text-to-speech (TTS)",
   "<b>Text-to-speech</b> turns written words into spoken audio &mdash; the opposite of what we really care about today. "
   "We use it for one small reason only: to <b>fabricate a demo clip</b> so everyone has an identical recording to work with, "
   "with no microphone required. The real star of the notebook is the step <i>after</i> this.")),
code(
   "from gtts import gTTS                 # text-to-speech tool (makes our demo clip)\n"
   "from IPython.display import Audio     # lets us play sound inside the notebook\n"
   "\n"
   "# This written sentence is what we will pretend a technician spoke out loud.\n"
   "spoken_report = 'There is an oil leak near the hydraulic pump and the pressure is dropping.'\n"
   "\n"
   "# Turn that sentence into speech and save it as an audio file named report.mp3\n"
   "gTTS(spoken_report).save('report.mp3')\n"
   "\n"
   "print('Created an audio file: report.mp3')\n"
   "print('It is the spoken version of:')\n"
   "print('   \"' + spoken_report + '\"')"),
code(
   "# Press play on the little audio bar below to HEAR our demo report.\n"
   "Audio('report.mp3')"),
md(did("We just created <code>report.mp3</code> and played it. That audio file is now our <b>stand-in for a real "
       "spoken report</b> &mdash; exactly the kind of clip a technician's handheld would produce. "
       "From the computer's point of view, it has no idea what words are inside; it only has sound. Our job next is to recover the words.")),

# ---- Step 3: transcribe with Whisper -------------------------------------
md(section("Listen to the audio and turn it into text", 3)),
md("This is the genuinely new skill of the notebook: handing raw audio to the computer and getting back the words. "
   "We load a small listening model and ask it to transcribe our clip."),
md(vocab("Speech-to-text / ASR (automatic speech recognition)",
   "<b>Speech-to-text</b> &mdash; also called <b>ASR</b>, automatic speech recognition &mdash; is a model that <b>listens</b> to "
   "audio and writes down the words it hears. It is exactly what your phone does when you dictate a message. "
   "We use a model called <b>Whisper</b>, in its smallest <code>tiny</code> size so it runs quickly here.")),
md(note("The first time you run the next cell, Whisper downloads its <code>tiny</code> model (a few seconds). "
        "It then prints a small warning about running on CPU &mdash; that is harmless and expected on Colab. Just wait for the text.")),
code(
   "import whisper\n"
   "\n"
   "# Load the smallest Whisper model. 'tiny' is fast and fine for short, clear clips.\n"
   "model = whisper.load_model('tiny')\n"
   "\n"
   "# Ask it to listen to our audio file and write down the words.\n"
   "result = model.transcribe('report.mp3')\n"
   "transcript = result['text'].strip()    # the recovered text\n"
   "\n"
   "print('What the computer HEARD (the transcript):')\n"
   "print('   \"' + transcript + '\"')\n"
   "print()\n"
   "print('The original sentence we spoke:')\n"
   "print('   \"' + spoken_report + '\"')"),
md(did("The computer <b>listened to sound and produced text</b> &mdash; and it is (nearly) word-for-word the sentence we spoke. "
       "It was never told the words; it worked them out from the audio alone. That recovered <code>transcript</code> is now "
       "ordinary text, which means we can feed it straight into the text analytics from Notebook 4.")),
md(watchout("ASR is not perfect. With a clear voice and no background noise &mdash; like our demo &mdash; it is excellent. "
            "But strong accents, machine noise on the shop floor, mumbling, or unusual part names can make it <b>mis-hear</b> a word "
            "(\"hydraulic\" might come out as \"high drawlic\"). In the real world you check important transcripts, and a noisy clip "
            "will read less cleanly than this quiet studio-style one. Honest expectations beat magical ones.")),

# ---- Step 4: build the text classifier (self-contained, validated) -------
md(section("How honest is that transcript? Measure it with WER")),
md(vocab("Word Error Rate (WER)",
   "How do we put a number on how well speech-to-text did? <b>WER</b> compares the transcript with a correct reference and counts "
   "three kinds of slip &mdash; <b>wrong</b> words (substitutions), <b>missing</b> words (deletions) and <b>extra</b> words "
   "(insertions) &mdash; divided by the number of reference words. 0% is perfect. It is simply the speech version of the "
   "<i>accuracy</i> idea from the earlier sessions.")),
code(
   "# A tiny, self-contained WER (word-level edit distance). No model or internet needed --\n"
   "# we compare a known-correct sentence against what an ASR system might have heard.\n"
   "def wer(reference, heard):\n"
   "    r, h = reference.lower().split(), heard.lower().split()\n"
   "    d = [[0]*(len(h)+1) for _ in range(len(r)+1)]\n"
   "    for i in range(len(r)+1): d[i][0] = i\n"
   "    for j in range(len(h)+1): d[0][j] = j\n"
   "    for i in range(1, len(r)+1):\n"
   "        for j in range(1, len(h)+1):\n"
   "            cost = 0 if r[i-1] == h[j-1] else 1\n"
   "            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + cost)\n"
   "    return d[-1][-1] / max(1, len(r))\n"
   "\n"
   "reference = 'replace hydraulic actuator part number MS21042 dash four on the main landing gear'\n"
   "heard = {\n"
   "    'clean studio voice':       'replace hydraulic actuator part number MS21042 dash four on the main landing gear',\n"
   "    'some shop-floor noise':    'replace the hydraulic actuator part number MS21042 dash four on main landing gear',\n"
   "    'misheard the part number': 'replace hydraulic actuator part number MS21052 dash four on the main landing gear',\n"
   "}\n"
   "print(f'{\"scenario\":26s} {\"WER\":>6}   part number correct?')\n"
   "for name, said in heard.items():\n"
   "    part_ok = 'MS21042' in said.upper()\n"
   "    print(f'{name:26s} {wer(reference, said)*100:5.1f}%   {\"yes\" if part_ok else \"NO  <-- wrong part!\"}')"),
md(did("Read the three lines. The noisy transcript scores a <b>worse</b> WER (~15%) but every important word survived &mdash; harmless. "
       "The third scores a <b>better</b> WER (~8%) yet quietly turned <b>MS21042</b> into <b>MS21052</b> &mdash; the one word that "
       "matters, now wrong. <b>A low error rate does not mean the transcript is safe.</b>")),
md(watchout("WER weighs every word equally &mdash; mishearing \"the\" counts the same as mishearing a part number, a callsign or a "
            "torque value. So for anything safety- or traceability-critical the rule is simple and non-negotiable: a human verifies the "
            "numbers and serials. Speech-to-text is a fast first draft, not the final record.")),

md(section("When you only need a few words: keyword spotting")),
md(vocab("Keyword spotting",
   "Often you do not need a full transcript &mdash; only to know whether one of a few <b>commands</b> was spoken (\"start log\", "
   "\"flag defect\"). <b>Keyword spotting</b> listens for just a small fixed vocabulary. Because the job is so much narrower, it is far "
   "more <b>robust to noise and accents</b> than open-ended transcription &mdash; the right tool when reliability matters more than detail.")),
code(
   "# Listen for a tiny fixed command vocabulary inside messy, real-world transcripts.\n"
   "COMMANDS = ['start log', 'flag defect', 'pressure low', 'engine fire']\n"
   "\n"
   "noisy_transcripts = [\n"
   "    'uh start log please',                   # command buried in filler\n"
   "    'the the flag defect on number two',     # stutter + extra words\n"
   "    'cabin pressure low warning came on',    # command inside a sentence\n"
   "    'replace the oil filter next service',   # no command at all\n"
   "]\n"
   "for t in noisy_transcripts:\n"
   "    hits = [c for c in COMMANDS if c in t.lower()]\n"
   "    print(f'{t:42s} -> {hits if hits else \"(no command detected)\"}')"),
md(did("Even with stutters, filler words and whole surrounding sentences, the small vocabulary is spotted reliably &mdash; and the line "
       "with no command is correctly left alone. This is why hands-free shop-floor tools lean on a handful of wake-words rather than "
       "full dictation: a 10-word target is dramatically easier to get right than every word a person might say.")),
md(note("<b>Hard by default, strong with domain data.</b> Out of the box, ASR struggles with accents, heavy jargon and radio noise. "
        "But it can be <b>trained on a specific domain</b>: the EU <b>HAAWAII</b> project built speech recognition for air-traffic "
        "control that reached over <b>95%</b> word recognition for controllers and over <b>90%</b> for pilots after domain training, "
        "and about <b>97%</b> on aircraft callsigns once the audio was combined with radar context. Open ATC speech datasets &mdash; "
        "<b>ATCOSIM</b> (clean) and <b>ATCO2</b> (noisy) &mdash; are where teams practise exactly this.")),

md(section("Teach the computer the three teams (text analytics)", 4)),
md("Now we rebuild the Notebook 4 idea, self-contained right here. We give the computer a small set of past spoken-style "
   "reports, each already labelled with the team that handled it. From those examples it learns which words point to which team. "
   "This is the same learn-from-past-examples pattern as every notebook today &mdash; only the data is words instead of numbers."),
md(vocab("Turning words into numbers (TF-IDF)",
   "A model can only do maths on numbers, so first we convert each report into a row of numbers that records <b>which words it "
   "contains</b>. The standard tool for this is <code>TfidfVectorizer</code>. The idea in one line: words that are <b>rare and "
   "distinctive</b> (like \"voltage\" or \"hydraulic\") count for more than common filler words (like \"the\"). "
   "After this step, a sentence is just a row of numbers &mdash; and we already know how to predict from rows of numbers.")),
code(
   "from sklearn.feature_extraction.text import TfidfVectorizer\n"
   "from sklearn.linear_model import LogisticRegression\n"
   "from sklearn.pipeline import make_pipeline\n"
   "\n"
   "# A small set of PAST spoken-style reports, each labelled with the team that owns it.\n"
   "# In real life these would be thousands of historical reports from your logs.\n"
   "reports = [\n"
   "    # --- Electrical ---\n"
   "    'the control panel keeps tripping the circuit breaker',\n"
   "    'there is a burning smell from the wiring near the motor',\n"
   "    'voltage reading is unstable and a fuse blew again',\n"
   "    'the indicator lights are dead, looks like a power supply fault',\n"
   "    'sparks coming from the electrical junction box',\n"
   "    'the battery is not charging and the alternator seems faulty',\n"
   "    'the circuit breaker tripped and the wiring is overheating',\n"
   "    'an electrical short blew the fuse and the panel lost power',\n"
   "    # --- Mechanical ---\n"
   "    'loud grinding noise from the gearbox under load',\n"
   "    'the bearing is worn out and the shaft is vibrating',\n"
   "    'a belt has snapped and the fan is not turning',\n"
   "    'metal fatigue cracks visible on the mounting bracket',\n"
   "    'the rotor is misaligned and rubbing against the casing',\n"
   "    'excessive vibration and a broken coupling on the drive',\n"
   "    'the gearbox is grinding and the shaft bearing is worn',\n"
   "    'a snapped belt and a seized bearing stopped the fan',\n"
   "    # --- Hydraulic ---\n"
   "    'oil leak near the hydraulic pump and pressure is dropping',\n"
   "    'the hydraulic cylinder is slow and losing pressure',\n"
   "    'fluid leaking from a cracked hydraulic hose',\n"
   "    'the pump is not building enough hydraulic pressure',\n"
   "    'a seal has failed and hydraulic fluid is everywhere',\n"
   "    'low oil level in the hydraulic reservoir, valve is sticking',\n"
   "    'the hydraulic hose is leaking oil and pressure keeps dropping',\n"
   "    'oil is leaking from the pump seal and the cylinder lost pressure',\n"
   "]\n"
   "teams = (\n"
   "    ['Electrical'] * 8 +   # first 8 reports are Electrical\n"
   "    ['Mechanical'] * 8 +   # next 8 are Mechanical\n"
   "    ['Hydraulic']  * 8     # last 8 are Hydraulic\n"
   ")\n"
   "\n"
   "print('We have', len(reports), 'past reports across 3 teams:')\n"
   "print('   Electrical, Mechanical, Hydraulic  (8 examples each)')"),
md(did("There is our labelled history: 24 short reports, each tagged with the team that handled it. "
       "Eight examples per team. Small, but enough to show the idea. The computer has not learned anything yet &mdash; "
       "we have only laid out the examples.")),
code(
   "# Snap the two pieces together: words -> numbers (TF-IDF), then a classifier.\n"
   "# make_pipeline just chains them so we can train and predict in one go.\n"
   "classifier = make_pipeline(\n"
   "    TfidfVectorizer(),\n"
   "    LogisticRegression(max_iter=1000),\n"
   ")\n"
   "\n"
   "# Train: the model studies the 18 past reports and learns which words signal which team.\n"
   "classifier.fit(reports, teams)\n"
   "\n"
   "print('Training done. The computer has learned the words for each team.')"),
md(did("One <code>.fit()</code> call &mdash; the same word you saw in Notebook 0 &mdash; and the model has learned which words "
       "lean Electrical, which lean Mechanical, and which lean Hydraulic. It is ready to judge a brand-new report.")),

# ---- Step 5: classify the transcript -------------------------------------
md(section("Route the spoken report automatically", 5)),
md("Here is the payoff. We take the **transcript** from Step 3 &mdash; the text the computer recovered from the audio &mdash; "
   "and ask the trained classifier which team it belongs to. Speech became text; now text becomes a decision."),
code(
   "# Feed the TRANSCRIBED text (from Step 3) into the trained classifier.\n"
   "predicted_team = classifier.predict([transcript])[0]\n"
   "\n"
   "# How confident is it? Show the probability for each team.\n"
   "probs = classifier.predict_proba([transcript])[0]\n"
   "labels = classifier.classes_\n"
   "\n"
   "print('Spoken report (transcribed):')\n"
   "print('   \"' + transcript + '\"')\n"
   "print()\n"
   "print('Routed to team: ', predicted_team)\n"
   "print()\n"
   "print('Confidence per team:')\n"
   "for team, p in sorted(zip(labels, probs), key=lambda kv: -kv[1]):\n"
   "    bar = '#' * int(round(p * 30))    # a little text bar chart\n"
   "    print('   {:<11} {:>4.0f}%  {}'.format(team, p * 100, bar))"),
md(did("The full pipeline just ran end to end: a <b>spoken</b> report became <b>text</b>, and that text was automatically "
       "<b>routed to the Hydraulic team</b> &mdash; with a confidence score to back it. Nobody typed, nobody sorted. "
       "The mention of an oil leak and hydraulic pressure made the answer clear, and the computer saw exactly those words.")),

# ---- Step 6: a second clip to show it generalizes ------------------------
md(section("Try a different report, to prove it is not a fluke", 6)),
md("One example could be luck. Let us speak a *different* report &mdash; an electrical one this time &mdash; and run the whole "
   "pipeline again: make audio, transcribe, route. We bundle the three steps into one small helper so it is easy to reuse."),
code(
   "def route_spoken_report(sentence):\n"
   "    '''Speak the sentence, transcribe it, and route it to a team.'''\n"
   "    # Step A: turn the sentence into audio (our stand-in for a recording).\n"
   "    gTTS(sentence).save('clip.mp3')\n"
   "    # Step B: transcribe the audio back into text.\n"
   "    heard = model.transcribe('clip.mp3')['text'].strip()\n"
   "    # Step C: route the transcribed text to a team.\n"
   "    team = classifier.predict([heard])[0]\n"
   "    confidence = classifier.predict_proba([heard]).max()\n"
   "    print('Spoke      :', sentence)\n"
   "    print('Transcribed:', heard)\n"
   "    print('Routed to  :', team, '  ({:.0f}% confident)'.format(confidence * 100))\n"
   "    return team\n"
   "\n"
   "# A clearly electrical complaint this time.\n"
   "route_spoken_report('The circuit breaker keeps tripping and there is a burning smell from the wiring.')"),
md(did("A completely different spoken sentence ran through the same three steps and landed on the <b>Electrical</b> team. "
       "The words \"circuit breaker\", \"burning smell\", and \"wiring\" pointed there clearly. "
       "The pipeline <code>speak &rarr; transcribe &rarr; route</code> is reusable for any report &mdash; that one helper does it all.")),

# ---- Your turn -----------------------------------------------------------
md(turn(
   "This is the most hands-on moment of the day &mdash; make the computer route <b>your own</b> spoken report.<br><br>"
   "In the cell just above, change the sentence inside <code>route_spoken_report( ... )</code> to anything you like, then press "
   "<b>Shift + Enter</b>. Watch the category change as the words change. A few to try:<br>"
   "1. <code>'The gearbox is making a loud grinding noise and the shaft is vibrating.'</code> &rarr; should route to <b>Mechanical</b>.<br>"
   "2. <code>'A hydraulic hose is leaking fluid and the cylinder has lost pressure.'</code> &rarr; should route to <b>Hydraulic</b>.<br>"
   "3. Write one in your own words. Mix in two teams' worth of clues (say, \"sparks AND an oil leak\") and watch the "
   "confidence split &mdash; that is the computer telling you it is genuinely unsure, which is honest behaviour, not a failure.")),

# ---- Recap for this notebook --------------------------------------------
md(recap("What we learned in Notebook 5", [
   "<b>Speech analytics = speech-to-text + text analytics</b> &mdash; two familiar pieces snapped together.",
   "<b>Text-to-speech</b> only made our demo clip; the real work is <b>speech-to-text (ASR)</b>, which turns audio into words.",
   "Once speech becomes text, it is just text &mdash; so the <b>exact Notebook 4 method</b> classifies it, no new ideas needed.",
   "The showpiece pipeline: <b>speak &rarr; transcribe &rarr; categorize</b>, with a confidence score at the end.",
   "<b>Be honest about ASR:</b> clear speech transcribes beautifully, but accents and shop-floor noise can cause mis-hearings.",
])),

# ---- CLOSING: wrap Session 3, hand off to the Session 4 finale -----------
md(section("Wrapping up Session 3", None)),
md(bigidea(
   "Step back and look at the pipeline you just ran: a <b>spoken</b> report became <b>text</b>, and that text became a "
   "<b>decision</b> &mdash; the very same words-to-numbers method from the text sessions, with one new front end (listening). "
   "And you saw it <b>honestly</b>: speech-to-text is excellent on clear speech and measurable with <b>WER</b>, but a low error "
   "rate can still miss the one word that matters &mdash; which is why a small fixed vocabulary (keyword spotting) is so much more "
   "reliable when the stakes are high, and why critical numbers always get a human's eyes.")),
md(nextup(
   "<b>Session 4 &mdash; predicting from the sound itself.</b> So far the sound only mattered for the <i>words</i> inside it. "
   "Next we throw the words away entirely and ask a bolder question: can a computer <b>hear a failing bearing</b> &mdash; diagnose a "
   "machine fault from its raw sound, the way a seasoned technician can? That is the finale, and it is the same idea one last time: "
   "turn it into numbers, learn the pattern, judge the new case.")),
]

build(cells, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notebooks", "03_speech_analytics.ipynb"),
      title="Predictive AI - Session 3 - Speech I")
