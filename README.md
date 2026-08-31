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
| high-confidence human | 0.00 – 0.35 | "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it." |
| unsure | 0.35 – 0.55 | "We can't tell whether this was written by a person or by AI. This isn't an accusation — it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it." |
| high-confidence AI | 0.55 – 1.00 | "We think this was probably written by AI. That's a guess from automated checks, not a finding — they're wrong sometimes. If you wrote this yourself, you can appeal and a person will look at it." |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->
I wrote the first sentence as plainly as the other two ("we can't tell"), then added a second sentence specifically to head off the reading a real writer would otherwise land on: that "unsure" is a soft accusation, or "we're not sure, but we suspect you." Saying outright that it isn't an accusation, and that it just means the checks didn't produce a clear answer, keeps the tone the same whether the writer is completely innocent or actually used AI — it doesn't lean either way, which is the whole point of the band.

**Revised after reviewing a peer's project (unit 8):** all three labels originally ended at "we think X" with no mention of the appeal path, and the `ai` label read like a flat verdict ("We think this was probably written by AI.") rather than a guess. Reading them cold, a wrongly-flagged writer would have no way to know from the response itself that a challenge exists, and the `ai` label in particular didn't distinguish "our checks produced this guess" from "this is what happened" — the same gap a peer's writeup named directly and fixed on their own labels. I added: (1) an explicit appeal mention to all three, not just the ones that seem like they'd need it — a label with no way out reads as a verdict even when it's the *good* label, since a "human" call can also be wrong and worth appealing; (2) a hedge on the `ai` label ("that's a guess from automated checks, not a finding — they're wrong sometimes") so it doesn't overstate what a probability score is. Score ranges and `AI_THRESHOLD`/`HUMAN_THRESHOLD` are unchanged — this is a copy-only revision, verified by re-running `python detector.py` style label reachability checks; nothing about `scoring.py::combine_signals` moved.


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

**My limits:** 6 per minute, 120 per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->
A real writer submitting own work fires off a handful of drafts an hour, not six in sixty seconds. 6/minute lets someone resubmit a few times after edits without hitting the wall, but caps a burst tight enough that mapping thresholds costs a script real time. 120/day covers a genuinely prolific human (a few dozen pieces, some retries) while keeping a thousand-variation sweep from finishing in one sitting; at 6/min a script maxes out the daily cap in 20 minutes if it doesn't get throttled by the minute limit first, so the minute limit is the one actually doing the work.

**What a caller counts as:** 
<!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

