"""
The style and pattern signals, and the shared contract all three signals hold.

The model signal isn't tested here, because it loads about 550 MB and takes
seconds per call. Its arithmetic, a logistic curve over perplexity, is checked
in test_model_signal.py using a stubbed perplexity value, so the curve gets
covered without the download.
"""

import pytest

from authentiwrite import phrasing, stylometry


# ── stylometry: the measures ──────────────────────────────────────────────────


def test_sentence_length_spread_is_zero_for_a_single_sentence():
    """One sentence has no spread to measure, so it returns 0.0 as documented."""
    assert stylometry.sentence_length_spread("Just the one sentence here.") == 0.0


def test_sentence_length_spread_rises_with_uneven_sentences():
    even = "One two three four. Five six seven eight. Nine ten eleven twelve."
    uneven = "Short. This sentence goes on considerably longer than the one before it did."
    assert stylometry.sentence_length_spread(uneven) > stylometry.sentence_length_spread(even)


def test_type_token_ratio_is_one_when_no_word_repeats():
    assert stylometry.type_token_ratio("alpha beta gamma delta") == pytest.approx(1.0)


def test_type_token_ratio_falls_when_words_repeat():
    assert stylometry.type_token_ratio("word word word word") == pytest.approx(0.25)


def test_measures_handle_empty_text_without_raising():
    """Empty text is rejected at the route, but a signal must not crash on it."""
    assert stylometry.type_token_ratio("") == 0.0
    assert stylometry.punctuation_density("") == 0.0
    assert stylometry.sentence_length_spread("") == 0.0


def test_punctuation_density_counts_only_the_varied_marks():
    """Full stops are left out on purpose, since they vary little between writers."""
    assert stylometry.punctuation_density("One. Two. Three. Four.") == 0.0
    assert stylometry.punctuation_density("One; two; three; four") > 0.0


# ── stylometry: the combined signal ───────────────────────────────────────────


def test_style_signal_stays_in_range():
    for text in ["Short. Text.", "A" * 500, "One two three four five six seven."]:
        assert 0.0 <= stylometry.style_signal(text) <= 1.0


def test_absent_punctuation_scores_neutral_not_maximally_ai():
    """
    This project already shipped this bug once. Scoring "no semicolons" as
    the most AI-like reading possible made the high-confidence-human label
    impossible to reach with ordinary writing. A missing punctuation mark is
    not evidence of anything. See docs/DECISIONS.md.
    """
    plain = "The dog sat on the mat. Then it went outside to look around the yard."
    assert stylometry.punctuation_density(plain) == 0.0
    # With the punctuation measure pinned neutral, the whole signal must not
    # saturate toward 1.0 on text whose only quirk is ordinary punctuation.
    assert stylometry.style_signal(plain) < 0.75


# ── phrasing ──────────────────────────────────────────────────────────────────


def test_plain_prose_scores_zero():
    """Zero hits means 0.0. Unlike punctuation, an absence here isn't a trap."""
    plain = (
        "The meeting is on Thursday at two. I booked the small room because "
        "the large one was already taken by the design team."
    )
    assert phrasing.pattern_signal(plain) == 0.0


def test_contrastive_pair_is_detected():
    assert phrasing.contrastive_hits("It's not about posting more. It's about posting smarter.") > 0


def test_contrastive_patterns_match_structure_not_fixed_wording():
    """
    The whole reason this signal replaced a keyword list: it has to fire on
    the device regardless of the nouns filling its slots.
    """
    assert phrasing.contrastive_hits("It's not about speed, it's about accuracy.") > 0
    assert phrasing.contrastive_hits("It's not about money, it's about principle.") > 0


def test_fragment_run_needs_three_in_a_row():
    """One or two short sentences is ordinary writing, not a tell."""
    assert phrasing.fragment_run_count("No. Really.") == 0
    assert phrasing.fragment_run_count("Focused. Aligned. Measurable.") == 1


def test_numbered_list_is_not_counted_as_a_fragment_run():
    """
    A bare numeral splits as its own "sentence", which would make an ordinary
    numbered list look like a run of AI-style fragments. Documented in
    phrasing.fragment_run_count.
    """
    assert phrasing.fragment_run_count("1. Fast. 2. Cheap. 3. Reliable.") == 0


def test_rhetorical_question_answered_in_full_prose_does_not_match():
    """
    The length cap is what separates "The result? Higher engagement." from a
    real question answered in ordinary prose.
    """
    real = (
        "What's the result? A modest improvement in accuracy, nothing "
        "dramatic, and it took three weeks to get there."
    )
    assert phrasing.contrastive_hits(real) == 0


def test_pattern_signal_saturates_rather_than_spiking_on_one_hit():
    """One device from a real copywriter shouldn't outweigh a whole submission."""
    one = "It's not about speed, it's about accuracy."
    assert 0.0 < phrasing.pattern_signal(one) < 1.0


def test_pattern_signal_stays_in_range():
    heavy = (
        "It's not about posting more. It's about posting smarter. Not because "
        "it's easy. But because it works. Focused. Aligned. Measurable. "
        "The result? Higher engagement."
    )
    assert phrasing.pattern_signal(heavy) == pytest.approx(1.0)


# ── the contract all three share ──────────────────────────────────────────────


@pytest.mark.parametrize(
    "signal",
    [stylometry.style_signal, phrasing.pattern_signal],
    ids=["style", "pattern"],
)
@pytest.mark.parametrize(
    "text",
    ["Three short words.", "word " * 300, "Unicode ✓ emoji 🙂 and ümlauts."],
    ids=["short", "long", "unicode"],
)
def test_signals_return_a_bounded_float(signal, text):
    score = signal(text)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
