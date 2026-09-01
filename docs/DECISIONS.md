# Decisions

The significant decisions, roughly in the order they were made, with the
reasoning behind each one. The data and evidence live in
[RESEARCH.md](RESEARCH.md). This file is the why, not the numbers.

## One of the two mistakes costs more than the other

**Decision:** design every threshold and weight around avoiding false
accusations of real writers, even when that means letting more AI text
through.

**Why:** on a writing platform, wrongly telling a real person "we think
this is AI" costs that person real credibility. Missing some AI-generated
text costs the platform a little. Treating both errors as equally bad would
describe a system nobody would want to ship.

## Weighting style over the model signal (first pass: 0.35 / 0.65)

**Decision:** in the original two-signal design, give the stylometry signal
(`WEIGHT_STYLE_SIGNAL`) nearly twice the weight of the model signal
(`WEIGHT_MODEL_SIGNAL`) inside `combine_signals`.

**Why:** calibrating against 7 texts (clearly AI, clearly human, formal
human, informal human, lightly-edited AI, and so on) showed the two signals
never actually pointed in opposite directions. What they did show was that
the model signal swung much further (0.47 to 0.93) than the style signal
(0.46 to 0.70), and that it was the model signal specifically pushing
formal, literate human writing toward "AI". Weighting style higher blunted
that particular path to a false positive.

## Adding a third signal and rebalancing to 0.30 / 0.55 / 0.15

**Decision:** add `pattern_signal`, which looks for sentence structures
common in AI copy, as a third input, and rebalance to
`WEIGHT_MODEL_SIGNAL=0.30`, `WEIGHT_STYLE_SIGNAL=0.55`,
`WEIGHT_PATTERN_SIGNAL=0.15`.

**Why:** style still gets the most weight for the same reason as before.
Pattern gets the least on purpose. It only works in one register, reading
0.0 on almost anything that isn't B2B or marketing-style prose, and it has
a known partial false-positive path on writers who use short declarative
fragments deliberately. It's built to nudge the score on the specific text
it targets, not to drive the result.

## Fixing the zero case in punctuation_density

**Decision:** when `punctuation_density` is 0, meaning no semicolons,
dashes, or ellipses, which is the normal case for ordinary writing, score
it as neutral (0.5) instead of the most AI-like reading possible. Then lower
`AI_THRESHOLD` from 0.65 to 0.55 to compensate.

**Why:** a label-reachability test found that the absence of fancy
punctuation was dragging plain human writing toward "AI", which made the
high-confidence-human label impossible to reach with real text. A missing
punctuation mark isn't evidence of anything. It's just how most people
write. The fix costs some sharpness in detecting AI, since AI text often has
no fancy punctuation either, and that's the deliberate trade: blunt the
detection rather than keep punishing plain writers.

## The label wording

**Decision:** every one of the three labels mentions the appeal path, and
the AI label is hedged, saying outright that it's "a guess from automated
checks, not a finding" and that the checks are "wrong sometimes".

**Why:** this came out of reviewing a peer's project. The original wording
stopped at "we think X" with no mention of any way to push back, and the AI
label read like a flat verdict. A label with no stated way out reads as a
verdict even when it's the *good* label, because a "human" call can also be
wrong and worth appealing. This changed only the copy. No threshold or
weight moved.

The "unsure" label needed particular care to avoid sounding like a soft
accusation, so it says outright that it isn't one. The person reading it may
well have written every word themselves, and the wording has to hold up
either way.

## Rate limiting per creator_id rather than per IP, at 6 a minute and 120 a day

**Decision:** count requests against the `creator_id` in the request body,
falling back to the IP address only when the payload can't provide one.

**Why:** a script rotating `creator_id` on every request looks like a
thousand separate callers to a per-IP limiter, but it's still one caller per
`creator_id`. Counting against `creator_id` closes the one gap an attacker
can't get around by changing addresses. It also avoids lumping everyone
behind a shared household or office IP into a single bucket.

6 a minute is comfortable for a real writer resubmitting drafts, and tight
enough that mapping out the thresholds costs a script real time. 120 a day
caps even a genuinely prolific person while stopping a thousand-variation
sweep from finishing in one sitting.

## Reweighting after the attack run (0.30/0.55/0.15 to 0.45/0.40/0.15)

**Decision:** after running the attack set and the acceptance criteria,
raise `WEIGHT_MODEL_SIGNAL` to 0.45 and drop `WEIGHT_STYLE_SIGNAL` to 0.40,
leaving the pattern weight where it was.

**Why:** the style-heavy weighting was letting ordinary AI-generated prose
through as a matter of structure. Text scoring 0.84 to 0.91 on the model
signal, meaning genuinely predictable, would land near style's neutral
midpoint (0.42 to 0.48, because plain AI prose has no unusual *shape*) and
never cross the AI threshold. That same mechanism was behind four separate
evasion attacks and two missed acceptance criteria. Before picking new
numbers, every weighting was tested against the 15-sample calibration set to
confirm that no combination clears the score-spread target without also
creating a false positive. Both the fix and its ceiling were measured rather
than guessed.

**The cost, accepted on purpose:** one previously correct "unsure" call, on
dense real technical documentation, flipped to a wrong "ai". That is the
direct result of giving the model signal more weight, since its own blind
spot, reading plain information-dense writing as predictable, now has more
say. [RESEARCH.md](RESEARCH.md) has the full before and after numbers, and
[ARCHITECTURE.md](ARCHITECTURE.md) explains why the trade was kept rather
than reversed.

## Per-creator reputation instead of a "verified human" badge

**Decision:** build a reputation tally (`creators.py`), which is a running
count of what this service's own three signals have said about a
`creator_id` over time, rather than a real identity credential.

**Why:** a real "verified human" badge requires answering a hard design
question. Does an appeal from years ago excuse today's text? Does a
first-time writer get penalised by default? That deserves its own
investigation. What shipped is smaller and more honest. It never touches the
score or the label. It just shows the service's own track record back to the
reader as a `creator_note` string, so a person can weigh it instead of
having the service decide quietly. "Verified" here means this service's own
past guesses lean human, worked out fresh from the counts rather than stored
as a trust flag, and it is not a claim about anyone's identity.

## Two third-signal candidates that were rejected

**Decision:** don't ship a keyword or stock-phrase list, and don't ship a
burstiness signal based on perplexity variance.

**Why:** the keyword list scored zero hits across five test passes against
real chatbot completions and calibration text. It only fired on text written
specifically to contain its own trigger phrases, which makes it a mirror
rather than a signal. The burstiness signal did have real directional
signal, with AI samples averaging a coefficient of variation around 0.55
against roughly 0.84 for human samples, but one real human sample, a piece
of formal academic writing, scored as more machine-uniform than every AI
sample tested. That is exactly the false-positive failure this whole project
exists to avoid. Both investigations are kept in the codebase and written up
in full in [RESEARCH.md](RESEARCH.md), because a negative result on real
data is still evidence.
