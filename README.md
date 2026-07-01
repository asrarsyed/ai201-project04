# Provenance Guard

A backend system that classifies submitted text as likely AI-generated, likely human-written, or uncertain, scores confidence, surfaces a plain-language transparency label, and lets creators appeal a classification.

## Implementation Status

**Design/spec complete; code not yet implemented.** `app.py`, `config.py`, `detection/*.py`, and `production/*.py` are currently empty stub files. Nothing in this repo has been run yet. The full design below — signals, scoring formula, thresholds, label text, rate limits, audit log schema, appeal flow — is specified in detail in [`planning.md`](./planning.md) and is implementation-ready.

Every curl request/response and audit log entry shown below is **illustrative expected output** derived from that spec, not captured from a real run. Each such block is labeled inline. This section exists so no example here is mistaken for demo evidence of working code.

## Architecture Overview

A submission travels: `POST /submit` → Signal 1 (LLM-as-judge via Groq, scores semantic/stylistic AI-likelihood) → Signal 2 (stylometric heuristics, scores structural uniformity) → confidence scorer (weighted combination + disagreement clamp) → label generator (score band → plain-language label) → audit log (structured entry written) → JSON response to caller.

An appeal travels: `POST /appeal` → look up `content_id` → set status to `under_review` → append a linked audit log entry containing the creator's reasoning → confirmation response. Appeals never trigger automatic re-classification; they queue the content for human review. Full diagram in `planning.md` under `## Architecture`.

## Detection Signals

Two independent signals, chosen because one reads meaning and the other reads structure — a text that fools one is unlikely to fool both for the same reason.

**Signal 1 — LLM-as-judge (Groq `llama-3.3-70b-versatile`).** Measures holistic semantic/stylistic coherence: generic phrasing, hedge-heavy transitions, lack of concrete personal detail, overly balanced argument structure. Outputs `J`, a 0-1 probability the text is AI-generated. Misses: a human-edited AI draft, or a human writing in a deliberately generic/formal register, can fool it either direction — it judges style, not actual provenance.

**Signal 2 — Stylometric heuristics (pure Python).** Combines three structural metrics into one 0-1 score `S`: sentence-length variance, type-token ratio (vocabulary diversity), punctuation density. AI text trends toward more uniform sentence lengths, narrower vocabulary at length, and more regular punctuation. Misses: needs roughly 50+ words to be statistically meaningful; also can't tell a human writing in a naturally uniform genre (legal, academic) from actual AI output — it measures uniformity, not authorship.

## Confidence Scoring

```
combined = 0.7 * J + 0.3 * S
```

`J` (LLM signal) is weighted higher as the more semantically discriminating signal; `S` corroborates structurally. **Disagreement clamp:** if `abs(J - S) > 0.4`, `combined` is forced into `[0.35, 0.65]` (the uncertain band) regardless of the weighted average — when an independent semantic signal and an independent structural signal contradict each other, that disagreement is itself the honest answer, not something to average away. This is also how the system avoids confidently mislabeling a human's work as AI-generated when the evidence is actually mixed (a false positive here is worse than a false negative, per the assignment's own framing).

**Thresholds:**

| `combined` score | Attribution |
|---|---|
| `>= 0.70` | Likely AI |
| `0.30 – 0.70` | Uncertain |
| `<= 0.30` | Likely human |

