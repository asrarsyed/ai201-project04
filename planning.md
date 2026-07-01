# Provenance Guard — Planning

## Overview

Provenance Guard classifies submitted text as likely AI-generated, likely human-written, or uncertain, and returns a confidence score plus a plain-language transparency label. Creators can appeal a classification; every decision and appeal is written to a structured audit log.

**Path a submission takes, start to finish:**

1. Creator submits `text` + `creator_id` to `POST /submit`.
2. Signal 1 (LLM-as-judge, Groq) scores the text: `J` = P(AI-generated), 0-1.
3. Signal 2 (stylometric heuristics) scores the text: `S` = P(AI-generated), 0-1.
4. Scorer combines `J` and `S` into one `confidence` score (see Uncertainty Representation).
5. Confidence maps to an `attribution` (`likely_ai` / `uncertain` / `likely_human`) and a transparency `label` string.
6. A structured entry (content_id, both signal scores, combined confidence, attribution, timestamp) is appended to the audit log.
7. Response returns `content_id`, `attribution`, `confidence`, `label` to the creator/platform.

If a creator disputes the result, `POST /appeal` with the `content_id` and their reasoning updates that content's status to `under_review` and appends a linked audit log entry — no re-classification happens automatically.

## Detection Signals

**Signal 1 — LLM-as-judge (Groq `llama-3.3-70b-versatile`).**
Measures: holistic semantic and stylistic coherence — does the text read like something a language model would produce (generic phrasing, hedge-heavy transitions, lack of concrete personal detail, overly balanced "on one hand / on the other" structure)?
Output: `J`, a float 0-1, the model's estimated probability the text is AI-generated (prompted to return a structured probability, not a bare label).
Blind spot: an AI draft that's been meaningfully human-edited, or a human deliberately writing in a generic/formal register (e.g. a cover letter), can both fool this signal in either direction. It judges *style*, not provenance — it has no ground truth about who actually typed the words.

**Signal 2 — Stylometric heuristics (pure Python, no external libraries).**
Measures: structural/statistical uniformity across three metrics, combined into one score:
- Sentence-length variance (AI text trends toward more uniform sentence lengths).
- Type-token ratio / TTR (vocabulary diversity; AI text often re-uses a narrower vocabulary at length).
- Punctuation density (AI text tends toward more regular, "correct" punctuation patterns; human text is burstier).

Output: `S`, a float 0-1, computed by normalizing each metric and averaging (low variance + low TTR + high punctuation regularity → higher `S`).
Blind spot: needs enough text to be meaningful — under roughly 50 words, variance and TTR are noisy and not statistically reliable. It also can't distinguish a human writing in a naturally uniform/formal genre (legal, academic) from actual AI output; it measures *uniformity*, not *authorship*.

