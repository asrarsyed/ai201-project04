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

**What it can't see:** It cannot read. It has no idea what the text says, so anything that changes shape without changing substance (typos, breaking up sentences, pasting a quotation) moves the score. Its vocabulary measure has the same trap signal one falls into: rare, varied words (`type_token_ratio` near 1.0) score as more human even when AI wrote them, and repetitive, ordinary vocabulary scores as more AI-ish even from a real person.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** A weighted average of the two 0–1 signal scores, `config.WEIGHT_MODEL_SIGNAL * model_score + config.WEIGHT_STYLE_SIGNAL * style_score`. I ran both signals over 7 calibration texts (clearly AI, informal real human, plain AI, formal AI, a real human blog post, formal human writing, and a lightly-edited AI paragraph) before picking the weights. Contrary to what I expected, the two signals never actually disagreed in direction on this set — they consistently moved *together*, both leaning AI-ish on the same texts, including two human-written ones. So "what happens when they disagree" turned out to be the wrong question for my data; the real finding was that model_score swung harder and less reliably (0.47–0.93 across the set) than style_score (0.46–0.70), and the model signal was the one most responsible for pushing formal/literate human writing toward "AI". I weighted style_score higher specifically to blunt that.

**The numbers:** `WEIGHT_MODEL_SIGNAL = 0.35`, `WEIGHT_STYLE_SIGNAL = 0.65` (config.py). Style counts nearly twice as much as the model signal, because the model signal was the less stable, more false-positive-prone of the two on my calibration set.

