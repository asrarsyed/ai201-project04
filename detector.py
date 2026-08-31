"""
Signal one: the model signal.

This is the signal that "reads the text for meaning". It runs a language model
on your own machine and asks one question: **how predictable is this text?**

The idea is the one every AI-detection product is built on. A language model
writes by repeatedly picking a likely next word, so text a model produced tends
to be text a model finds easy to predict. Human writing wanders more — odd word
choices, abrupt turns, the specific rather than the typical.

The measure is called **perplexity**. Low perplexity means "I could have
guessed this"; high perplexity means "that surprised me". This module turns
that into a 0–1 score where **higher means more likely AI**.

    from detector import model_signal
    score = model_signal("some text")     # 0.0 human-ish … 1.0 AI-ish

Everything runs locally. No account, no key, no card.

⚠️ **The blind spot, which you have to name in Milestone 1.**

Predictability is not the same thing as authorship. What this signal actually
rewards is **common words in short, ordinary sentences** — and plenty of real
people write that way.

Someone writing in a second language, sticking to vocabulary they're sure of.
A younger writer. Anyone writing plainly on purpose. Measured against gpt2,
writing like that scores about as machine-like as machine writing does.

The reverse trips people up too: dense, ornate prose full of rare words often
scores as *human* on this signal, because rare words are exactly what a
language model fails to predict. Formality on its own doesn't decide it.

So the writers this signal is most likely to accuse are the ones with the
least room to argue back. That is structural rather than a bug you can fix,
and it is the person Milestone 1 asks you to follow through your service.

Don't take that on trust — it's a claim you can check. Milestone 4 has you run
four calibration inputs. Add a plainly-written human paragraph to them and see
for yourself where it lands.
"""

import math

import config

_model = None
_tokenizer = None


class DetectorUnavailable(RuntimeError):
    """The model couldn't be loaded — no download yet, or no disk."""


def _load():
    """Load the model once and keep it. First call downloads ~550 MB."""
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer

    try:
        import torch  # noqa: F401
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise DetectorUnavailable(
            f"transformers or torch isn't installed ({exc}).\nRun: pip install -r requirements.txt"
        ) from exc

    try:
        _tokenizer = AutoTokenizer.from_pretrained(config.DETECTOR_MODEL)
        _model = AutoModelForCausalLM.from_pretrained(config.DETECTOR_MODEL)
        _model.eval()
    except Exception as exc:  # noqa: BLE001
        raise DetectorUnavailable(
            f"Couldn't load '{config.DETECTOR_MODEL}': {exc}\n"
            f"The first run downloads about 550 MB — check your connection and "
            f"that you have disk space free."
        ) from exc

    return _model, _tokenizer


def perplexity(text: str) -> float:
    """
    How surprised the model is by this text. Lower means more predictable.

    Returns a positive number. Typical values land roughly between 10 and 200,
    but that range shifts with topic and length, which is one reason the raw
    number isn't what you score on.
    """
    import torch

    model, tokenizer = _load()

    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=config.DETECTOR_MAX_TOKENS,
    )
    input_ids = encoded["input_ids"]

    # Two tokens is not enough to be surprised by anything.
    if input_ids.shape[1] < 3:
        raise ValueError("Text is too short to score — a few sentences at least.")

    with torch.no_grad():
        output = model(input_ids, labels=input_ids)

    # The model's loss here IS mean negative log-likelihood per token.
    return float(math.exp(output.loss.item()))


def model_signal(text: str) -> float:
    """
    The signal, as a 0–1 score. **Higher means more likely AI.**

    Perplexity is unbounded and roughly log-distributed, so it gets squashed
    onto 0–1 rather than clipped. The midpoint below is the perplexity that
    maps to 0.5 — text this surprising is a coin flip.

    You may want to move that midpoint once you've run the four calibration
    inputs in Milestone 4 and seen what your own text actually scores. If you
    do, say so in your README: it's a scoring decision, not a detail.
    """
    ppl = perplexity(text)

    midpoint = 45.0  # perplexity that scores 0.5
    steepness = 1.6  # how sharply the score moves either side of it

    # Logistic on log-perplexity. Low perplexity -> high AI score.
    score = 1.0 / (1.0 + (ppl / midpoint) ** steepness)
    return round(min(max(score, 0.0), 1.0), 4)