Per creator_id, not per address. `rate_limit_key()` in app.py reads `creator_id` off the JSON body and keys on that, falling back to the caller's IP only when the payload isn't a dict or creator_id is missing/blank. Per-IP would fail differently: a script rotating creator_id per request looks like a thousand distinct callers to a per-address limiter but is still one caller per-creator_id, so keying on creator_id is the one an attacker can't trivially route around by spoofing IPs, and it doesn't lump a shared household/NAT IP into one bucket either.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 200 429 429 429 429 429 429 429 429 429
```

6 through, 9 rate limited, matching the 6/minute limit exactly. Full run in `results/flood_2026-08-31_1717.md`.


## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

Full run: `results/attack_run_2026-08-31_1726_before.md` (56 attacks, 17:26). Verdicts below are mine, reasoned from each row's `targets` column against what came back — the script only auto-marks a 5xx as BROKE.

| ID | Family | Targeting | Status | Guess | Score | Verdict |
|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | human | 0.311 | **BROKE** |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | unsure | 0.253 | held |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | unsure | 0.023 | held |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | unsure | 0.116 | held |
| EV05 | evasion | both signals: heavy human editing pass | 200 | human | 0.343 | **BROKE** |
| EV06 | evasion | signal two: one very long, one very short sentence | 200 | human | 0.309 | **BROKE** |
| EV07 | evasion | signal two: padding with punctuation | 200 | unsure | 0.080 | held |
| EV08 | evasion | signal one: text below the token window | 200 | human | 0.284 | **BROKE** |
| EV09 | evasion | both: AI text with a human opening bolted on | 200 | unsure | 0.186 | held |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.206 | held |
| FP01 | false_positive | plain, clear human writing | 200 | unsure | 0.182 | held (see note) |
| FP02 | false_positive | human writing, formal register | 200 | unsure | 0.011 | held (see note) |
| FP03 | false_positive | non-native speaker writing carefully | 200 | unsure | 0.016 | held (see note) |
| FP04 | false_positive | student essay to a rubric | 200 | unsure | 0.048 | held (see note) |
| FP05 | false_positive | technical documentation | 200 | unsure | 0.055 | held (see note) |
| FP06 | false_positive | person imitating a formal template | 200 | unsure | 0.062 | held (see note) |
| FP07 | false_positive | deliberate phrase repetition | 200 | unsure | 0.057 | held (see note) |
| FP08 | false_positive | very short genuine submission | 200 | human | 0.455 | held |
| PI01 | prompt_injection | instruction to ignore the check | 200 | human | 0.274 | held |
| PI02 | prompt_injection | instruction as a fake system message | 200 | human | 0.273 | held |
| PI03 | prompt_injection | instruction wrapped in writer's voice | 200 | unsure | 0.472 | held |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.359 | held |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | unsure | 0.396 | held |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.394 | held |
| MF01 | malformed | text is only whitespace | 400 | — | — | held |
| MF02 | malformed | text is a single character | 400 | — | — | held |
| MF03 | malformed | text is control characters | 200 | human | 0.275 | held (not missing/empty/oversized) |
| MF04 | malformed | text is only punctuation | 200 | unsure | 0.462 | held |
| MF05 | malformed | text is a very long single word | 400 | — | — | held |
| MF06 | malformed | text is emoji only | 400 | — | — | held |
| MF07 | malformed | text is right-to-left script | 200 | ai | 0.730 | held |
| MF08 | malformed | text is 60,000 characters | 200 | ai | 0.655 | **BROKE** |
| RQ01 | malformed | no text field at all | 400 | — | — | held |
| RQ02 | malformed | no creator_id | 200 | human | 0.347 | held (falls back to IP, by design) |
| RQ03 | malformed | text is a number | 400 | — | — | held |
| RQ04 | malformed | text is a list | 400 | — | — | held |
| RQ05 | malformed | text is null | 400 | — | — | held |
| RQ06 | malformed | creator_id is an object | 200 | human | 0.290 | **BROKE** |
| RQ07 | malformed | body is a JSON array, not an object | 500 | — | — | **BROKE** (auto) |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | held |
| RQ09 | malformed | body is empty | 400 | — | — | held |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | — | — | held |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | — | — | held (see note) |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | held |
| FL01_01–06 | flood_same_creator | 20 rapid submissions, one creator | 200×6 | human | 0.284 | held |
| FL01_07–12 | flood_same_creator | 20 rapid submissions, one creator | 429×6 | — | — | held |

**Count:** 56 attacks. 50 held, 6 broke (EV01, EV05, EV06, EV08, MF08, RQ06), plus 1 of those (RQ07) auto-marked by the script for a 500. Rounding out the families: evasion 4/10 broke, false_positive 0/8 broke (label), malformed 2/20 broke (+1 auto), prompt_injection 0/6, flood 0/12.

**Notes on the "held (see note)" rows:**
- **FP01–FP07** never got called `ai`, so they pass the letter of "no wrong high-confidence-AI accusation." But all seven landed `unsure`, not `human` — real, unremarkable human writing that a service is telling its author "we can't tell." That's not a broken attack by my letter-of-the-criterion definition, but it's the softer failure mode: the criteria measure the strict false-positive rate, not this one.
- **RQ11**: the 429 isn't RQ11 defeating anything on its own — the preceding malformed-body attacks (RQ08–RQ10, which have no parseable `creator_id`) all fell back to the caller's IP as the rate-limit key, and burned through the 6/minute budget together before RQ11 even ran. One script sending different *attacks* still counted as one *caller* the moment those attacks stopped carrying a creator_id. Real finding, not a scoring bug.

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json
{"combined_score": 0.31096, "content_id": "29272d7d-341e-4e70-9971-829946b19c90", "creator_id": "attacker_EV01", "guess": "human", "label": "We think this was probably written by a person.", "model_score": 0.1635, "pattern_score": 0.0, "status": "decided", "style_score": 0.4762}
{"combined_score": 0.34331, "content_id": "15c46fc4-52d9-441c-9e3b-b41cea1b5965", "creator_id": "attacker_EV05", "guess": "human", "label": "We think this was probably written by a person.", "model_score": 0.3212, "pattern_score": 0.0, "status": "decided", "style_score": 0.449}
{"combined_score": 0.30931, "content_id": "da0cf46f-86c6-4981-abc5-273e88ae35b6", "creator_id": "attacker_EV06", "guess": "human", "label": "We think this was probably written by a person.", "model_score": 0.5727, "pattern_score": 0.0, "status": "decided", "style_score": 0.25}
{"combined_score": 0.283715, "content_id": "401611ea-ce78-4e0a-a130-9cb5cd5713cb", "creator_id": "attacker_EV08", "guess": "human", "label": "We think this was probably written by a person.", "model_score": 0.2452, "pattern_score": 0.0, "status": "decided", "style_score": 0.3821}
{"combined_score": 0.494575, "content_id": "f039610c-b34a-46cf-b1d7-47e67977ce7d", "creator_id": "attacker_FP02", "guess": "unsure", "label": "We can't tell whether this was written by a person or by AI...", "model_score": 0.7387, "pattern_score": 0.0, "status": "decided", "style_score": 0.4963}
{"combined_score": 0.46913, "content_id": "28d49576-63c1-4942-ab79-eefb905a16cb", "creator_id": "attacker_FP06", "guess": "unsure", "label": "We can't tell whether this was written by a person or by AI...", "model_score": 0.8814, "pattern_score": 0.0, "status": "decided", "style_score": 0.3722}
{"combined_score": 0.6553200000000001, "content_id": "d3bfd956-6f62-433e-a57d-63e06bbc22e0", "creator_id": "attacker_MF08", "guess": "ai", "label": "We think this was probably written by AI.", "model_score": 0.9876, "pattern_score": 0.0, "status": "decided", "style_score": 0.6528}
{"combined_score": 0.28976, "content_id": "f6260228-f2e1-4db8-8cb6-9c784dfb19de", "creator_id": {"id": "x"}, "guess": "human", "label": "We think this was probably written by a person.", "model_score": 0.0492, "pattern_score": 0.0, "status": "decided", "style_score": 0.5}
{"creator_id": "unknown", "event": "rejected", "limit": "6 per 1 minute", "reason": "rate_limited", "status": "rejected"}
{"creator_id": "attacker_RQ12", "event": "rejected", "reason": "invalid_text", "status": "rejected"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

**RQ06** — `creator_id` sent as a JSON object (`{"id": "x"}`) instead of a string. The route accepted it, scored the text normally, and wrote the raw object straight into `creator_id` in the audit log — a field every other entry treats as a string. `GET /creator/<creator_id>` and `creators.record_guess()` both assume a string key; a real writer whose client library serializes their id oddly wouldn't get rejected up front, they'd get scored fine and then silently vanish from their own reputation history and their own `/creator/<id>` lookup, because nothing can match a dict against a URL path segment. It's the quietest kind of broken: no error, no 4xx, just a writer's record filed somewhere they can never find it again. `_validate_text` checks `text`'s type; nothing checks `creator_id`'s.


## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

Scenarios: `scenarios.py`. Full output: `results/run_2026-08-31_1810_before.md` (`run_eval.py::main`, 3 internal trials, 18:10). Note on Criterion 1's samples: these 10 are real human writing sourced from the public [allenai/c4](https://huggingface.co/datasets/allenai/c4) dataset, not my own writing as the criterion asks for — I didn't have my own writing prepared for this run. Documented here rather than silently substituted; see `scenarios.py`'s module docstring for the same note.

Across all three internal trials, gpt2's perplexity scores were bit-for-bit identical on every sample — the "identical input can score differently" warning in criteria.md didn't materialize on this run, on this machine. Trials differ only where the service's own logic branches (the appeal path, the bad-input rejections), not from model noise. Table below reflects that: three columns are shown because three trials were run and the target says three, but for these five scenarios the outcome was the same all three times.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives (human samples labelled high-confidence AI) | ≤ 1 of 10 | 0/10 | 0/10 | 0/10 | MET |
| 2. Score spread (AI avg exceeds human avg by ≥ 30 points) | ≥ 30 pts | 11.4 pts | 11.4 pts | 11.4 pts | **MISSED** |
| 3. Label coverage (all 3 labels reachable across the 15 samples) | 3 of 3 | 2/3 (no `ai`) | 2/3 (no `ai`) | 2/3 (no `ai`) | **MISSED** |
| 4. Appeal always changes status + logs an entry | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Missing/empty/oversized text → 4xx, detector never runs | 4 of 4 | 3/4 | 3/4 | 3/4 | **MISSED** |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

`scenarios.py` (the "human vs ai" scenario) → `run_eval.py::main` → `app.py::submit`. Criterion 2's 15 combined scores, trial 1, in submission order (10 human samples from `scenarios.py::SCENARIOS[1]`, then 5 AI samples):

```json
[0.383085, 0.425255, 0.41394, 0.4995600000000001, 0.31101, 0.49422, 0.402135, 0.4425, 0.27485000000000004, 0.38029999999999997, 0.5329699999999999, 0.529875, 0.49015, 0.51476, 0.516705]
```

Human average: 0.4027 (40.27 pts). AI average: 0.5169 (51.69 pts). Gap: **11.42 pts**, against a target of 30.

`scenarios.py` (the "bad input" scenario) → `run_eval.py::main` → `app.py::submit`. Trial 1, the oversized-text case:

```json
{
  "status": 200,
  "guess": "ai",
  "confidence": 0.5151,
  "model_score": 0.9975,
  "style_score": 0.8333,
  "label": "We think this was probably written by AI.",
  "sent": "word word word word word word word word word word word word word word "
}
```

`scenarios.py` (the "appeal path" scenario, `"kind": "appeal"`, added to `run_eval.py::main`) → `app.py::appeal`. Trial 1, item 1:

```json
{
  "status": 200,
  "guess": "unsure",
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation — it just means our checks didn't turn up a clear answer either way.",
  "appeal_status_code": 200,
  "appeal_response_status": "under_review",
  "status_before": "decided",
  "status_after": "under_review",
  "status_changed": true
}
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

