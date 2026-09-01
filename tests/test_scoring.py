"""
The combining rule and the labelling rule.

These run against the real functions and the real configured weights, so a
weight or threshold change that breaks an invariant fails here rather than
silently changing what the service tells writers.
"""

import pytest

from authentiwrite import config, scoring


# ── combine_signals ───────────────────────────────────────────────────────────


def test_weights_sum_to_one():
    """
    If the weights don't add up to 1.0, the combined score no longer covers
    the same range as its inputs. combine_signals(1, 1, 1) would stop coming
    out at 1.0, and every threshold in config.py would quietly start meaning
    something different.
    """
    total = (
        config.WEIGHT_MODEL_SIGNAL
        + config.WEIGHT_STYLE_SIGNAL
        + config.WEIGHT_PATTERN_SIGNAL
    )
    assert total == pytest.approx(1.0)


@pytest.mark.parametrize("value", [0.0, 0.25, 0.5, 1.0])
def test_unanimous_signals_return_that_value(value):
    """Three signals that agree exactly should combine to what they agree on."""
    assert scoring.combine_signals(value, value, value) == pytest.approx(value)


def test_output_stays_within_input_range():
    """A weighted average can never leave the span of its inputs."""
    combined = scoring.combine_signals(0.2, 0.9, 0.4)
    assert 0.2 <= combined <= 0.9


def test_pattern_score_defaults_to_zero():
    """Two-signal callers still work, and get the same answer as passing 0.0."""
    assert scoring.combine_signals(0.8, 0.4) == scoring.combine_signals(0.8, 0.4, 0.0)


def test_each_signal_moves_the_score_in_the_same_direction():
    """
    All three signals run "higher = more likely AI". A signal wired backwards
    would still produce a plausible-looking number, so check the direction of
    each one independently.
    """
    base = scoring.combine_signals(0.5, 0.5, 0.5)
    assert scoring.combine_signals(0.9, 0.5, 0.5) > base
    assert scoring.combine_signals(0.5, 0.9, 0.5) > base
    assert scoring.combine_signals(0.5, 0.5, 0.9) > base


# ── score_to_label ────────────────────────────────────────────────────────────


def test_thresholds_leave_a_real_unsure_band():
    """If the thresholds ever cross or meet, "unsure" stops being reachable."""
    assert config.HUMAN_THRESHOLD < config.AI_THRESHOLD


@pytest.mark.parametrize(
    "score, expected",
    [
        (0.0, "human"),
        (config.HUMAN_THRESHOLD - 0.01, "human"),
        (config.HUMAN_THRESHOLD, "human"),
        (config.HUMAN_THRESHOLD + 0.01, "unsure"),
        (config.AI_THRESHOLD - 0.01, "unsure"),
        (config.AI_THRESHOLD, "ai"),
        (config.AI_THRESHOLD + 0.01, "ai"),
        (1.0, "ai"),
    ],
)
def test_score_maps_to_expected_guess(score, expected):
    """Both threshold boundaries, from either side."""
    guess, _ = scoring.score_to_label(score)
    assert guess == expected


def test_all_three_labels_are_reachable():
    """
    A dead band in the thresholds is the failure this catches: a label no
    score can produce is a label a writer can never be shown.
    """
    guesses = {scoring.score_to_label(s / 100)[0] for s in range(101)}
    assert guesses == {"human", "unsure", "ai"}


@pytest.mark.parametrize("score", [0.0, 0.4, 0.9])
def test_every_label_mentions_the_appeal_path(score):
    """
    Every label has to tell the reader they can push back, including the
    "human" one, which can also be wrong. See docs/DECISIONS.md.
    """
    _, label = scoring.score_to_label(score)
    assert "appeal" in label.lower()


def test_ai_label_is_hedged_not_a_verdict():
    """The AI label is the one that costs a real person credibility."""
    _, label = scoring.score_to_label(0.99)
    lowered = label.lower()
    assert "guess" in lowered
    assert "not a finding" in lowered


def test_unsure_label_says_it_is_not_an_accusation():
    _, label = scoring.score_to_label(0.5)
    assert "isn't an accusation" in label.lower()


def test_label_ranges_cover_the_configured_thresholds():
    ranges = scoring.label_ranges()
    assert len(ranges) == 3
    assert f"{config.AI_THRESHOLD:.2f}" in ranges[2][1]