def burstiness_signal(text: str) -> float:
    """
    ⚠️ NOT WIRED INTO SCORING. Kept as a documented, tested, and rejected
    third-signal candidate — see README's Stretch Features. `combine_signals`
    and `/submit` use `phrasing.pattern_signal` as the live third signal
    instead. This function is not called anywhere in the running service.

    What it measured: how *consistent* the text's per-sentence
    predictability is, not how predictable it is on average.

    `model_signal` scores the level — is this text predictable overall.
    This scores the variance — does the predictability swing sentence to
    sentence, or stay flat. Human writing tends to alternate between easy,
    throwaway sentences and harder, denser ones; generated text tends to
    hold a locally uniform difficulty even as topic shifts. That's a
    genuinely different property from the level `model_signal` already
    measures, which is why it's a third signal rather than a restatement of
    the first: a plain-spoken, low-average-perplexity human paragraph can
    still have high burstiness, and this signal is the only one of the
    three that would catch that.

    Reuses the same model as `model_signal` — no new dependency, but one
    forward pass per scorable sentence instead of one pass total, so this is
    the slowest of the three signals on a long submission.

    Returns:
        A float from 0.0 (bursty, human-ish) to 1.0 (uniform, AI-ish).

    ⚠️ The blind spot: a short submission doesn't have enough sentences to
    have a meaningful variance at all. Fewer than two scorable sentences
    returns a neutral 0.5 — same reasoning as `stylometry.punctuation_density`'s
    fix: absence of measurable spread isn't evidence of anything, and scoring
    it as maximally AI-ish or maximally human-ish would make one of the three
    labels unreachable on short, ordinary submissions. A submission written
    entirely in one register on purpose (a single long uniform paragraph, or
    a list of short similar sentences) will also read as low-burstiness
    here even from a real person — consistency of *tone* isn't the same
    thing as being AI-written, and this signal can't tell those apart.
    """
    import statistics

    from stylometry import sentences as split_sentences

    parts = split_sentences(text)
    per_sentence = []
    for s in parts:
        try:
            per_sentence.append(perplexity(s))
        except ValueError:
            continue  # too short to score on its own — skip, don't crash

    if len(per_sentence) < 2:
        return 0.5

    mean = statistics.mean(per_sentence)
    if mean == 0:
        return 0.5

    coefficient_of_variation = statistics.stdev(per_sentence) / mean

    # Coefficient of variation of 1.2 or higher is a lot of swing between
    # sentences — comparable magnitude to sentence_length_spread's cap in
    # stylometry.py, picked the same way: run real text through it and see
    # where human and AI samples actually separate.
    spread = min(coefficient_of_variation, 1.2) / 1.2

    # Higher spread means more human, so flip to match the other two
    # signals' "higher = more likely AI" direction.
    score = 1.0 - spread
    return round(min(max(score, 0.0), 1.0), 4)


def warm_up() -> str:
    """Load the model without scoring anything. Run this before class."""
    _load()
    return f"{config.DETECTOR_MODEL} loaded and ready."


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = (
            "The implementation of the proposed framework requires careful "
            "consideration of several key factors. First, it is important to "
            "note that the system must be able to handle a wide variety of "
            "different inputs. Additionally, the overall performance of the "
            "solution depends on a number of important variables."
        )
        print("(no text given — scoring a sample)\n")

    print(f"Loading {config.DETECTOR_MODEL} (first run downloads ~550 MB)…")
    print(f"perplexity     {perplexity(text):.1f}")
    print(f"model_signal   {model_signal(text):.4f}   (higher = more likely AI)")
