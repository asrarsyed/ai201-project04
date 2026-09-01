"""
The model signal's squashing curve.

`perplexity()` is stubbed all the way through. Loading gpt2 costs about 550 MB
and seconds per call, and what's worth testing here is the logistic curve that
turns an unlimited perplexity value into a 0-1 score. That part is arithmetic.
Scoring real text with the real model is what scripts/run_eval.py is for.
"""

import importlib.util

import pytest

from authentiwrite import detector


@pytest.fixture
def stub_perplexity(monkeypatch):
    """Drive model_signal with a chosen perplexity instead of a real model."""

    def _set(value):
        monkeypatch.setattr(detector, "perplexity", lambda text: value)

    return _set


def test_low_perplexity_scores_ai_ish(stub_perplexity):
    """Predictable text is what this signal reads as machine written."""
    stub_perplexity(5.0)
    assert detector.model_signal("anything") > 0.8


def test_high_perplexity_scores_human_ish(stub_perplexity):
    stub_perplexity(400.0)
    assert detector.model_signal("anything") < 0.2


def test_the_midpoint_scores_one_half(stub_perplexity):
    """The documented midpoint (45.0) is what maps to 0.5."""
    stub_perplexity(45.0)
    assert detector.model_signal("anything") == pytest.approx(0.5, abs=1e-3)


def test_the_curve_is_monotonic(stub_perplexity):
    """
    More surprising text must never score as more AI-like. A flipped sign in
    the logistic would still hand back believable numbers between 0 and 1,
    which is exactly why this needs checking.
    """
    scores = []
    for ppl in (1.0, 10.0, 45.0, 100.0, 1000.0):
        stub_perplexity(ppl)
        scores.append(detector.model_signal("anything"))
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize("ppl", [0.001, 1.0, 45.0, 10_000.0])
def test_the_score_stays_bounded_for_extreme_perplexity(stub_perplexity, ppl):
    """Perplexity has no upper limit. The signal it feeds must have one."""
    stub_perplexity(ppl)
    score = detector.model_signal("anything")
    assert 0.0 <= score <= 1.0


@pytest.mark.skipif(
    importlib.util.find_spec("torch") is None,
    reason="perplexity() imports torch directly; the rest of the suite stubs it out",
)
def test_text_too_short_to_score_raises(monkeypatch):
    """
    Fewer than three tokens can't be surprising. The route already rejects
    short text before it gets this far, but the signal still refuses rather
    than making up a number.
    """

    class _Tokenizer:
        def __call__(self, text, **kwargs):
            class _Shape:
                shape = (1, 2)

            return {"input_ids": _Shape()}

    monkeypatch.setattr(detector, "_load", lambda: (object(), _Tokenizer()))
    with pytest.raises(ValueError, match="too short"):
        detector.perplexity("hi")