**Criterion 2 and 3, and the evasion attacks (EV01/EV05/EV06/EV08) — one problem, not three.** Stage: the combining rule. My 5 AI-generated paragraphs (plain, well-formed, informational marketing-style prose) score high on signal one (`model_score` 0.84–0.91 — genuinely predictable text) but land right at signal two's midpoint (`style_score` 0.42–0.48 — ordinary sentence-length variety, ordinary vocabulary, no unusual punctuation; nothing about *shape* flags this text at all). `combine_signals` weights style at 0.55 and the model at 0.30 (`config.py`), specifically because Milestone 4 found the model signal was the less trustworthy, more false-positive-prone of the two on formal human writing. That decision is still right for its original purpose — it's why Criterion 1 passes at 0/10 — but it has a cost nobody measured until now: any AI text whose *shape* looks ordinary gets its strong model-signal evidence diluted by a style signal that has nothing to say, and the combined score can't clear 0.55 on its own. All 5 AI samples landed 0.49–0.53 — unsure, every time, in every trial. That's the same mechanism behind EV01 (typos raise word variety → style neutralizes a strong model signal), EV05 (heavy editing does the same), EV06 (sentence-length extremes), and EV08 (short text where style has even less to measure) — four "evasion" attacks and Criterion 2/3's whole miss are the identical failure: **style_score sits near 0.5 on plain prose, and at a 0.55 weight it can single-handedly keep a high model_score out of the "ai" band.** The `ai` label being unreachable across 15 varied samples (Criterion 3) isn't a separate bug from the 11.4-point gap (Criterion 2) — it's the direct consequence of it. This is also why `ai` only appeared in the attack run on text with real punctuation/length extremity (MF07's right-to-left script, MF08's repetition) rather than on ordinary AI prose — the style signal has to be pushed hard before it stops canceling out signal one.

