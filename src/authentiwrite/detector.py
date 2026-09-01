"""
Signal one: the model signal. Runs a language model on this machine and
scores how predictable the text is (perplexity), as a 0-1 score where higher
means more likely AI.

    from authentiwrite.detector import model_signal
    score = model_signal("some text")     # 0.0 human-ish ... 1.0 AI-ish

Everything runs locally. No account and no key.

Blind spot: predictable is not the same as machine-written. This signal
treats common words in short, plain sentences as AI-like, which unfairly
catches plain writers and people writing in a second language who stick to
safe vocabulary. It does the reverse too, reading rare words and ornate
prose as human even when AI wrote it. docs/ARCHITECTURE.md covers how this
blind spot is balanced against the other two signals.
"""

import math

from . import config

_model = None
_tokenizer = None


class DetectorUnavailable(RuntimeError):
    """The model couldn't be loaded. Either it hasn't downloaded, or there's no disk."""


def _load():
    """Load the model once and keep it. The first call downloads about 550 MB."""
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer

    try:
        import torch  # noqa: F401
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise DetectorUnavailable(
            f"transformers or torch isn't installed ({exc}).\nRun: pip install -e ."
        ) from exc

    try:
        _tokenizer = AutoTokenizer.from_pretrained(config.DETECTOR_MODEL)
        _model = AutoModelForCausalLM.from_pretrained(config.DETECTOR_MODEL)
        _model.eval()
    except Exception as exc:  # noqa: BLE001
        raise DetectorUnavailable(
            f"Couldn't load '{config.DETECTOR_MODEL}': {exc}\n"
            f"The first run downloads about 550 MB. Check your connection and "
            f"that you have disk space free."
        ) from exc

    return _model, _tokenizer


def perplexity(text: str) -> float:
    """
    How surprised the model is by this text. Lower means more predictable.

    Returns a positive number. Values usually land somewhere between 10 and
    200, but that range shifts with topic and length. That's one reason the
    raw number isn't what gets scored.
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
        raise ValueError("Text is too short to score. A few sentences at least.")

    with torch.no_grad():
        output = model(input_ids, labels=input_ids)

    # The model's loss here IS mean negative log-likelihood per token.
    return float(math.exp(output.loss.item()))


def model_signal(text: str) -> float:
    """
    The signal, as a 0-1 score. **Higher means more likely AI.**

    Perplexity has no upper limit and is roughly log-distributed, so it gets
    squashed onto 0-1 with a logistic curve instead of being clipped.
    `midpoint` is the perplexity value that comes out as 0.5.
    """
    ppl = perplexity(text)

    midpoint = 45.0  # perplexity that scores 0.5
    steepness = 1.6  # how sharply the score moves either side of it

    # Logistic on log-perplexity. Low perplexity gives a high AI score.
    score = 1.0 / (1.0 + (ppl / midpoint) ** steepness)
    return round(min(max(score, 0.0), 1.0), 4)


def burstiness_signal(text: str) -> float:
    """
    Not used. Kept as the record of a third-signal candidate that was tested
    and dropped. See docs/RESEARCH.md. The live third signal is
    phrasing.pattern_signal, which is what combine_signals and /submit use.

    This measures whether predictability swings from sentence to sentence or
    stays flat (the coefficient of variation of per-sentence perplexity),
    rather than the average level that model_signal measures. It was dropped
    because one real human sample, a piece of formal academic writing, came
    out looking more machine-uniform than every AI sample tested.
    docs/RESEARCH.md has the numbers.

    Text with fewer than two scorable sentences returns a neutral 0.5, since
    having no measurable spread isn't evidence either way.
    """
    import statistics

    from .stylometry import sentences as split_sentences

    parts = split_sentences(text)
    per_sentence = []
    for s in parts:
        try:
            per_sentence.append(perplexity(s))
        except ValueError:
            continue  # too short to score on its own, so skip it rather than crash

    if len(per_sentence) < 2:
        return 0.5

    mean = statistics.mean(per_sentence)
    if mean == 0:
        return 0.5

    coefficient_of_variation = statistics.stdev(per_sentence) / mean

    # A coefficient of variation of 1.2 or higher means a lot of swing between
    # sentences. That cap is a similar size to sentence_length_spread's cap in
    # stylometry.py, and was picked the same way: run real text through it and
    # see where human and AI samples actually separate.
    spread = min(coefficient_of_variation, 1.2) / 1.2

    # Higher spread means more human, so flip it to match the direction the
    # other two signals use, where higher means more likely AI.
    score = 1.0 - spread
    return round(min(max(score, 0.0), 1.0), 4)


def warm_up() -> str:
    """Load the model without scoring anything, for example to pre-download it."""
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
        print("(no text given, so scoring a sample)\n")

    print(f"Loading {config.DETECTOR_MODEL} (the first run downloads about 550 MB)...")
    print(f"perplexity     {perplexity(text):.1f}")
    print(f"model_signal   {model_signal(text):.4f}   (higher = more likely AI)")
