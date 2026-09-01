"""
Signal two: the style signal. Looks at text as text, measuring its shape
rather than its meaning, using three measures:

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

style_signal() folds those into one 0-1 score pointing the same way as
detector.model_signal, where higher means more likely AI.

Blind spot: this signal cannot read. It has no idea what the text says, so
anything that changes the shape without changing the substance moves the
score. Typos do it, so do broken-up sentences and a pasted quotation. All of
those are cheap to do on purpose. See docs/ARCHITECTURE.md.

    python -m authentiwrite.stylometry "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences on terminal punctuation. Rough, and good enough."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures ────────────────────────────────────────────────────────


def sentence_length_spread(text: str) -> float:
    """
    Standard deviation of sentence length in words, divided by the mean so
    that texts of different lengths can be compared. Higher means more human,
    since generated prose tends toward even, mid-length sentences.

    Text with fewer than two sentences has no spread to measure, so it
    returns 0.0, which is the most AI-like reading on this measure. That is a
    known rough edge: short text gets treated as machine-like for no better
    reason than being short.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    if len(lengths) < 2:
        return 0.0

    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0

    return statistics.stdev(lengths) / mean


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words, from 0 to 1. Higher means more varied
    vocabulary. This falls as text gets longer, because common words repeat,
    so texts of very different lengths can't be compared on this measure by
    itself.
    """
    tokens = words(text)
    if not tokens:
        return 0.0

    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    How many semicolons, colons, dashes, and ellipses appear relative to word
    count. Those marks vary more from writer to writer than full stops do,
    which is why the measure counts only them.
    """
    tokens = words(text)
    if not tokens:
        return 0.0

    marks = re.findall(r"[;:—–]|\.\.\.", text)
    return len(marks) / len(tokens)


# ── Combining them ───────────────────────────────────────────────────────────


def style_signal(text: str) -> float:
    """
    Folds the three measures into one 0-1 score where higher means more
    likely AI. That's the same direction detector.model_signal uses, so
    scoring.combine_signals can average them directly. Each raw measure runs
    the other way, where higher means more human, so each one gets flipped
    and scaled before being averaged.
    """
    spread = min(sentence_length_spread(text), 0.8) / 0.8
    ttr = type_token_ratio(text)

    # Having no semicolons, dashes, or ellipses is the normal case for plain
    # writing, whether a person or a machine wrote it. It isn't evidence of
    # anything, so it scores a neutral 0.5 rather than flipping all the way to
    # "most AI-like". Only actually using that punctuation moves this measure,
    # and it moves it toward "more human".
    punct_raw = punctuation_density(text)
    punct = 0.5 if punct_raw == 0 else 1.0 - min(punct_raw, 0.3) / 0.3

    # All three raw measures run "higher = more human", which is the opposite
    # of model_signal, so each one gets flipped before averaging.
    ai_ish = ((1.0 - spread) + (1.0 - ttr) + punct) / 3.0
    return round(min(max(ai_ish, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