**Criterion 5 and MF08/RQ07 — one stage, two mechanisms, both in the route.** `app.py::_validate_text` (line 231) checks only that `text` is a string with at least 3 words — there is no upper bound at all. A 50,000-word body (Criterion 5's oversized case) and a 60,000-character body (attack set's MF08) both sailed through validation and paid the full cost of `detector.model_signal` and `stylometry.style_signal` on the whole text — exactly the "run the detector on oversized input" failure Criterion 5 exists to catch, and the same mechanism both times. Separately, RQ07 (a JSON array body) is a route-stage crash, not a scoring one: `request.get_json(silent=True) or {}` happily returns a list when the body is a JSON array, and `rate_limit_key()` (and later `payload.get("text", "")`) calls `.get()` on it unconditionally — `list` has no `.get`, so it's an unhandled `AttributeError` before `_validate_text` ever runs. Both are the same class of gap: the route validates the *shape* of `text` but never validates the *shape* of the payload itself, at two different points (top-level body, and the field with no ceiling).

**RQ06 — the route, a different unchecked shape.** `creator_id` sent as a JSON object rather than a string. `_validate_text` only inspects `text`; nothing in the route checks `creator_id`'s type before it's written straight into the audit log and passed to `creators.record_guess()`. Same root cause as the RQ07/MF08 pair above — the route trusts payload shape past the one field it explicitly checks — but it doesn't crash, it corrupts silently: the audit log now has a non-string `creator_id`, and both `/creator/<creator_id>` and `creators.py`'s per-creator lookups key on strings, so that submission's reputation history is permanently unreachable by any legitimate lookup.

