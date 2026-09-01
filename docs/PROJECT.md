# Project

## What it is

AuthentiWrite is a backend service a writing platform can call to get a
second opinion on whether a piece of text was written by a person or by AI.
It gives back a guess, a confidence score, and one of three labels written
in plain English: high-confidence human, unsure, or high-confidence AI. A
writer who disagrees with a label can appeal, which flags the item for a
person to look at instead of letting the automated guess stand.

## Why it exists

Automated AI-detection is unreliable, and most products built on it make
the same mistake of treating a probability score as a verdict. This project
is an attempt to build the same kind of detector honestly: three separate
signals, each with a blind spot that's named and tested, combined into a
score presented as a guess, with a real way for a wrongly accused writer to
push back.

## How it works, in one paragraph

Three signals score a submission independently. A language model measures
how predictable the text is (perplexity). A stylometry check measures the
shape of the writing, its sentence lengths, vocabulary, and punctuation,
without understanding any of the meaning. A pattern check looks for
particular sentence structures that turn up more often in AI copy. A
weighted average turns those three 0-1 scores into one combined score, and
that score maps to a label. Every decision goes into an append-only audit
log, and an appeal adds to that record rather than overwriting it.

## What it's trying to accomplish

Give a platform something useful without pretending it's a verdict, and
give a wrongly flagged writer a real way to push back. Five acceptance
criteria define what working means here. Full targets and results are in
[REQUIREMENTS.md](REQUIREMENTS.md) and [RESEARCH.md](RESEARCH.md):

1. **False positives are rare.** At most 1 in 10 real human writing samples
   gets labelled high-confidence AI, across repeated trials.
2. **AI and human text separate meaningfully.** The average combined score
   for AI-generated text sits far enough above the average for human text
   that the gap reflects real signal rather than noise.
3. **All three labels are reachable.** A service where one label never
   appears has a dead band in its thresholds.
4. **Appeals always work.** Every valid appeal changes the item's status
   and creates a logged record you can check.
5. **Bad input never reaches the model.** Text that's missing, empty,
   malformed, or oversized gets a clear 4xx before any signal runs.

## Non-goals

- **This is not identity verification.** There's no credential and no proof
  of authorship. [DECISIONS.md](DECISIONS.md) explains why per-creator
  reputation was built instead of a "verified human" badge.
- **This is not a moderation platform.** There's no reviewer role and no
  decision queue. An appeal moves an item to `under_review` and stops
  there. A `POST /decide` endpoint would need a real answer to who is
  allowed to decide. Without that it's just a second unauthenticated way to
  overwrite a status, which is worse than the appeal path that already
  exists.
- **This is not trying to beat state-of-the-art AI detection.** The three
  signals are simple and explainable on purpose, so their blind spots can
  be named and reasoned about. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Current status

Everything in scope is built. All three signals are implemented and
calibrated, the appeal path works, rate limiting is on, and the service has
been run against a 56-attack set covering evasion, false positives, prompt
injection, malformed input, and flooding. Results are in
[RESEARCH.md](RESEARCH.md). Several extra endpoints (`/stats`,
`/creator/<id>`, `/submit/batch`, and per-creator reputation) sit on top of
the core service.

One acceptance criterion is still missed: score spread, at 16.6 points
against a 30-point target. That gap is a problem with signal design rather
than tuning. [RESEARCH.md](RESEARCH.md) shows that no reweighting closes it
without breaking the false-positive criterion. The rest of the known
limitations are in [ARCHITECTURE.md](ARCHITECTURE.md).

## Key context for anyone picking this up

- **This is not an identity check.** Nothing here proves who wrote
  anything. It's a probabilistic guess from three imperfect signals, and
  the whole design, meaning the labels, the appeal path, and the
  per-creator notes, is built around treating it as exactly that. See
  [DECISIONS.md](DECISIONS.md).
- **One of the two mistakes costs more than the other.** Wrongly accusing a
  real writer is worse than missing some AI-generated text, and that
  imbalance shaped every threshold and weight in the project.
- **Every signal's blind spot is written down rather than hidden.**
  [ARCHITECTURE.md](ARCHITECTURE.md) covers what each signal measures and
  what it structurally cannot see.
- **The detector model runs locally.** No API key and no hosted call. It's
  a model of about 550MB (`gpt2` by default) loaded into the process.