**Validation approach:** thresholds and weights were chosen deliberately (not fit to data, since no labeled dataset exists yet) to guarantee that scores in different bands produce visibly different behavior — a `0.51` and a `0.95` land in different bands entirely, not just different numbers. Planned validation once the code is running (per `planning.md`'s M4 plan): run the four milestone test inputs (clearly AI, clearly human, two borderline cases) and confirm each lands in the expected band; if a borderline case doesn't, inspect `J` and `S` individually to see which signal is misbehaving before trusting the combined score.

**Two illustrative example submissions (expected output, not yet executed):**

High-confidence case — clearly AI-styled input:
```json
// illustrative expected output — not yet executed
{
  "content_id": "c1a2b3c4-...",
  "attribution": "likely_ai",
  "confidence": 0.88,
  "llm_score": 0.91,
  "stylometric_score": 0.80,
  "label": "This content shows strong signs of being AI-generated. Our system found patterns typical of AI writing tools in both the writing style and structure."
}
```

Lower-confidence case — borderline formal human writing:
```json
// illustrative expected output — not yet executed
{
  "content_id": "d5e6f7a8-...",
  "attribution": "uncertain",
  "confidence": 0.58,
  "llm_score": 0.72,
  "stylometric_score": 0.31,
  "label": "We couldn't confidently tell whether this was AI-generated or human-written. The signals were mixed or inconclusive — treat this result with caution, not as a verdict."
}
```

Note the second example: `J` and `S` differ by 0.41 (> 0.4), so the disagreement clamp pulls `combined` into the uncertain band even though the raw weighted average (`0.7*0.72 + 0.3*0.31 = 0.60`) would already have landed there anyway in this case — illustrating the clamp's effect on a case where the two signals genuinely disagree.

## Transparency Label

Displayed to the reader; plain language only, no jargon like "classifier output" or "logit score."

| Attribution | Exact label text |
|---|---|
| High-confidence AI | "This content shows strong signs of being AI-generated. Our system found patterns typical of AI writing tools in both the writing style and structure." |
| Uncertain | "We couldn't confidently tell whether this was AI-generated or human-written. The signals were mixed or inconclusive — treat this result with caution, not as a verdict." |
| High-confidence human | "This content shows strong signs of human authorship. Our system found the natural variation and personal voice typical of human writing." |

## Appeals Workflow

`POST /appeal` accepts `content_id` + `creator_reasoning`. On receipt: looks up the content record, sets `status` to `under_review`, appends a new audit log entry linked to the original classification containing the creator's reasoning, and returns a confirmation. No automatic re-classification — a human reviewer is expected to compare the appeal against the original decision.

```json
// illustrative expected output — not yet executed
// POST /appeal {"content_id": "d5e6f7a8-...", "creator_reasoning": "I wrote this myself; I'm a non-native English speaker and my writing style tends to be more formal."}
{
  "content_id": "d5e6f7a8-...",
  "status": "under_review",
  "timestamp": "2026-07-01T14:32:10.123Z",
  "message": "Appeal received and logged for review."
}
```

## Rate Limiting

`10 per minute; 100 per day`, per IP, via Flask-Limiter with in-memory storage. Reasoning: a writer actively revising a draft realistically resubmits a handful of times in a focused session — 10/minute comfortably covers that burst while blocking a script hammering the endpoint. 100/day comfortably covers even a very prolific editing day across multiple pieces, while still bounding total load from any single source. Both numbers are deliberately generous to legitimate single-creator usage and tight against automated flooding.

Expected behavior once implemented (illustrative, not yet executed): the first 10 requests in a minute return `200`, the 11th+ return `429` until the window resets.

## Audit Log

Structured JSONL, one entry per submission or appeal. Submission entries: `content_id, creator_id, timestamp, attribution, confidence, llm_score, stylometric_score, status`. Appeal entries add `appeal_reasoning` and set `status` to `under_review`, linked to the original entry by `content_id`.

```json
// illustrative sample log — not yet executed
{"content_id": "c1a2b3c4-...", "creator_id": "user-1", "timestamp": "2026-07-01T14:20:01.000Z", "attribution": "likely_ai", "confidence": 0.88, "llm_score": 0.91, "stylometric_score": 0.80, "status": "classified"}
{"content_id": "d5e6f7a8-...", "creator_id": "user-2", "timestamp": "2026-07-01T14:25:44.000Z", "attribution": "uncertain", "confidence": 0.58, "llm_score": 0.72, "stylometric_score": 0.31, "status": "classified"}
{"content_id": "e9f0a1b2-...", "creator_id": "user-3", "timestamp": "2026-07-01T14:28:12.000Z", "attribution": "likely_human", "confidence": 0.14, "llm_score": 0.10, "stylometric_score": 0.22, "status": "classified"}
{"content_id": "d5e6f7a8-...", "creator_id": "user-2", "timestamp": "2026-07-01T14:32:10.123Z", "status": "under_review", "appeal_reasoning": "I wrote this myself; I'm a non-native English speaker and my writing style tends to be more formal."}
```

The fourth entry is the appeal for `d5e6f7a8-...`, shown alongside its original classification entry — the pairing a human reviewer would need.

## Known Limitations

Formal or academic human writing (and non-native-English human writing in a careful register) is the type of content this system would most likely misclassify. Both signals key on features that formal prose naturally has: the LLM judge associates hedge-heavy transition language ("it is important to note," "furthermore") and balanced argument structure with AI output, and the stylometric signal associates low sentence-length variance and consistent punctuation with AI output. A human writing carefully in this register can trigger both signals simultaneously, which the disagreement clamp cannot catch (it only helps when the signals *disagree*). This is a direct consequence of what the signals measure, not a generic "needs more data" caveat — it's the same failure mode the appeals workflow exists to catch.

## Spec Reflection

Writing the uncertainty section of `planning.md` before any code forced a concrete answer to "what does a 0.6 mean" — the disagreement clamp only exists because I had to specify, in writing, how the system should behave when the two signals contradict each other, rather than only when they agree. That's a design decision I likely would have skipped if I'd started from the scoring code first and worked backward.

Where implementation is expected to diverge once built: the spec fixes `combined = 0.7*J + 0.3*S` and the `0.4` disagreement threshold as static constants, but these are judgment calls made without any labeled data. Once real test inputs are run (per the M4 plan), I expect the actual weights or the `0.4` disagreement threshold to need adjustment if the four milestone test cases don't land in their expected bands — the spec is a starting calibration, not a guarantee.

## AI Usage

**Instance 1 (this session, real):** Directed Claude Code to read the assignment and grading rubric, then draft the full `planning.md` and `README.md` structure and content against them. Iterated live on several design decisions rather than accepting the first draft: changed the signal weighting from an initial 0.6/0.4 split to 0.7/0.3 for `J`/`S`; added the disagreement-clamp mechanism (not in the first draft) specifically to give a concrete, defensible answer to the false-positive-asymmetry hint in the assignment; kept the label-text wording it proposed but reviewed it against the "plain language, no jargon" requirement before accepting it; and explicitly decided against an asymmetric-threshold design it could have proposed, in favor of the single disagreement-clamp mechanism, since a second arbitrary threshold gap wasn't defensible without data.

**Instance 2 (planned, not yet executed):** Per the `## AI Tool Plan` in `planning.md`, Milestone 3 will hand the AI tool the Detection Signals section plus the architecture diagram and ask it to generate the Flask app skeleton and the Signal 1 (Groq) function. Planned verification: call the generated signal function directly on 2-3 hand-picked inputs before wiring it into the route, and check the route's request/response shape against the API contract in `planning.md` rather than accepting it as-is.