**On the two MET criteria — were they too easy?** Criterion 4 (appeal path, 5/5) I'd defend: the appeal handler is small and unconditional (any existing `content_id` moves to `under_review` and logs an entry, no branching), so there's no hidden failure mode a slightly harder target would have caught — 5/5 isn't a lucky number here, the code has no way to produce 4/5. Criterion 1 (false positives, 0/10) is a genuinely soft target in hindsight, though: it says "at most 1 of 10," but the same style-weight mechanism diagnosed above (Criterion 2/3) also means the service is *biased toward under-calling AI as human* right now — 0/10 false positives isn't proof the false-positive control is well-tuned, it's a symptom of the same imbalance that's failing Criterion 2. The criterion I'd tighten isn't the false-positive rate itself (missing some AI text is supposed to be the cheaper mistake) — it's that Criterion 1 in isolation can look reassuring for the wrong reason, and only reading it next to Criterion 2's miss reveals that. Next iteration, I'd pair Criterion 1 with a check that human samples don't just avoid `ai`, but also reach `human` (not stall in `unsure`) at some minimum rate — right now 8 of my 10 human samples landed `unsure`, which passes Criterion 1 to the letter while giving most real writers the same "we can't tell" answer as the AI samples.


## The Improvement

**What I changed:** Reweighted `combine_signals` (`config.py`): `WEIGHT_MODEL_SIGNAL` 0.30 → 0.45, `WEIGHT_STYLE_SIGNAL` 0.55 → 0.40, `WEIGHT_PATTERN_SIGNAL` unchanged at 0.15. One change, nothing else touched — no threshold moved, no validation added, no signal code edited.

