"""
Signal three: the sentence-pattern signal.

Signal one reads for predictability. Signal two reads shape. This one reads
for a specific set of *rhetorical structures* — not words, sentence
skeletons — that show up disproportionately in AI-written content: a
contrastive "it's not X, it's Y" pair, a short declarative sentence answering
its own rhetorical question, a run of clipped fragments used for emphasis.

    from phrasing import pattern_signal
    score = pattern_signal("some text")   # 0.0 human-ish ... 1.0 AI-ish

This replaces an earlier version of this module that matched a fixed list of
stock phrases ("delve into", "it's important to note that", …). That
approach was built, tested against two hand-written calibration sets and
four real chatbot completions, and scored **zero hits on every single
sample** — AI and human alike — across five separate test passes. The
phrase list only fired on text written specifically to contain its own
keywords (a demo sentence, or AI content-marketing copy), and never on the
kind of plain informational chatbot completions this service is actually
likely to see. A signal that only detects the test cases built to trigger
it is not a signal; the whole module was rebuilt around sentence structure
instead of vocabulary specifically to avoid ending up back in that trap. See
README's Stretch Features for the phrase-list numbers.

⚠️ The blind spot. These are legitimate rhetorical devices — real writers,
especially anyone doing persuasive or opinion writing, use short parallel
fragments and contrastive pairs on purpose. A human copywriter's "Not louder.
Clearer." is structurally identical to what this signal flags. The pattern
is disproportionately common in AI output, not exclusive to it — same shape
of blind spot as the two signals it joins, just triggered by structure
instead of predictability or vocabulary. And like the phrase list before it,
it is easy to defeat on purpose: writing in longer, non-parallel sentences
defeats every pattern here with no loss of meaning.
"""

import re

from stylometry import sentences

# Each pattern matches a rhetorical structure, not a fixed phrase — e.g. "It's
# not about X, it's about Y" matches with any X and Y, not just one example.
# Deliberately built as regexes over open slots rather than a longer keyword
# list, because the keyword-list approach (tested and rejected — see the
# module docstring) only catches AI text that happens to reuse the exact
# vocabulary in the list. A structural pattern catches the device regardless
# of topic or wording.
_CONTRASTIVE_PATTERNS = [
    re.compile(r"\bit'?s not about\b.{2,60}?,?\s*it'?s about\b", re.IGNORECASE),
    re.compile(r"\bit'?s not just\b.{2,40}?[.!]\s*it'?s\b", re.IGNORECASE),
    re.compile(r"\bthat'?s not\b.{2,40}?,\s*that'?s\b", re.IGNORECASE),
    re.compile(r"\bnot because\b.{2,60}?[.!]\s*but because\b", re.IGNORECASE),
    re.compile(r"\bnot by\b.{2,40}?,\s*but by\b", re.IGNORECASE),
    # A "no X. no X. just Z." pattern was tried here and dropped. Every
    # variant tested (requiring a period instead of a comma, anchoring "no"
    # to a sentence start) matched an AI-style "No fluff. No filler. Just
    # results." exactly as often as it matched ordinary speech — "No milk.
    # No eggs. Just bread on the list." and "No thanks. No worries. Just
    # fine, thanks for checking in." both matched every variant tried. The
    # device is real, but nothing distinguishes it from ordinary short
    # sentences using structure alone; a keyword list would be needed to
    # separate them, which is the approach this module was already built to
    # avoid. Left out rather than shipped with a false confidence in the
    # comment explaining why it's safe.
    #
    # "The result? Higher engagement." — the tell is answering the question
    # with an immediate short (1-4 word) fragment, not a full sentence. A
    # real "What's the result? A modest improvement in accuracy, nothing
    # dramatic." keeps going in ordinary prose and must NOT match — the
    # length cap and required terminator right after the fragment are what
    # keep this pattern from firing on plain rhetorical questions.
    re.compile(r"\bthe result\?\s*(?:\w+\s+){0,3}\w+[.!]", re.IGNORECASE),
    re.compile(r"\band the\s+\w+(?:\s+\w+){0,3}\?\s*(?:\w+\s+){0,3}\w+[.!]", re.IGNORECASE),
]


def contrastive_hits(text: str) -> int:
    """How many "it's not X, it's Y"-style contrastive pairs appear."""
    return sum(len(p.findall(text)) for p in _CONTRASTIVE_PATTERNS)


def fragment_run_count(text: str) -> int:
    """
    How many runs of 3+ short (1-3 word) declarative sentence fragments in a
    row — "Focused. Aligned. Measurable." — appear.

    Counts runs, not individual fragments, so one long stretch of clipped
    sentences counts once rather than once per fragment. A single short
    sentence (a real, ordinary "No.") isn't evidence of anything on its
    own — this only fires on 3 or more in immediate succession.

    A bare list numeral ("1.", "2.") counts as its own "sentence" under
    `stylometry.sentences`'s splitter, which would otherwise make an
    ordinary numbered list ("1. Fast. 2. Cheap. 3. Reliable.") look like a
    run of AI-style fragments. Requiring at least one alphabetic word rules
    that out — a numeral alone isn't a declarative fragment, it's list
    punctuation.
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

    Two structural counts, combined: contrastive pairs ("it's not X, it's
    Y") and runs of clipped declarative fragments. Either alone is a real
    tell; either can also happen once in ordinary persuasive writing, so
    this only climbs toward 1.0 once several instances appear rather than
    saturating on a single occurrence — a single "No. Just execution." from
    a real copywriter shouldn't outweigh a whole submission's context.

    Zero hits scores 0.0. Unlike `stylometry.punctuation_density`, absence
    of these patterns is not a trap — plain writing that never sets up a
    contrastive pair is exactly the ordinary case, not a gap to protect
    against.
    """
    hits = contrastive_hits(text) + fragment_run_count(text)
    if hits == 0:
        return 0.0

    # Two occurrences of either pattern in one submission is already a
    # meaningful density for a device that's rare in ordinary prose; three
    # or more is saturation.
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