> **Updated in Stretch Features:** a third signal (`phrasing.py::pattern_signal`) was added later, and the weights above were rebalanced to `WEIGHT_MODEL_SIGNAL = 0.30`, `WEIGHT_STYLE_SIGNAL = 0.55`, `WEIGHT_PATTERN_SIGNAL = 0.15` to make room for it — style still counts for the most, for the same reason described above. `combine_signals` is now a three-term weighted average; see the Stretch Features section for the third signal's own writeup and why it's weighted lowest. This paragraph is left as originally written because it's the record of the actual two-signal Milestone 4 decision, not because the numbers are current.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:** They didn't split in direction, but they split in *magnitude* on two texts with almost identical texture. "Informal real human" writing (a founder's blog post) scored model=0.467, style=0.463 — both correctly near the human end. "Clearly human (blog)" — another real, informal, first-person post, just as casual, with a typo left in — scored model=0.624, style=0.578: both signals leaning AI, and the model signal driving most of that lean. Combined, that second text lands at 0.594, in the "unsure" band rather than "human" under my current thresholds. That's the case the combining rule has to live with: reweighting toward style softened it (0.594 vs. an unweighted average of 0.601) but didn't fix it. A real, ordinary person writing casually about their own life can still land in "unsure," not "human" — the reweight reduces how often that happens, it doesn't eliminate it.

**A bug the label-reachability test in Milestone 5 uncovered:** `punctuation_density` returning 0 (no semicolons/dashes/ellipses — the common case for ordinary writing, human or AI) was flipping to a *maximally AI-ish* contribution inside `style_signal`. That's backwards: absence of that punctuation isn't evidence of anything, it's just how most people write most of the time. It was actively dragging plain human calibration text upward and making "high-confidence human" unreachable with real text. Fixed it to score a neutral 0.5 when density is 0, so the measure only moves the score when a writer actually uses that punctuation — which is where it has real signal. I chose this over dropping punctuation from `style_signal` entirely because I wanted to keep its contribution for writers who *do* use semicolons and dashes distinctively, not just discard the measure. This did cost some AI-detection sharpness — clearly-AI text also commonly has zero fancy punctuation, so the fix pulled AI-text scores down too, and I had to lower `AI_THRESHOLD` from 0.65 to 0.55 to compensate (see Label Variants). That's the deliberate trade from Criterion 1: I'd rather blunt AI detection than keep punishing real writers for writing plainly.


## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | "We think this was probably written by a person." |
| unsure | 0.35 – 0.55 | "We can't tell whether this was written by a person or by AI. This isn't an accusation — it just means our checks didn't turn up a clear answer either way." |
| high-confidence AI | 0.55 – 1.00 | "We think this was probably written by AI." |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->
I wrote the first sentence as plainly as the other two ("we can't tell"), then added a second sentence specifically to head off the reading a real writer would otherwise land on: that "unsure" is a soft accusation, or "we're not sure, but we suspect you." Saying outright that it isn't an accusation, and that it just means the checks didn't produce a clear answer, keeps the tone the same whether the writer is completely innocent or actually used AI — it doesn't lean either way, which is the whole point of the band.


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
  -d '{"text": "MerchantE is a financial technology company that provides payment-processing and payment-infrastructure services to businesses. Founded in 1999, it began as an e-commerce payment provider and has grown into a full-service payments platform.", "creator_id": "asrar"}'
```

```json
{
  "confidence": 0.1875,
  "content_id": "a9b43bd3-c035-411d-ae96-997cb2567301",
  "guess": "ai",
  "label": "We think this was probably written by AI.",
  "model_score": 0.8206,
  "style_score": 0.4716
}
```

> **Note:** this is the actual unit 7 response, pasted as it was returned before
> the Stretch Features were built. A current `/submit` response also includes
> `pattern_score` (the third signal) and `creator_note` (per-creator
> reputation) — see the Stretch Features section for a current, full example.

**An appeal**

<!-- The writer disagrees with the "ai" label above and appeals, using the
     content_id from the submission response. -->

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "a9b43bd3-c035-411d-ae96-997cb2567301", "reasoning": "I wrote this myself, it'\''s a factual company description I researched and wrote by hand."}'
```

```json
{
  "content_id": "a9b43bd3-c035-411d-ae96-997cb2567301",
  "message": "Your appeal has been recorded and the decision is under review.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 3,
  "entries": [
    {
      "combined_score": 0.44199999999999995,
      "content_id": "c809438f-962e-4585-bfca-c170f12b2cd0",
      "creator_id": "asrar",
      "guess": "unsure",
      "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation — it just means our checks didn't turn up a clear answer either way.",
      "model_score": 0.6474,
      "status": "decided",
      "style_score": 0.3314,
      "timestamp": "2026-08-31T01:48:01+00:00"
    },
    {
      "combined_score": 0.59375,
      "content_id": "a9b43bd3-c035-411d-ae96-997cb2567301",
      "creator_id": "asrar",
      "guess": "ai",
      "label": "We think this was probably written by AI.",
      "model_score": 0.8206,
      "status": "decided",
      "style_score": 0.4716,
      "timestamp": "2026-08-31T01:48:01+00:00"
    },
    {
      "content_id": "a9b43bd3-c035-411d-ae96-997cb2567301",
      "creator_id": "asrar",
      "event": "appeal",
      "reasoning": "I wrote this myself, it's a factual company description I researched and wrote by hand.",
      "status": "under_review",
      "timestamp": "2026-08-31T01:48:08+00:00"
    }
  ]
}
```

<!-- Note the original "decided" entry for a9b43bd3... is untouched — the
     appeal is a new, separate entry with status "under_review", not an edit.
     That's the audit log's append-only design: the record of what was first
     decided survives the challenge. -->


## How I Used AI

**Moment 1**

- *What I asked for:* I asked for `style_signal`'s combining rule (Milestone 4) — how to flip direction and scale `sentence_length_spread` and `punctuation_density` onto 0–1 before averaging them with `type_token_ratio`.
- *What came back:* A hard-clip-and-divide approach (`min(value, cap) / cap`) with specific caps, plus flipping all three toward "higher = AI" to match `model_signal`'s direction.
- *What I changed:* I didn't take the caps on faith — I ran the three-measure signal against real calibration text I supplied (a founder's informal blog post vs. two AI-generated paragraphs) and found the human text barely separated from the AI text. I pushed back and asked to retune the `sentence_length_spread` cap specifically, which the model had set too loose (1.5) to let that measure swing hard enough on real human writing. Lowering it to 0.8 fixed the separation — a change driven by my own test data, not something I accepted as given.

**Moment 2**

- *What I asked for:* Before writing `scoring.py::combine_signals`'s weights, I asked it to run both signals over several calibration texts (mine plus ones I found) and report where they agreed and disagreed, per Milestone 4's instructions.
- *What came back:* A weighting recommendation (0.35 model / 0.65 style) based on the finding that the two signals never disagreed in direction, but the model signal swung harder and was the main driver of false positives on formal human writing.
- *What I changed:* Later, while testing label reachability for Milestone 5, I had it re-verify the "high-confidence human" label was actually reachable with real text rather than assuming the earlier weighting was sufficient. That test surfaced a real bug it had introduced back in Moment 1 — `punctuation_density` returning 0 was scoring as maximally AI-ish, which silently blocked the human label from ever being reached. I had it fix the direction (0 density now scores neutral, not AI-ish) and then re-derive `AI_THRESHOLD` from fresh test data instead of guessing a new number, which is what actually made all three labels reachable.

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

## Stretch Features

Six additions beyond the required build, in the order they were built.

