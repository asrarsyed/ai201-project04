# Reference

Terms used throughout these docs, then the outside sources behind them.

## Terms

**Signal** is one of the three separate measures (model, style, pattern).
Each produces a 0-1 score where higher means more likely AI.

**Model signal** is signal one. It's based on perplexity, meaning how
predictable a language model finds the text. `detector.py::model_signal`.

**Style signal** is signal two. It's based on stylometry: sentence-length
spread, vocabulary repetition, and punctuation density.
`stylometry.py::style_signal`.

**Pattern signal** is signal three. It looks for particular sentence
structures common in AI copy, namely contrastive pairs and runs of short
fragments. `phrasing.py::pattern_signal`.

**Combined score** is the single 0-1 number that comes out of
`scoring.py::combine_signals`, a weighted average of the three signals.

**Guess** is the short machine-readable outcome of a submission: `"ai"`,
`"human"`, or `"unsure"`.

**Label** is the full sentence shown to a reader for a given guess. Every
label mentions the appeal path.

**Confidence** is how far the combined score sits from 0.5, doubled so it
runs 0 to 1. It is not the combined score, and mixing the two up is a
mistake this project has already made once. See
[RESEARCH.md](RESEARCH.md).

**Blind spot** is a specific, named class of input a signal structurally
cannot tell apart from the thing it's trying to detect. Every signal here
has one, and they're written up in [ARCHITECTURE.md](ARCHITECTURE.md).

**Appeal** is a writer asking to have a decision reviewed. It moves an
item's status to `under_review` and adds a log entry without editing the
original decision.

**Content ID** is the UUID given to a submission when it's scored. It's
what you use to look the submission up (`GET /content/<id>`) or appeal it.

**Creator ID** is the identifier a caller attaches to a submission to
credit it to a writer. It's used for rate limiting and per-creator
reputation.

**Reputation**, also called the creator note, is a running tally of what
this service's own past guesses have said about a given `creator_id`,
shown as a `creator_note` string. It is not an identity check. See
[DECISIONS.md](DECISIONS.md).

**Audit log** is the append-only record of every decision, rejection, and
appeal, kept in `logs/audit.jsonl`.

**Attack set** is the structured set of adversarial inputs in
`attack_set/*.csv` used to test the service, covering evasion, false
positives, prompt injection, malformed requests, and flooding.

**Held and broke** are the two attack-run verdicts. Held means the service
behaved as intended against that attack. Broke means it didn't. A 5xx
response is always marked broke automatically. Anything else gets judged
against the thresholds in [REQUIREMENTS.md](REQUIREMENTS.md).

**Perplexity** is a language model's measure of how surprised it is by a
piece of text, and it's what the model signal is built on. Low perplexity
means predictable text.

**Type-token ratio** is unique words divided by total words. It's a
standard stylometric measure of how varied the vocabulary is, used in the
style signal.

## Data

- [allenai/c4](https://huggingface.co/datasets/allenai/c4) is a public web
  text dataset. It's the source of the 10 real human writing samples used
  in `src/authentiwrite/scenarios.py` and in the acceptance criteria in
  [REQUIREMENTS.md](REQUIREMENTS.md).

## Libraries

- [Flask](https://flask.palletsprojects.com/) runs the web service.
- [Flask-Limiter](https://flask-limiter.readthedocs.io/) does the rate
  limiting.
- [Transformers](https://huggingface.co/docs/transformers/) and
  [PyTorch](https://pytorch.org/) run the local `gpt2` model behind the
  perplexity signal in `detector.py`.
- [Gunicorn](https://gunicorn.org/) is the production WSGI server. The
  Flask development server only listens on loopback in this project.
