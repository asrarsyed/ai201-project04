# Research

What came out of calibration, the attack set, and the acceptance-criteria
runs. The raw output lives in `results/`. This file is the analysis.

## A note on the calibration set

The 10 "own writing" samples used in the false-positive and score-spread
criteria are real human writing taken from the public
[allenai/c4](https://huggingface.co/datasets/allenai/c4) dataset. They
weren't written by hand for this project. That's recorded here rather than
swapped in quietly. See `src/authentiwrite/scenarios.py`.

## Acceptance criteria, before the reweight

Full output: `results/run_2026-08-31_1810_before.md`.

| Criterion | Target | Result | Verdict |
|---|---|---|---|
| 1. False positives | 1 of 10 or fewer | 0 of 10, all three trials | MET |
| 2. Score spread | 30 points or more | 11.4 points, all three trials | **MISSED** |
| 3. Label coverage | 3 of 3 | 2 of 3, no `ai` | **MISSED** |
| 4. Appeal path | 5 of 5 | 5 of 5 | MET |
| 5. Bad input | 4 of 4 | 3 of 4 | **MISSED** |

**Criteria 2 and 3 turned out to be one problem, not two.** The 5
AI-generated paragraphs scored high on the model signal, 0.84 to 0.91,
meaning genuinely predictable. But they landed right at the style signal's
neutral midpoint, 0.42 to 0.48, because they had ordinary sentence variety
and ordinary vocabulary. At the 0.55 style weight in force at the time,
that neutral reading on its own held every combined score under 0.55. All 5
AI samples came back "unsure" in every trial. This is a problem with the
combining rule: any AI text whose *shape* looks ordinary gets its strong
model-signal evidence watered down by a style signal that has nothing to
say about it.

**Criterion 5 was a validation gap.** `_validate_text` in `app.py` checked
that `text` was a string of at least 3 words and had no upper limit at all.
A 50,000-word body went straight through validation and paid the full cost
of both signals, which is exactly the failure Criterion 5 exists to catch.

## Attack run, before the reweight

Full run: `results/attack_run_2026-08-31_1726_before.md`, 56 attacks.

**Result: 50 held, 6 broke** (EV01, EV05, EV06, EV08, MF08, RQ06), plus
RQ07 auto-marked because of an unhandled 500.

| Family | Broke / Total |
|---|---|
| evasion | 4 / 10 |
| false_positive (by the letter of the criterion) | 0 / 8 |
| malformed | 2 / 20, plus 1 auto-marked |
| prompt_injection | 0 / 6 |
| flood | 0 / 12 |

**EV01, EV05, EV06, and EV08 all failed by the same mechanism as Criteria
2 and 3.** Typos (EV01) and heavy editing (EV05) raise word variety, which
the style signal reads as more human, cancelling out an otherwise strong
model-signal reading. Extreme sentence lengths (EV06) and short text (EV08)
leave the style signal with even less to measure. All four are the same
failure as the criteria miss above: the style signal sitting near 0.5 on
plain prose was enough, at a 0.55 weight, to keep a high model score out of
the "ai" band by itself.

**MF08 and RQ07 failed at the same stage for different reasons.** MF08, at
60,000 characters, went through the missing upper limit in
`_validate_text`, exactly like the Criterion 5 miss. RQ07, a JSON array
body, crashed earlier. `request.get_json(silent=True) or {}` happily
returns a list for an array body, and the rate-limiter key function called
`.get()` on it without checking. A list has no `.get()`, so that raised an
AttributeError nothing caught, before validation ever ran.

**RQ06 was the quietest failure.** A `creator_id` sent as a JSON object,
`{"id": "x"}`, rather than a string. The route accepted it, scored it
normally, and wrote the raw object into `creator_id` in the audit log. Both
`GET /creator/<id>` and `creators.record_guess()` expect a string key, so
that submission's reputation history became permanently unreachable by any
ordinary lookup. No error, no 4xx, just a writer whose record was filed
somewhere they could never find it.

**A soft failure worth naming (FP01 to FP07).** None of the 8
false-positive attacks were ever called `ai`, so technically they all pass.
But 7 of the 8 came back "unsure" rather than "human", meaning real,
unremarkable human writing was told "we can't tell". That isn't a broken
attack by the letter of the criterion. It is a sign that Criterion 1's
0-of-10 pass was partly a symptom of the same imbalance causing Criterion
2's miss, rather than proof the false-positive control was well tuned.

## The fix: reweighting the combining rule

**The change:** `WEIGHT_MODEL_SIGNAL` from 0.30 to 0.45,
`WEIGHT_STYLE_SIGNAL` from 0.55 to 0.40, `WEIGHT_PATTERN_SIGNAL` left alone
at 0.15. One change, nothing else touched. The full reasoning is in
[DECISIONS.md](DECISIONS.md).

Before settling on 0.45 and 0.40, every weighting was tried against the
real signal scores from the 15-sample calibration set. No weighting clears
the 30-point Criterion 2 target without also creating a false positive on
that data. 0.45/0.40 was the highest model weight that kept Criterion 1 at
0 of 10.

### Attack run, after

Full run: `results/attack_run_2026-08-31_1817_after.md`.

| ID | Before | After | Changed? |
|---|---|---|---|
| EV01 | human (0.311) | human (0.472) | no, still BROKE, but closer to the line |
| EV05 | human (0.343) | human (0.352) | no, still BROKE |
| EV06 | human (0.309) | unsure (0.285) | **yes, fixed** |
| EV08 | human (0.284) | human (0.474) | no, still BROKE, but closer to the line |
| FP05 | unsure (0.055) | **ai (0.139)** | **yes, newly BROKE** |
| MF08 | ai (0.655) | ai (0.411) | no, held both times |

### Criteria, after

| Criterion | Before | After | Verdict |
|---|---|---|---|
| 1. False positives | 0 of 10 | 0 of 10 | MET, unchanged |
| 2. Score spread | 11.4 points | 16.6 points | **still MISSED** |
| 3. Label coverage | 2 of 3 | **3 of 3** | **MET** |
| 4. Appeal path | 5 of 5 | 5 of 5 | MET, unchanged |
| 5. Bad input | 3 of 4 | 3 of 4 | still missed at this point, fixed later, see below |

```json
{"human_avg": 0.4133, "ai_avg": 0.5790, "gap_points": 16.57}
```

**Did it help?** Partly, and the cost was measured rather than assumed. It
fixed label coverage, so `ai` is now reachable and all 5 AI calibration
samples correctly come out above 0.55, and it closed one evasion attack
(EV06). It did not close the score-spread gap, and the sweep above already
showed no weighting on its own reaches 30 points without breaking Criterion
1. It also introduced one new false positive. FP05, which is real technical
documentation, flipped from a correct "unsure" to a wrong "ai". That is the
direct cost of giving more weight to the model signal's own blind spot,
where plain information-dense prose reads as predictable.
[ARCHITECTURE.md](ARCHITECTURE.md) explains why that trade was kept.

## Hardening the route stage

The three attacks that broke for reasons having nothing to do with the
signals, MF08, RQ06 and RQ07, all failed at the same stage: what the route
accepts before any scoring happens. All three are now fixed and the set has
been re-run.

Full run: `results/attack_run_2026-08-31_1947_postfix.md`, with the
criteria in `results/run_2026-08-31_1948_postfix.md`.

| ID | Was | Now | Fix |
|---|---|---|---|
| RQ07 (JSON array body) | **500**, unhandled `AttributeError` | 400 | `_json_object()` rejects any body that isn't a JSON object, in every route |
| RQ06 (`creator_id` as an object) | 200, record quietly orphaned | 400 | `_validate_creator_id()` checks its type the same way `text` gets checked |
| MF08 (57,640 characters) | 200, paid the full cost of every signal | 400 | `config.MAX_TEXT_CHARS` (25,000) enforced in `_validate_text()` |

**Attack set: 53 held, 3 broke, 0 auto-marked.** Re-running the full 56
confirmed that exactly those three rows changed and nothing else moved. The
remaining three are EV01, EV05 and EV08, the evasion attacks that come from
signal design rather than validation.

| Criterion | Before | Now | Verdict |
|---|---|---|---|
| 1. False positives | 0 of 10 | 0 of 10 | MET |
| 2. Score spread | 16.6 points | 16.6 points | **still MISSED**, unchanged as expected since no weight moved |
| 3. Label coverage | 3 of 3 | 3 of 3 | MET |
| 4. Appeal path | 5 of 5 | 5 of 5 | MET |
| 5. Bad input | 3 of 4 | **4 of 4** | **MET** |

Four of the five criteria now pass. The one still missed is score spread,
which no amount of validation work can close. See the sweep above.

**A mislabelled column, found while re-reading the reports.** The attack
report's "Score" column was printing `confidence` rather than the combined
score. EV10 therefore showed up as `ai` at 0.331, which is well under the
0.55 AI threshold and looks alarming until you notice the number is a
distance from 0.5 rather than a score. Its real combined score is 0.666.
The column is now headed `Confidence`. It's worth recording because the
misreading it invited is exactly the kind this project is meant to be
careful about.

## Rate limit verification

```
python scripts/run_attacks.py --flood 15
200 200 200 200 200 200 429 429 429 429 429 429 429 429 429
```

6 through and 9 rate-limited, which matches the 6-a-minute limit exactly.
Full run in `results/flood_2026-08-31_1717.md`.

The `flood_same_creator` family in the attack set confirms the same thing
from the other direction: 6 of its 12 rows scored and the other 6 came back
429.

## Signal candidates that were rejected

Two approaches were built and tested against real data before the pattern
signal that shipped. They're kept here because a negative result on real
data is still evidence, not to pad the file out.

### Attempt 1, a stock-phrase keyword list

This matched about 20 known AI-writing phrases ("delve into", "navigate the
complexities", "it's important to note that", and so on), counted per 100
words. It was tested against two hand-written calibration sets, four real
chatbot completions, and a larger external buzzword list of around 130
entries.

**Result: zero hits on every single sample, AI and human alike, across five
separate test passes.** It only ever fired on text written specifically to
contain its own keywords, and never on ordinary informational chatbot
output, which is what this service is actually likely to receive. It was
dropped completely rather than given a smaller weight, because a keyword
list that only detects the examples built to trigger it isn't a signal at
all.

### Attempt 2, burstiness (perplexity variance across sentences)

This scored the coefficient of variation of per-sentence perplexity, on the
idea that human writing alternates between easy and hard-to-predict
sentences while generated text holds a steadier difficulty.

**Result: there was real signal there,** with AI samples averaging a
coefficient of variation around 0.55 against roughly 0.84 for human
samples, pointing the right way. **But the overlap was too big to trust.**
One real human sample, a piece of formal academic writing, scored *lower*,
meaning more machine-uniform, than every single AI sample tested. That's
exactly the false-positive failure this project exists to avoid: punishing
a real writer for writing in a consistent, formal register. It was dropped
for the same reason the model signal's blind spot matters. The code stays
in the repository as `detector.py::burstiness_signal`, marked unused, as
the record of the attempt.

### What shipped instead

`phrasing.py::pattern_signal` matches sentence *structure* using regexes
over open slots, rather than matching vocabulary, which is why it doesn't
repeat the keyword list's failure. Tested against the same chatbot
completions that broke the phrase list, it also scores 0.0 on all of them,
and correctly so, since none of that text is in the register it targets.
Given B2B or marketing-style text instead, it separates cleanly. A
constructed AI-style paragraph scores 1.0, ordinary human product writing
on the same topic scores 0.0, and a human deliberately writing in a punchy
fragment-heavy style scored 0.33. That last one is a real, if partial, path
to a false positive, and it's specific to the fragment-run half of the
signal. The contrastive-pair half stayed at 0.0 on every human sample
tested.
