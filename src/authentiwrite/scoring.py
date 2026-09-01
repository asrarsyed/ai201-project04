"""
Turns the three signal scores into one number (combine_signals), then turns
that number into wording a reader can understand (score_to_label). The
weights and thresholds both come from config.py. docs/DECISIONS.md explains
where those values came from.
"""

from . import config


def combine_signals(model_score: float, style_score: float, pattern_score: float = 0.0) -> float:
    """
    Weighted average of three 0-1 signals into one 0-1 score. All three
    inputs and the output point the same way: higher means more likely AI.

    Args:
        model_score: from detector.model_signal.
        style_score: from stylometry.style_signal.
        pattern_score: from phrasing.pattern_signal. Defaults to 0.0 so
            callers that only have two signals still work.

    The weights live in config.py (WEIGHT_MODEL_SIGNAL, WEIGHT_STYLE_SIGNAL,
    WEIGHT_PATTERN_SIGNAL). See docs/DECISIONS.md for how they were picked.
    """
    return (
        config.WEIGHT_MODEL_SIGNAL * model_score
        + config.WEIGHT_STYLE_SIGNAL * style_score
        + config.WEIGHT_PATTERN_SIGNAL * pattern_score
    )


def score_to_label(score: float) -> tuple[str, str]:
    """
    Turn a combined score into (guess, label_text). The guess is a short
    string for other code to read ("ai", "human", or "unsure"). The label is
    the full sentence a person sees.

    The cutoffs are config.HUMAN_THRESHOLD and config.AI_THRESHOLD. See
    docs/DECISIONS.md for why the wording reads the way it does.
    """
    if score >= config.AI_THRESHOLD:
        return "ai", (
            "We think this was probably written by AI. That's a guess from "
            "automated checks, not a finding. They're wrong sometimes. If "
            "you wrote this yourself, you can appeal and a person will look at it."
        )
    if score <= config.HUMAN_THRESHOLD:
        return "human", (
            "We think this was probably written by a person. If you think "
            "we got this wrong, you can appeal and a person will look at it."
        )
    return "unsure", (
        "We can't tell whether this was written by a person or by AI. This "
        "isn't an accusation. It just means our checks didn't turn up a "
        "clear answer either way. Nothing has been decided, and you can "
        "appeal at any time if you'd like a person to look at it."
    )


def label_ranges() -> list[tuple[str, str]]:
    """The score range each label covers, read straight from config.py."""
    return [
        ("high-confidence human", f"0.00 to {config.HUMAN_THRESHOLD:.2f}"),
        ("unsure", f"{config.HUMAN_THRESHOLD:.2f} to {config.AI_THRESHOLD:.2f}"),
        ("high-confidence AI", f"{config.AI_THRESHOLD:.2f} to 1.00"),
    ]