### `GET /content/<content_id>`

Returns the most recent audit log entry for one content_id — a writer's or a
site's way of asking "where does this stand right now" without pulling the
whole log. "Current" means the *last* entry, not the first: an item that was
appealed shows `status: "under_review"`, even though the original `decided`
entry (with the original score and label) is still sitting in `/log`,
untouched. That's the same append-only design the appeal path already relies
on — this endpoint just reads the tail of one item's history instead of all
of it.

```bash
$ curl http://127.0.0.1:5000/content/cc96cc83-10c3-467e-b6ad-5669da740cac
```
```json
{
  "combined_score": 0.7026,
  "content_id": "cc96cc83-10c3-467e-b6ad-5669da740cac",
  "creator_id": "testphrase",
  "guess": "ai",
  "label": "We think this was probably written by AI.",
  "model_score": 0.8818,
  "pattern_score": 1.0,
  "status": "decided",
  "style_score": 0.5238,
  "timestamp": "2026-08-31T04:34:01+00:00"
}
```

Unknown id returns `404 {"error": "not_found", ...}` rather than an empty
200 — a typo in the id should look like "nothing here," not "here's nothing."

### `GET /creator/<creator_id>`

A writer's full history: every content_id they've ever submitted, each with
its own timeline of entries and its current status, grouped rather than left
as one flat list a caller would have to reassemble by hand.

```bash
$ curl http://127.0.0.1:5000/creator/testphrase
```
```json
{
  "creator_id": "testphrase",
  "submission_count": 1,
  "items": [
    {"content_id": "cc96cc83-...", "current_status": "decided", "history": [ ... ]}
  ]
}
```

### `GET /stats`

Aggregate numbers over the whole audit log: label distribution, appeal rate,
and average score per signal. Nothing here is a new source of truth — it's a
read of what `/log` already recorded, computed on request rather than stored
separately, so it can never drift from the log itself.

```bash
$ curl http://127.0.0.1:5000/stats
```
```json
{
  "total_entries": 20,
  "decisions": 11,
  "appeals": 2,
  "rejections": 3,
  "appeal_rate": 0.1818,
  "guess_distribution": {"ai": 6, "human": 2, "unsure": 3},
  "average_scores": {
    "model_score": 0.6429, "style_score": 0.4412,
    "pattern_score": 1.0, "combined_score": 0.5167
  }
}
```

**A real limitation worth naming:** the audit log is append-only with no
per-content-id index, so `/stats` and `/creator/<id>` both do a full scan of
`read_entries()` and group in memory. Fine at this project's scale (hundreds
to low thousands of entries); the wrong design for a log with millions of
lines, where this would need a real index or a database instead of a flat
JSONL file.

### Signal three — the pattern signal, and two rejected attempts before it

This section documents a real investigation, not just the final answer:
two approaches were built and tested against real data before landing on the
one that shipped. The negative results are included because they're honest
evidence about where these signals do and don't work, not padding.

