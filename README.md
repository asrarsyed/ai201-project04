# Provenance Guard

<!-- ─────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

Provenance Guard is a small backend service a writing site plugs into. Text comes in, and what comes back is a guess (AI or human), a confidence score, and one of three plain-English labels a reader can actually understand: high-confidence AI, high-confidence human, or unsure. Two independent signals feed the guess: a local language model reading for predictability, and a stylometry check reading the text's shape (sentence length, vocabulary, punctuation) with no understanding of meaning at all. A writer who disagrees with the label can appeal, which flags the item for review rather than silently standing in judgment.

The full trace path a submission takes, step by step, is in [notes/trace.md](notes/trace.md).

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the text is to a local language model (perplexity), turned into a 0–1 score where higher means more likely AI.

**Why that might differ between human and AI writing:** A language model writes by repeatedly picking a likely next word, so its own output tends to be easy for a model to predict. Human writing wanders more.

**What it can't see:** It can't tell predictable from AI-written. Plain, ordinary writing (short sentences, common words) scores machine-like even from a real person, and dense, rare-word prose scores human-like even when AI wrote it. It rewards the writers with the least room to argue back.

### Signal two — the style signal

**What it measures:** The shape of the text, not its meaning — sentence length spread, vocabulary repetition (type-token ratio), and density of semicolons/dashes/ellipses. Combined into a 0–1 score, higher means more likely AI.

**Why that might differ between human and AI writing:** Generated prose tends toward even, mid-length sentences and a narrower vocabulary. Human writing is lumpier.

**What it can't see:** It cannot read. It has no idea what the text says, so anything that changes shape without changing substance (typos, breaking up sentences, pasting a quotation) moves the score. It also has the same blind spot as signal one in reverse: testing it on my own calibration text, plain AI writing scored *more* AI-ish than ornate AI writing with rare words and an em dash — rare/varied words read as more human to this signal, same trap signal one falls into.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** A weighted average of the two 0–1 signal scores, `config.WEIGHT_MODEL_SIGNAL * model_score + config.WEIGHT_STYLE_SIGNAL * style_score`. I ran both signals over 7 calibration texts (clearly AI, informal real human, plain AI, formal AI, a real human blog post, formal human writing, and a lightly-edited AI paragraph) before picking the weights. Contrary to what I expected, the two signals never actually disagreed in direction on this set — they consistently moved *together*, both leaning AI-ish on the same texts, including two human-written ones. So "what happens when they disagree" turned out to be the wrong question for my data; the real finding was that model_score swung harder and less reliably (0.47–0.93 across the set) than style_score (0.46–0.70), and the model signal was the one most responsible for pushing formal/literate human writing toward "AI". I weighted style_score higher specifically to blunt that.

**The numbers:** `WEIGHT_MODEL_SIGNAL = 0.35`, `WEIGHT_STYLE_SIGNAL = 0.65` (config.py). Style counts nearly twice as much as the model signal, because the model signal was the less stable, more false-positive-prone of the two on my calibration set.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:** They didn't split in direction, but they split in *magnitude* on two texts with almost identical texture. "Informal real human" writing (a founder's blog post) scored model=0.467, style=0.463 — both correctly near the human end. "Clearly human (blog)" — another real, informal, first-person post, just as casual, with a typo left in — scored model=0.624, style=0.578: both signals leaning AI, and the model signal driving most of that lean. Combined, that second text lands at 0.594, in the "unsure" band rather than "human" under my current thresholds. That's the case the combining rule has to live with: reweighting toward style softened it (0.594 vs. an unweighted average of 0.601) but didn't fix it. A real, ordinary person writing casually about their own life can still land in "unsure," not "human" — the reweight reduces how often that happens, it doesn't eliminate it. Threshold tuning in Milestone 5 is the next lever, not the combining rule alone.


## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->


## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next week's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "The quick brown fox jumps over the lazy dog near the riverbank every single morning without fail.", "creator_id": "asrar"}'
```

```json
{
  "confidence": null,
  "content_id": "1d55ceb2-3008-447b-8e94-5b603ceec951",
  "guess": null,
  "label": null,
  "model_score": 0.139,
  "style_score": null
}
```

<!-- confidence, guess, and label are still placeholders — Milestone 3 only
     wires in the first signal. Milestones 4 and 5 fill these in. -->

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 1,
  "entries": [
    {
      "combined_score": null,
      "content_id": "1d55ceb2-3008-447b-8e94-5b603ceec951",
      "creator_id": "asrar",
      "guess": null,
      "label": null,
      "model_score": 0.139,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-08-30T23:41:31+00:00"
    }
  ]
}
```


## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->


## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```


## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:


## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->


## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->


## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last week

     Do not delete and recreate this repository.
     
══════════════════════════════════════════════════════════════════════ -->