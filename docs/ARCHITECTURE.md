# Architecture

## Layout

```
src/authentiwrite/
  app.py          Flask routes: /submit, /appeal, /log, /health, and more
  config.py       Every tunable setting: weights, thresholds, rate limits, paths
  detector.py     Signal one, the model signal (language model perplexity)
  stylometry.py   Signal two, the style signal (sentence shape, vocabulary, punctuation)
  phrasing.py     Signal three, the pattern signal (sentence structures common in AI copy)
  scoring.py      combine_signals() and score_to_label()
  audit.py        Append-only audit log (logs/audit.jsonl)
  creators.py     Per-creator reputation tally (logs/creators.json)
  scenarios.py    Test data for scripts/run_eval.py

scripts/
  run_attacks.py  Sends attack_set/*.csv against a running service
  run_eval.py     Runs the acceptance criteria in REQUIREMENTS.md, three trials each

tests/
  conftest.py           Fixtures: isolated log dirs, stubbed signals, limiter reset
  test_scoring.py       The combining rule and the labelling rule
  test_signals.py       The style and pattern signals
  test_model_signal.py  The model signal's curve, with perplexity stubbed
  test_routes.py        Validation, scoring, appeals, and the read endpoints
  test_storage.py       The audit log and the reputation tally
  test_rate_limit.py    The limiter, tripped on purpose
  test_environment.py   Environment and dependency check, run by hand

attack_set/       CSV attack definitions (evasion, false positive, prompt injection, malformed)
logs/             audit.jsonl and creators.json, written at runtime, not tracked
results/          Attack and evaluation reports, written at runtime, not tracked
```

`logs/` and `results/` are gitignored because they're output rather than
source. Their structure is described below. The findings that came out of
them are written up in [RESEARCH.md](RESEARCH.md) instead of keeping the raw
files in the repository.

## Request flow

One submission, start to finish:

1. **A writer submits text.** `POST /submit` with `text` and `creator_id`.
   That's the only way in.
2. **The route checks the input.** A body that isn't a JSON object, text
   that's missing, empty, too short, or too long, and a `creator_id` that
   isn't a string all get rejected here, before any signal runs. The
   rejection is logged.
3. **Signal one reads for predictability.** `detector.py` runs a language
   model and scores how surprised it is by the text (perplexity).
4. **Signal two reads shape.** `stylometry.py` measures sentence-length
   spread, vocabulary repetition, and punctuation density, with no
   understanding of the meaning at all.
5. **Signal three reads sentence structure.** `phrasing.py` looks for
   contrastive pairs and runs of short fragments.
6. **The three signals combine.** `scoring.py::combine_signals` turns them
   into one 0-1 score with a weighted average. See
   [DECISIONS.md](DECISIONS.md) for the weights and the reasoning.
7. **The score becomes a label.** `scoring.py::score_to_label` maps the
   number onto one of three fixed labels using the thresholds in
   `config.py`.
8. **The decision is logged and returned.** `audit.py` writes the whole
   decision to the log, meaning all three signal scores, the combined
   score, and the label. The same data comes back as JSON.
9. **An appeal doesn't re-score anything.** `POST /appeal` marks the item
   `under_review` and adds a new log entry. The original decision entry is
   never edited, only appended after.

## The three signals and their blind spots

Every signal here is simple and explainable on purpose, so its blind spot
can be named and reasoned about instead of disappearing inside a model
nobody can inspect. All three point the same way, where a higher score
means more likely AI.

### Signal one, the model signal (`detector.py`)

**What it measures:** perplexity, meaning how predictable the text is to a
language model (`gpt2` by default).

**Why human and AI text might differ:** a language model writes by picking
a likely next word over and over, so its output tends to be predictable to
another model. Human writing wanders more.

**Blind spot:** being predictable is not the same as being machine
written. This signal treats common words in short, ordinary sentences as
machine-like, which catches plain writers and people writing in a second
language who stick to safe vocabulary. It does the reverse too, reading
dense rare-word prose as human even when AI wrote it. Of the three, this is
the one most likely to accuse the writers with the least room to argue
back.

### Signal two, the style signal (`stylometry.py`)

**What it measures:** sentence-length spread, type-token ratio (how much
vocabulary repeats), and punctuation density. The shape of the text rather
than what it says.

**Why human and AI text might differ:** generated prose tends toward even,
mid-length sentences and a narrower vocabulary. Human writing is lumpier.

**Blind spot:** it cannot read. Anything that changes the shape without
changing the substance moves the score. Typos do it, so do broken-up
sentences and a pasted quotation, and all of those are cheap to do on
purpose.

### Signal three, the pattern signal (`phrasing.py`)

**What it measures:** particular sentence structures that show up in
AI-written copy. Contrastive pairs ("it's not about X, it's about Y") and
runs of short declarative fragments ("Focused. Aligned. Measurable.").