**Why these two:** they are genuinely independent. `J` is semantic (what is being said and how it's phrased); `S` is structural (measurable statistical shape of the text, blind to meaning). A text that fools one is unlikely to fool both for the same reason, which is why disagreement between them is itself informative (see below).

## Uncertainty Representation

Both signals are normalized to `[0, 1]`, each representing "probability this text is AI-generated." Combined score:

```
combined = 0.7 * J + 0.3 * S
```

`J` is weighted higher because it captures semantic content and is generally more discriminating; `S` acts as a corroborating structural check rather than an equal vote.

**Disagreement clamp.** If `abs(J - S) > 0.4`, the two signals substantially disagree. In that case `combined` is clamped into `[0.35, 0.65]` (the uncertain band) regardless of what the raw weighted average says. Rationale: an independent semantic signal and an independent structural signal contradicting each other is itself evidence the system doesn't actually know — it should not report high confidence just because one outlier signal pulled the weighted average past a threshold. This is also how the system encodes the assignment's stated asymmetry: a false positive (calling a human's work AI-generated) is worse than a false negative, so when signals disagree, the system defaults to "uncertain" rather than confidently accusing.

**Thresholds** (symmetric — considered widening the gap on the AI side specifically, but decided the disagreement clamp above is the one well-justified asymmetry mechanism; stacking a second arbitrary threshold gap isn't defensible without real calibration data):

| `combined` score | Attribution | Label shown |
|---|---|---|
| `>= 0.70` | `likely_ai` | High-confidence AI |
| `0.30 – 0.70` (exclusive) | `uncertain` | Uncertain |
| `<= 0.30` | `likely_human` | High-confidence human |

A `0.51` and a `0.95` therefore land in different bands entirely (uncertain vs. high-confidence AI) and get visibly different label text, not just a different number — satisfying the "0.51 should look meaningfully different from 0.95" requirement.

## Transparency Label Design

Displayed text must be plain language, no jargon ("classifier," "logit," "signal score" never appear to the end user), and must visibly differ by band.

| Attribution | Exact label text |
|---|---|
| High-confidence AI (`likely_ai`) | "This content shows strong signs of being AI-generated. Our system found patterns typical of AI writing tools in both the writing style and structure." |
| Uncertain | "We couldn't confidently tell whether this was AI-generated or human-written. The signals were mixed or inconclusive — treat this result with caution, not as a verdict." |
| High-confidence human (`likely_human`) | "This content shows strong signs of human authorship. Our system found the natural variation and personal voice typical of human writing." |

## Appeals Workflow

- **Who:** the original creator (`creator_id` on the submission), identified by supplying the `content_id` they received back from `/submit`.
- **What they provide:** `content_id` + free-text `creator_reasoning` explaining why they believe the classification is wrong.
- **What the system does on `POST /appeal`:**
  1. Looks up the stored content record by `content_id`.
  2. Sets its `status` to `under_review`.
  3. Appends a new audit log entry linked to the original `content_id`, containing the `creator_reasoning` and a reference to the original classification (attribution, confidence, signal scores).
  4. Returns a confirmation response (`content_id`, new `status`, timestamp) to the creator.
- **No automated re-classification** — a human reviewer is expected to look at the appeal queue later.
- **What a human reviewer would see:** for each `under_review` item, the original text, original `attribution`/`confidence`/signal breakdown, and the creator's `creator_reasoning`, side by side — everything needed to make a manual call without re-running detection.

## Anticipated Edge Cases

1. **Short-form content (haiku, tweet-length, under ~50 words).** Stylometric metrics (sentence-length variance, TTR) need enough tokens to be statistically meaningful; on very short text they're mostly noise. The combined score effectively collapses to just the LLM signal, undermining the multi-signal design for exactly the content type (very short creative pieces) this system is meant to help.

2. **Formal/academic or non-native-English human writing.** Literature-review-style prose naturally has low sentence-length variance and heavy use of hedging/transition language ("it is important to note," "furthermore") — the same surface features the LLM judge and the stylometric heuristics both associate with AI generation. A human writing carefully in a formal register, especially a non-native speaker, is at elevated risk of a false "likely_ai" result — precisely the false-positive case the system is designed to avoid confidently asserting (see disagreement clamp), but a false positive is still possible if both signals happen to agree on this genre's surface features.

## Architecture

```
                         SUBMISSION FLOW
                         ---------------
   creator
     |  POST /submit {text, creator_id}
     v
 +-----------+     raw text      +------------------+
 |  Flask    | ----------------> | Signal 1:        |
 |  /submit  |                   | LLM-as-judge      |
 |  route    |                   | (Groq)  -> J      |
 +-----------+                   +------------------+
     |    \                              |
     |     \  raw text                   | J (0-1)
     |      v                            v
     |  +------------------+     +------------------+
     |  | Signal 2:        |     |                  |
     |  | Stylometrics     |---->|  Scorer:         |
     |  | (pure Python)    |  S  |  combined =      |
     |  | -> S             |     |  0.7J + 0.3S     |
     |  +------------------+     |  (+ disagreement |
     |                           |    clamp)        |
     |                           +------------------+
     |                                    |
     |                                    | combined score
     |                                    v
     |                           +------------------+
     |                           | Label generator: |
     |                           | score -> band ->  |
     |                           | attribution +     |
     |                           | label text        |
     |                           +------------------+
     |                                    |
     |     content_id, attribution,       |
     |     confidence, J, S, label        |
     v                                    v
 +----------------------------------------------------+
 |  Audit Log (append entry: content_id, creator_id,   |
 |  timestamp, attribution, confidence, J, S, status)  |
 +----------------------------------------------------+
     |
     v
 response {content_id, attribution, confidence, label}
     |
     v
   creator


                          APPEAL FLOW
                          -----------
   creator
     |  POST /appeal {content_id, creator_reasoning}
     v
 +-----------+
 |  Flask    |
 |  /appeal  |
 |  route    |
 +-----------+
     |  1. look up content_id
     |  2. set status = "under_review"
     v
 +----------------------------------------------------+
 |  Audit Log (append entry: content_id,               |
 |  appeal_reasoning, status=under_review,             |
 |  linked to original classification entry)           |
 +----------------------------------------------------+
     |
     v
 response {content_id, status: "under_review", timestamp}
     |
     v
   creator
```

**Narrative:** The submission flow runs raw text through two independent signals in parallel (LLM-as-judge for semantic style, stylometrics for structural uniformity), combines their scores into one calibrated confidence value, derives an attribution band and matching plain-language label from that score, logs the full decision, and returns the label to the creator. The appeal flow is deliberately simpler and decoupled from detection: it never re-scores the content, it only updates status and appends the creator's reasoning to the same audit log, linked by `content_id`, so a human reviewer can compare the original decision against the appeal later.

## AI Tool Plan

**M3 (submission endpoint + first signal):**
- Spec sections provided to the AI tool: Detection Signals (Signal 1 description) + the Architecture diagram above.
- What I'll ask for: a Flask app skeleton with the `POST /submit` route stub, and the Signal 1 (Groq LLM-as-judge) function in isolation.
- Verification: call the signal function directly with 2-3 hand-picked inputs (clearly AI, clearly human) before wiring it into the route; confirm the route accepts `text` + `creator_id` JSON and returns `content_id` even before real scoring is wired in.

**M4 (second signal + confidence scoring):**
- Spec sections provided: Detection Signals (Signal 2) + Uncertainty Representation (weights, disagreement clamp, thresholds) + the Architecture diagram.
- What I'll ask for: the stylometric signal function (sentence-length variance, TTR, punctuation density → single `S` score), and the scorer function implementing `combined = 0.7*J + 0.3*S` with the disagreement clamp.
- Verification: run the 4 milestone test inputs (clearly AI, clearly human, 2 borderline) and confirm scores fall in the bands this document specifies — not just "look reasonable." If the generated clamp logic doesn't match `abs(J-S) > 0.4 -> clamp to [0.35, 0.65]` exactly, correct it before integrating.

**M5 (production layer):**
- Spec sections provided: Transparency Label Design (exact 3 strings) + Appeals Workflow + the Architecture diagram.
- What I'll ask for: a label-generation function mapping `combined` score to the exact attribution + label text above, and the `POST /appeal` route.
- Verification: force all three score bands (via test inputs or direct function calls) and confirm the exact label strings match this document verbatim; submit a test appeal and confirm status flips to `under_review` and the audit log shows both the original entry and the linked appeal entry.