**Attempt 1 — a stock-phrase keyword list.** First version of
`phrasing.py` matched a short, high-precision list of ~20 phrases ("delve
into", "navigate the complexities", "tapestry of", "it's important to note
that", "as an AI language model," …), counted per 100 words. Tested against
two hand-written calibration sets (16 samples, mixed AI-style and
human-style writing across topics) and four real chatbot completions
(informational answers about Earth, pregnancy care, ocean fish populations,
and UFC controversies) — **it scored zero hits on every single sample**,
AI and human alike, across five separate test passes, including a second,
much larger pass using an external ~130-entry list of documented AI
overused words, phrases, and corporate buzzwords. It only ever fired on
text written specifically to contain its own keywords (a demo sentence, or
AI content-marketing copy) — never on ordinary informational chatbot output,
which is what this service is actually likely to receive. A keyword list
that only detects the examples built to trigger it isn't a signal, it's a
mirror. Dropped entirely, not shrunk in weight.

**Attempt 2 — burstiness (perplexity variance across sentences).** Reusing
`detector.py`'s model, this scored the coefficient of variation of
per-sentence perplexity instead of the average level `model_signal` already
measures — the idea being that human writing alternates between easy and
hard-to-predict sentences while generated text holds a more uniform
difficulty. Real signal existed (AI-sample mean CV ≈0.55, human-sample mean
CV ≈0.84, correct direction), but the overlap was too large to trust: one
real human sample (formal academic writing) scored *lower* — more
"AI-uniform" — than every single AI sample tested, which is exactly the
false-positive failure mode this whole project exists to avoid: penalizing
a real writer specifically because they write in a consistent, formal
register. Dropped for the same reason signal one's blind spot matters —
a signal that fails hardest on formal writers isn't safe to ship at any
weight. (`detector.py::burstiness_signal` is left in the codebase,
explicitly marked as unused, as the record of this attempt.)

**What shipped — `phrasing.py::pattern_signal`.** Rather than matching
vocabulary, this matches *rhetorical sentence structure*: a contrastive pair
("It's not about X, it's about Y"), and runs of three or more short (1–3
word) declarative fragments in a row ("Focused. Aligned. Measurable."). Both
patterns are documented AI writing tics, specifically in B2B, marketing, and
opinion-style content. Regexes over open slots, not fixed strings, so it
catches the *shape* of the device regardless of the words filling it in.

**Why that might differ between human and AI writing:** these are
persuasive rhetorical devices a language model reaches for often when
writing punchy, confident-sounding copy, because the pattern itself reads as
authoritative regardless of what fills the slots. A person writing plainly
about something they know rarely constructs a formal contrastive pair or
stacks three one-word sentences in a row — those are stylistic choices a
copywriter (human or AI) makes on purpose, not something that happens by
accident in ordinary writing.

**What it can't see, and the actual numbers:** tested against the same real
chatbot completions and calibration text that broke the phrase list — this
signal also scores 0.0 on all of them, correctly, because none of that text
is in the register these patterns target. Given B2B/marketing-style text
instead, it separates cleanly: a constructed AI-style marketing paragraph
("It's not about working harder. It's about working smarter. Not because
it's easy. But because it works. Clear priorities. Aligned incentives.
Measurable goals. The result? Teams that actually ship.") scores 1.0
(3 contrastive pairs, 1 fragment run); ordinary human product writing about
the same topic, in plain sentences, scores 0.0; a human deliberately writing
in a punchy, fragment-heavy style ("Short. Clear. Honest.") scored 0.33 —
real but partial false-positive risk from the fragment-run half of the
signal specifically, not the contrastive-pair half, which stayed at 0.0 on
every human sample tested including that one. So the blind spot is
concrete: this signal is **register-specific** (silent outside B2B/opinion
content, which is most of what a general writing site would see) and its
weaker half (fragment runs) can fire on a real writer's deliberate style
choice. It is also, like the rejected phrase list, cheap to defeat on
purpose — writing in longer, non-parallel sentences removes every trigger
with no loss of meaning.

**Why it's weighted lowest:** `WEIGHT_MODEL_SIGNAL = 0.30`,
`WEIGHT_STYLE_SIGNAL = 0.55`, `WEIGHT_PATTERN_SIGNAL = 0.15` (down from
0.35/0.65 with only two signals). Given it reads 0.0 on most submissions
(anything outside its target register) and has a known partial
false-positive path even within that register, it's built to nudge the
combined score on the specific text it's built for, not drive it.
`combine_signals` still takes `pattern_score` as an optional third argument
defaulting to 0.0, so nothing upstream that only knows about two signals
breaks.

### `POST /submit/batch`

Scores a list of `{text, creator_id}` items in one request instead of one
call per item — the shape a real writing platform would actually want when
importing or re-scanning a backlog. Each item runs through the same
validation and scoring path as `/submit` (`_score_and_log`, shared by both
routes so they can't silently diverge), independently: one bad item in a
batch gets its own rejection and doesn't stop the rest of the batch.

Capped at `config.BATCH_MAX_ITEMS = 20`, and it carries the same
`@limiter.limit(...)` line as `/submit` (commented out until unit 8 turns
rate limiting on, exactly like `/submit`'s). Both protections matter for
different reasons: the item cap bounds how much scoring work one request can
demand; the rate limit bounds how many requests a caller gets per minute.
Without its own limiter line, `/submit/batch` would have let one request do
20x the scoring work of a normal submission while counting as a single call
against `/submit`'s limit — a free way around the cap that "cap the batch
size" alone doesn't close.

```bash
$ curl -X POST http://127.0.0.1:5000/submit/batch \
  -H "Content-Type: application/json" \
  -d '{"items": [
    {"text": "The cat sat quietly on the warm windowsill all afternoon.", "creator_id": "batch1"},
    {"text": "", "creator_id": "batch2"},
    {"text": "It'\''s not about working harder. It'\''s about working smarter. Not because it'\''s easy. But because it works. The result? Teams that ship.", "creator_id": "batch3"}
  ]}'
```
```json
{
  "count": 3,
  "results": [
    {"content_id": "7297d9a3-...", "guess": "unsure", "model_score": 0.2064, "pattern_score": 0.0, "style_score": 0.5333, ...},
    {"error": "invalid_input", "message": "text is required and must be at least a few words long."},
    {"content_id": "76545fb6-...", "guess": "ai", "model_score": 0.5809, "pattern_score": 1.0, "style_score": 0.4136, ...}
  ]
}
```

### Per-creator reputation (`creators.py`) — the informational answer to "verified human"

A real verified-human credential (an identity check, an extra step a writer
takes to earn a badge) was scoped out earlier — see the deferred section
below for why. What shipped instead is smaller and more honest about what
this service can actually claim: a running tally, per `creator_id`, of what
this service's *own* three signals have said about that writer's past
submissions, surfaced back to the reader instead of decided for them.

**What it is not:** an identity check. Nobody proves anything to earn
"verified" here. It's a majority vote of this detector's own past guesses
about one creator_id — `human_count > ai_count`, recomputed fresh on every
read, not stored as an independent flag that could drift out of sync with
the counts. A brand-new creator with zero history is unverified (`0 > 0` is
false), same starting point as everyone else.

**Storage:** `creators.py`, backed by `logs/creators.json` — a plain dict
keyed by `creator_id`, not the audit log. The audit log's append-only shape
is right for "what happened, in order" but wrong for "what's true about
this creator right now": answering that from the log would mean scanning
every entry on every request. This is current-state, so a small
read-modify-write file fits better, guarded by the same `threading.Lock`
pattern `audit.py` already uses for its own writes — a real concurrency
concern here too, since two submissions from the same creator arriving
close together both read-modify-write the same record.

**What updates it:** every `/submit` and `/submit/batch` decision calls
`creators.record_guess(creator_id, guess)` right after logging, bumping
exactly one of `ai_count` / `human_count` / `unsure_count`. A submission
with no `creator_id` updates nothing — there's no one to attribute it to.
Rejected submissions (bad input) never reach this — only a completed
decision counts.

**A current, full `/submit` response** — the same request that opened the
Sample Run section above, re-sent after every Stretch Feature landed:

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "MerchantE is a financial technology company that provides payment-processing and payment-infrastructure services to businesses. Founded in 1999, it began as an e-commerce payment provider and has grown into a full-service payments platform.", "creator_id": "asrar"}'
```
```json
{
  "confidence": 0.0111,
  "content_id": "01b15855-7c84-45e2-83b5-ee12c2de6578",
  "creator_note": "This writer is unverified human. Deemed AI 0 times, deemed human 0 times, and unsure 1 time.",
  "guess": "unsure",
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation — it just means our checks didn't turn up a clear answer either way.",
  "model_score": 0.8206,
  "pattern_score": 0.0,
  "style_score": 0.4716
}
```

Note this lands on "unsure" rather than the original "ai" — `model_score`
and `style_score` are close to their original unit 7 values (perplexity
scoring has real run-to-run noise, documented in `detector.py`), but the
rebalanced weights (0.30/0.55/0.15 instead of 0.35/0.65) combined with an
`unsure`-counted `creator_note` for a brand-new creator are enough to move
this specific text across the threshold. That's a real, visible consequence
of the reweighting, not a cherry-picked example.

**What it changes, and what it deliberately doesn't:** nothing about
`combine_signals` or the thresholds. Reputation never touches the score or
the label — it rides alongside them as a `creator_note` string on `/submit`,
`/submit/batch`, `/content/<id>`, and `/creator/<id>`, e.g.:

```
"This writer is verified human. Deemed AI 1 time, deemed human 2 times, and unsure 0 times."
"This writer is unverified human. Deemed AI 11 times, deemed human 2 times, and unsure 3 times."
```

That was a deliberate scope cut: letting a creator's history soften or
sharpen their *current* score is a real design decision (does one appeal
years ago excuse today's text? does a first-time writer with no history get
penalized by default?) big enough to deserve its own investigation, the
same way the third signal did. Reporting the numbers and letting a human
reader weigh them avoids answering that question by accident.

---

**Not built (yet), and deliberately deferred** — not one of the six
additions above, listed here because it was actively considered and cut,
not overlooked: review queue, moderator decisions, real identity
verification. A `GET /review-queue` +
`POST /decide` pair would round the appeal path into a full moderation loop,
but `POST /decide` needs an actual concept of "who is allowed to decide" —
without that it's just a second way to overwrite a status, which is worse
than the appeal path that exists now. A real verified-human credential (an
identity check, an "extra step" a writer completes once to earn a badge, as
opposed to the reputation tally above) needs its own design decision about
whether and how that credential should interact with scoring — worth doing
right, not worth rushing in alongside everything else here.