**Why human and AI text might differ:** these are persuasive devices a
language model reaches for often when writing confident-sounding copy.
Somebody writing plainly rarely builds one by accident.

**Blind spot:** it only works in one register, and stays silent on almost
anything outside B2B, marketing, and opinion writing. The fragment-run half
can also fire on a real writer's deliberate style. Like the others it's
cheap to defeat on purpose, since longer, non-parallel sentences remove
every trigger.

## Runtime data

Nothing under `logs/` or `results/` is tracked in git. Both directories get
created on first use (`config.LOG_DIR.mkdir(...)`) and rebuilt by running
the service and the scripts in `scripts/`. Here's what's in them.

### `logs/audit.jsonl`, the audit log

Append-only, one JSON object per line, written by `audit.py`. A decision
always carries the same nine core fields (timestamp, content_id,
creator_id, guess, model_score, style_score, combined_score, label, status)
plus `pattern_score`, so decisions written from different code paths can be
compared directly. Appeals and rejections carry the identifying fields and
add their own `event`:

```json
{"timestamp": "2026-08-31T23:42:29+00:00", "content_id": "e9361d27-...",
 "creator_id": "asrar", "guess": "unsure", "model_score": 0.5319,
 "style_score": 0.5208, "combined_score": 0.4477,
 "label": "We can't tell whether this was written by a person or by AI. ...",
 "status": "decided", "pattern_score": 0.0}
```

An appeal is a *new* entry (`event: "appeal"`, `status: "under_review"`),
never an edit to the original, so the record of what was first decided
survives any challenge to it. A rejection (`event: "rejected"`) gets logged
the same way, so a flood of blocked requests leaves a trace instead of
silence. `audit.read_entries()` is the only reader, and it skips a line it
can't parse rather than raising, so one corrupt row can't take down the
whole log.

### `logs/creators.json`, per-creator reputation

One JSON object rather than a log. This holds current state instead of a
history, so it's a plain dict rather than a file that grows. It's keyed by
`creator_id`, and each value is three counters:

```json
{"asrar": {"ai_count": 0, "human_count": 1, "unsure_count": 2}}
```

`creators.py` reads and writes it behind the same `threading.Lock` pattern
the audit log uses. Every update rewrites the whole file, reading it,
changing it, and writing it back. That's fine at this project's size and
the wrong approach for heavy write traffic or multiple processes.

### `results/*.md`

Reports meant for people to read, written by `scripts/run_attacks.py` and
`scripts/run_eval.py`. One Markdown file per run, timestamped, named
`attack_run_<date>_<label>.md`, `run_<date>_<label>.md`, or
`flood_<date>.md`. Each has a summary table plus the raw JSON that came
back for every request in the run. These are the documents behind the
numbers quoted in [RESEARCH.md](RESEARCH.md), and re-running the scripts
regenerates them.

## Known limitations

### The score-spread gap

This is the one acceptance criterion still missed. AI and human samples
separate by 16.6 points against a 30-point target.
[RESEARCH.md](RESEARCH.md) shows this isn't a tuning problem: every
weighting was tried against the calibration set, and none of them reaches
30 points without creating a false positive. Closing it needs a fourth
signal that separates plain, well-formed, informational prose better than
any of the current three manage alone. That's worth a second calibration
pass with a bigger and more varied AI sample set first, since 5 AI samples
from one prompt is a thin basis for designing a new signal.

### A false positive that's being kept on purpose

FP05, which is real technical documentation, scores `ai` and shouldn't. It
is the measured cost of giving the model signal more weight, and
[DECISIONS.md](DECISIONS.md) covers that decision. Three evasion attacks
(EV01, EV05, EV08) also still get through, all by the same mechanism:
typos, heavy editing, and short text all leave the style signal sitting
near its neutral midpoint. Both problems are the same lever pulling in
opposite directions.

The people who pay for this particular trade are writers of dense, plain,
technical prose. That's a real and identifiable group, not a vague one, and
they now have a higher chance of landing on "unsure" or worse. That cost is
worth stating plainly rather than reversing, because the alternative was
worse on the thing that matters most: letting AI text through purely
because it happened to be shaped in an ordinary way.

### Scale and deployment

- **No index on the audit log.** `/stats` and `/creator/<id>` scan the
  whole log on every request. That's fine at hundreds or low thousands of
  entries and the wrong design past that.
- **Rate-limit counters live in memory.** They reset on restart and aren't
  shared between running instances. Storage that survives a restart is
  needed the moment this runs as more than one process.
- **The detector model has to fit in the process.** Running this on a
  typical free-tier host doesn't work. `torch` plus the loaded model
  weights go past a 512MB memory budget before a single request arrives,
  and without a persistent disk the 550MB download repeats every time the
  host spins down. This service wants a host with real memory and a real
  disk, not a serverless or free tier.
