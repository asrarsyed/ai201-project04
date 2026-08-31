"""
Turning two numbers into one, and one number into something a person can read.
← YOU BUILD THIS IN MILESTONES 4 AND 5

Two functions live here, and both are stubs.

`combine_signals` is where your false-positive decision from Milestone 1
actually gets made. Everything above it — the labels, the appeal path — is
downstream of a number this function produced.

`score_to_label` is where you stop writing for a machine and start writing for
a person. A score of 0.62 means nothing to a writer.

⚠️ Your README's **Signals and Scoring** section has to name the file and
function holding your combining rule. The grader checks your code against what
you claim, so that line should read `scoring.py::combine_signals`.
"""

import config


def combine_signals(model_score: float, style_score: float, pattern_score: float = 0.0) -> float:
    """
    Combine three 0-1 signals into one 0-1 score.

    All three inputs point the same way: higher means more likely AI. The
    output does too. `pattern_score` (from `phrasing.pattern_signal`,
    Stretch Features) defaults to 0.0 so existing two-signal callers still
    work.

    Args:
        model_score: from `detector.model_signal` — how predictable the text is.
        style_score: from `stylometry.style_signal` — the shape of the text.
        pattern_score: from `phrasing.pattern_signal` — AI rhetorical-pattern density.

    Returns:
        A float from 0.0 (confidently human) to 1.0 (confidently AI).

    **The rule:** a weighted average, same shape as the original two-signal
    rule — see README's Signals and Scoring for the calibration behind the
    numbers. `pattern_score` was added last and given the smallest weight
    deliberately: it's the sharpest and most register-specific of the three
    (only fires on a particular rhetorical style — see phrasing.py), so it
    nudges the score rather than driving it.

    The weights live in config.py.
    """
    return (
        config.WEIGHT_MODEL_SIGNAL * model_score
        + config.WEIGHT_STYLE_SIGNAL * style_score
        + config.WEIGHT_PATTERN_SIGNAL * pattern_score
    )


def score_to_label(score: float) -> tuple[str, str]:
    """
    Turn a score into a guess and the text a reader actually sees.
    ← TODO (Milestone 5)

    Returns:
        (guess, label_text) — where `guess` is a short machine-readable string
        like "ai" / "human" / "unsure", and `label_text` is the full sentence
        shown to a person.

    ⚠️ Write the label text for someone who has never heard the word
    "threshold".

        ✗ "human, 0.81 confidence"
        ✓ "We think this was probably written by a person."

    All three labels have to be **reachable**. If no score can produce one of
    them, your ranges have a gap — and Milestone 5 asks you to submit text that
    produces each one, which is how you'd find out.

    The hardest one to write is "unsure". It has to admit uncertainty without
    sounding like an accusation, because the person reading it may well have
    written every word themselves. Your breakout asks your group what they'd
    think if they got it on their own work. That question is the whole
    milestone.
    """
    if score >= config.AI_THRESHOLD:
        return "ai", "We think this was probably written by AI."
    if score <= config.HUMAN_THRESHOLD:
        return "human", "We think this was probably written by a person."
    return "unsure", "We can't tell whether this was written by a person or by AI. This isn't an accusation — it just means our checks didn't turn up a clear answer either way."


def label_ranges() -> list[tuple[str, str]]:
    """
    The score range each label covers. Your README needs these beside the
    label text — given to you so the numbers can't drift apart from config.py.
    """
    return [
        ("high-confidence human", f"0.00 – {config.HUMAN_THRESHOLD:.2f}"),
        ("unsure", f"{config.HUMAN_THRESHOLD:.2f} – {config.AI_THRESHOLD:.2f}"),
        ("high-confidence AI", f"{config.AI_THRESHOLD:.2f} – 1.00"),
    ]
