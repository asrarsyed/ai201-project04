"""
Signal three: the sentence-pattern signal.

Signal one reads for predictability. Signal two reads shape. This one looks
for a specific set of sentence structures, not words, that turn up more often
in AI-written copy: a contrastive "it's not X, it's Y" pair, a short sentence
answering its own rhetorical question, a run of clipped fragments used for
emphasis.

    from authentiwrite.phrasing import pattern_signal
    score = pattern_signal("some text")   # 0.0 human-ish ... 1.0 AI-ish

An earlier version of this matched a fixed list of stock phrases ("delve
into", "it's important to note that", and so on). It scored zero hits on
every real chatbot completion tested, firing only on text written specially
to contain its own keywords. docs/RESEARCH.md has that investigation. This
version was rebuilt around sentence structure instead of vocabulary to avoid
the same trap.

Blind spot: these are ordinary rhetorical devices. Real writers use short
parallel fragments and contrastive pairs on purpose, especially in
persuasive or opinion writing. A human copywriter's "Not louder. Clearer."
has exactly the structure this signal flags. The pattern is more common in
AI output, but it isn't unique to it. That is the same shape of blind spot
the other two signals have, just triggered by structure instead of by
predictability or vocabulary. Like the phrase list before it, this is also
easy to defeat deliberately: writing in longer, non-parallel sentences
clears every pattern here without changing the meaning.
"""

import re

from .stylometry import sentences

# Each pattern matches a sentence structure rather than a fixed phrase. For
# example "It's not about X, it's about Y" matches with any X and Y, not just
# one example. These are written as regexes over open slots instead of as a
# keyword list (the approach that was rejected, see the module docstring),
# because a structural pattern catches the device whatever the topic or
# wording.
_CONTRASTIVE_PATTERNS = [
    re.compile(r"\bit'?s not about\b.{2,60}?,?\s*it'?s about\b", re.IGNORECASE),
    re.compile(r"\bit'?s not just\b.{2,40}?[.!]\s*it'?s\b", re.IGNORECASE),
    re.compile(r"\bthat'?s not\b.{2,40}?,\s*that'?s\b", re.IGNORECASE),
    re.compile(r"\bnot because\b.{2,60}?[.!]\s*but because\b", re.IGNORECASE),
    re.compile(r"\bnot by\b.{2,40}?,\s*but by\b", re.IGNORECASE),
    # A "no X. no X. just Z." pattern was tried here and dropped. Every variant
    # tested (requiring a period instead of a comma, anchoring "no" to a
    # sentence start) matched an AI-style "No fluff. No filler. Just results."
    # exactly as often as it matched ordinary speech. "No milk. No eggs. Just
    # bread on the list." and "No thanks. No worries. Just fine, thanks for
    # checking in." both matched every variant tried. The device is real, but
    # structure alone doesn't separate it from ordinary short sentences.
    # Telling them apart would need a keyword list, which is the approach this
    # module was built to avoid. Left out rather than shipped with a comment
    # claiming it was safe.
    #
    # "The result? Higher engagement." The tell is answering the question with
    # an immediate short fragment of one to four words, not with a full
    # sentence. A real "What's the result? A modest improvement in accuracy,
    # nothing dramatic." keeps going in ordinary prose and must not match. The
    # length cap and the required terminator right after the fragment are what
    # keep this pattern off plain rhetorical questions.
    re.compile(r"\bthe result\?\s*(?:\w+\s+){0,3}\w+[.!]", re.IGNORECASE),
    re.compile(r"\band the\s+\w+(?:\s+\w+){0,3}\?\s*(?:\w+\s+){0,3}\w+[.!]", re.IGNORECASE),
]


def contrastive_hits(text: str) -> int:
    """How many "it's not X, it's Y" style contrastive pairs appear."""
    return sum(len(p.findall(text)) for p in _CONTRASTIVE_PATTERNS)


def fragment_run_count(text: str) -> int:
    """
    How many runs of three or more short declarative fragments appear in a
    row, as in "Focused. Aligned. Measurable." A fragment here is one to three
    words.

    This counts runs, not individual fragments, so one long stretch of clipped
    sentences counts once instead of once per fragment. A single short
    sentence, an ordinary "No.", isn't evidence of anything by itself, so this
    only fires on three or more in immediate succession.

    A bare list numeral ("1.", "2.") counts as its own sentence under
    stylometry.sentences, which would otherwise make an ordinary numbered list
    like "1. Fast. 2. Cheap. 3. Reliable." look like a run of AI-style
    fragments. Requiring at least one alphabetic word rules that out, since a
    numeral on its own is list punctuation rather than a declarative fragment.
    """
    parts = sentences(text)
    run = 0
    runs = 0
    for s in parts:
        tokens = re.findall(r"[a-z0-9']+", s.lower())
        has_letters = any(re.search(r"[a-z]", t) for t in tokens)
        if has_letters and 1 <= len(tokens) <= 3:
            run += 1
        else:
            if run >= 3:
                runs += 1
            run = 0
    if run >= 3:
        runs += 1
    return runs


def pattern_signal(text: str) -> float:
    """
    The signal, as a 0-1 score. **Higher means more likely AI.**

    Two structural counts added together: contrastive pairs ("it's not X,
    it's Y") and runs of clipped fragments. Either one on its own is a real
    tell, but either can also show up once in ordinary persuasive writing. So
    the score only climbs toward 1.0 once several instances appear, rather
    than maxing out on a single one. A lone "No. Just execution." from a real
    copywriter shouldn't outweigh a whole submission.

    Zero hits scores 0.0. Unlike stylometry.punctuation_density, an absence
    here is not a trap: plain writing that never sets up a contrastive pair is
    the ordinary case, not a gap to protect against.
    """
    hits = contrastive_hits(text) + fragment_run_count(text)
    if hits == 0:
        return 0.0

    # Two of either pattern in one submission is already a meaningful density
    # for a device that's rare in ordinary prose. Three or more is the ceiling.
    score = min(hits, 3) / 3.0
    return round(min(max(score, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "It's not about posting more. It's about posting smarter. Not "
        "because it's easy. But because it works. Focused. Aligned. "
        "Measurable. The result? Higher engagement."
    )

    print(f"contrastive_hits    {contrastive_hits(text)}")
    print(f"fragment_run_count  {fragment_run_count(text)}")
    print(f"pattern_signal      {pattern_signal(text)}   (higher = more likely AI)")