**Which diagnosis pointed at it:** The diagnosis above (Criterion 2/3 and EV01/EV05/EV06/EV08) found that ordinary-shaped AI text scores high on signal one (model_score 0.84–0.91) but near-neutral on signal two (style_score 0.42–0.48), and at a 0.55 style weight that neutral reading was enough to single-handedly keep the combined score out of the "ai" band. Reweighting toward the signal that was actually right on this text — model — is the direct fix for that specific mechanism.

Before picking 0.45/0.40, I computed the combined scores my own 15-sample calibration set (`scenarios.py`'s "human vs ai") would produce at several weightings, using the real model_score/style_score pairs already collected. No weighting on this data clears the 30-point Criterion 2 target without also pushing human samples into "ai" — the two are in direct tension, not independently fixable. I picked the highest model weight that kept Criterion 1 at 0/10 on that data (0.45/0.40); anything past roughly 0.60/0.25 starts costing a false positive on this specific 10-sample set.

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

Full run: `results/attack_run_2026-08-31_1817_after.md` (56 attacks, 18:17). Only rows that changed from the "before" run are shown; everything else (all 6 prompt_injection, all 20 malformed except MF04, all 12 flood) landed exactly as before.

| ID | Family | Targeting | Before | After | Changed? |
|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | human (0.311) | human (0.472) | no — still BROKE, closer to the line |
| EV02 | evasion | signal two: broken-up sentences | unsure (0.253) | unsure (0.181) | no |
| EV05 | evasion | both signals: heavy human editing | human (0.343) | human (0.352) | no — still BROKE |
| EV06 | evasion | one very long, one very short sentence | human (0.309) | unsure (0.285) | **yes — fixed** |
| EV08 | evasion | signal one: text below the token window | human (0.284) | human (0.474) | no — still BROKE, closer to the line |
| EV10 | evasion | repeated stanza structure | ai (0.206) | ai (0.331) | no — held, more confidently |
| FP05 | false_positive | technical documentation, real human | unsure (0.055) | **ai (0.139)** | **yes — newly BROKE** |
| MF04 | malformed | text is only punctuation | unsure (0.462) | human (—) | no functional change — still not `ai` |
| MF08 | malformed | text is 60,000 characters | ai (0.655) | ai (0.411) | no — held both times, confidence dropped |

**Count:** 56 attacks, still 1 auto-BROKE (RQ07, same 500, untouched by this change). Of the 6 verdict changes shown: 1 evasion attack fixed (EV06), 1 new false positive (FP05), the rest are score movement without a verdict change.

**Criterion re-run (`run_eval.py --label after`, `results/run_2026-08-31_1817_after.md`):**

| Criterion | Target | Before | After | Verdict (after) |
|---|---|---|---|---|
| 1. False positives | ≤ 1 of 10 | 0/10 | 0/10 | MET (unchanged) |
| 2. Score spread | ≥ 30 pts | 11.4 pts | 16.6 pts | **still MISSED** |
| 3. Label coverage | 3 of 3 | 2/3 (no `ai`) | **3/3** | **MET** |
| 4. Appeal path | 5 of 5 | 5/5 | 5/5 | MET (unchanged) |
| 5. Bad input | 4 of 4 | 3/4 | 3/4 | still MISSED (unrelated — route-stage issue, not touched by this change) |

Criterion 2's real numbers, same 15-sample set, after the reweight:

```json
{"human_avg": 0.4133, "ai_avg": 0.5790, "gap_points": 16.57}
```

All 5 AI samples now score above 0.55 individually (0.557–0.599) — that's what flipped Criterion 3 to MET. The average gap widened from 11.4 to 16.6 points but still falls well short of 30; the two averages moved apart, but not far enough, because the human average also drifted up slightly (40.3 → 41.3) as the higher model weight gave a bit more say to signal one's noise on borderline human samples too.

**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

Partially, and I can point at exactly what it cost. It helped: Criterion 3 (label coverage) went from MISSED to MET — `ai` is now reachable, all 5 AI calibration samples correctly exceed 0.55, and one evasion attack (EV06) flipped from BROKE to held. It did not help: Criterion 2 (score spread) is still MISSED — the gap grew from 11.4 to 16.6 points but the math above showed no weighting alone reaches 30 without breaking Criterion 1, so this was never going to fully close it. And it has a real, measured cost: FP05 — real human technical documentation, previously a correct "unsure" — is now called `ai` outright. That's a new false-positive-shaped failure the attack set specifically warns to look for ("every one your service calls AI is a real writer it would have accused"), and it's the direct trade-off of giving signal one more weight: signal one's blind spot (dense, plain informational prose reads as "predictable," i.e. AI-like) got more say, and FP05 — a technical document, plain and information-dense — is exactly the kind of text that blind spot targets. This is the textbook "fixes one thing, creates another" case: I traded a style-signal blind spot (ordinary AI text reading as human) for more exposure to the model-signal's blind spot (plain informational human text reading as AI).


## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

**Criterion 2 (score spread, still MISSED at 16.6 of 30 points):** No amount of reweighting closes this without breaking Criterion 1 — I proved that with the sweep in "What I changed" before touching config.py, so I stopped here rather than keep nudging the same two numbers. Closing it for real needs a signal that separates the classes on *this specific kind of text* (plain, well-formed, informational prose) better than either existing signal does alone — which is a new-signal problem, the same category of work as Stretch Features' `pattern_signal`, not a reweighting problem. I'd want a second calibration pass with a larger, more varied AI sample set before trusting any specific new number, since 5 samples from one prompt is a thin basis to design a new signal against.

**Criterion 5 (bad input, still MISSED, 3/4):** Untouched by this change on purpose — it's a route-stage bug (`_validate_text` has no upper bound on `text` length), unrelated to the combining-rule mechanism this improvement targeted. I picked one change and followed it; fixing this is the obvious next pass (add a max-length check to `_validate_text`, matching `RQ07`'s missing payload-shape check while I'm in that function) but doing it in the same round would have made it impossible to tell which change moved which number.

**EV01, EV05, EV08 (evasion, still BROKE):** All three still land `human` after the reweight — closer to the 0.55 line (0.47, 0.35, 0.47) but not across it. Typos (EV01), heavy editing (EV05), and short text (EV08) all still leave style_score near its neutral midpoint, and the new 0.40 weight is still enough to hold the combined score under the threshold when model_score isn't also very high on that specific sample. A further reweight in the same direction is exactly the move that just cost Criterion 1 headroom and produced FP05 — I'm stopping rather than keep pulling the one lever that's already shown its cost.

**FP05 (false_positive, newly BROKE by this change):** Named and accepted above as the direct cost of the reweight, not something I'd patch by reversing it — reversing it reopens Criterion 3. Living with one specific new false-positive risk (dense technical writing) in exchange for label coverage and a narrower evasion attack surface is the trade I made; see below for why I'd make it again.

**The trade I'd make if this ran for real:**

I'd keep the reweight. Widening exposure to signal one's blind spot (plain, information-dense human writing read as "predictable") cost one new miscall in this test — FP05 — but fixed a mechanism that was silently letting AI text through on ordinary evasion (typos, editing, short text) and made `ai` structurally unreachable for a whole class of unremarkable AI-generated prose. A detector that can never say "ai" isn't a cautious detector, it's a broken one wearing caution as an excuse. The people who pay for this specific trade are writers of dense, plain, technical prose (FP05's category) — a real and identifiable group, not a diffuse one — who now have a higher chance of landing in "unsure" or worse on writing that happens to compress well to a language model. That's a cost worth stating plainly, not one worth reversing: unsure still isn't an accusation, and the alternative (0.30/0.55) was actively worse on the metric this whole project says matters most — letting AI text past undetected because it happened to be shaped ordinarily.

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
