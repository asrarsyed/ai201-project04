<div align="center">

# AuthentiWrite

**A backend service that gives a writing platform an honest second opinion on whether text was written by a person or by AI. It returns a guess and a confidence score, never a verdict, and anyone it gets wrong has a real way to appeal.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11%20to%203.13-blue.svg)
![Tests](https://img.shields.io/badge/tests-133%20passing-brightgreen.svg)
![Attack set](https://img.shields.io/badge/attack%20set-53%20held%20%2F%203%20broke-orange.svg)

[Docs](docs/PROJECT.md) · [Architecture](docs/ARCHITECTURE.md) · [Decisions](docs/DECISIONS.md)

</div>

---

## About the Project

Most AI-detection tools show you a probability score as though it settled
something. This one is built the other way round. Every signal it uses has
a blind spot that is named and tested, the rule that combines them was
worked out against real data instead of guessed, and every decision comes
with an appeal path that actually works.

Three separate signals score each submission. One is a language model
measuring how predictable the text is. One measures the shape of the
writing, its sentence lengths and vocabulary, with no idea what the words
mean. One looks for sentence patterns that show up more often in AI copy.
Their weighted combination turns into one of three labels written in plain
English. Every decision goes into an append-only log, and an appeal adds to
that record rather than overwriting it.

**Why I built this:** to get practice building a probabilistic system
honestly from end to end. Not just calling a model, but calibrating it
against real data, attacking it with a structured test set, and being
straight in the write-up about which real people pay for which trade-off.

### Built With

- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/) and [Flask-Limiter](https://flask-limiter.readthedocs.io/)
- [Transformers](https://huggingface.co/docs/transformers/) and [PyTorch](https://pytorch.org/), running `gpt2` locally with no API key
- [Gunicorn](https://gunicorn.org/)

## Features

- Three separate signals you can explain, instead of one model you can't
- A combining rule with calibration data behind every number in it
- Three plain-English labels, all reachable, all mentioning the appeal path
- An append-only audit log and an appeal path that works
- Rate limiting per `creator_id` (6 a minute, 120 a day) that can't be dodged by changing IP
- A 56-attack test set covering evasion, false positives, prompt injection, malformed input, and flooding. 53 held, 3 broke, all of them diagnosed
- `/submit/batch`, `/creator/<id>`, `/content/<id>`, `/stats`, and per-creator reputation notes
- 133 unit tests that stub the model and finish in under a second, run on CI against Python 3.11 to 3.13

## Getting Started

### Prerequisites

```bash
python >= 3.11, < 3.14
```

No API key and no account. The detector model runs on your machine and
downloads itself the first time you use it, about 550MB.

### Installation

```bash
git clone https://github.com/<your-username>/authentiwrite.git
cd authentiwrite
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python tests/test_environment.py   # confirms the environment is ready
```

### Running it

```bash
python -m authentiwrite.app
```

That's the Flask development server, which only listens on loopback. To run
it as a service:

```bash
gunicorn --workers 1 --timeout 120 "authentiwrite.app:app"
```

One worker on purpose. Each worker loads its own copy of the model, about
550MB, and the rate limiter's counters live in memory and aren't shared
between workers.

In another terminal:

```bash
curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Some writing to check.", "creator_id": "me"}'
```

## Usage

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "MerchantE is a financial technology company that provides payment-processing and payment-infrastructure services to businesses.", "creator_id": "asrar"}'
```

```json
{
  "confidence": 0.1046,
  "content_id": "e9361d27-cfb1-451c-aa92-de74b32d7977",
  "creator_note": "This writer is unverified human. Deemed AI 0 times, deemed human 0 times, and unsure 1 time.",
  "guess": "unsure",
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation. It just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
  "model_score": 0.5319,
  "pattern_score": 0.0,
  "style_score": 0.5208
}
```

A writer who disagrees can appeal:

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "e9361d27-cfb1-451c-aa92-de74b32d7977", "reasoning": "I wrote this myself."}'
```

```json
{
  "content_id": "e9361d27-cfb1-451c-aa92-de74b32d7977",
  "status": "under_review",
  "message": "Your appeal has been recorded and the decision is under review."
}
```

## Tests

```bash
pytest                             # 133 tests, no model download needed
```

The unit suite stubs out the local model, so it finishes in under a second.
To exercise the real thing, start the service and run the attack set and the
acceptance criteria against it:

```bash
python -m authentiwrite.app                            # one terminal
python scripts/run_attacks.py --set attack_set --label mine   # another
python scripts/run_eval.py --label mine
```

Both write a timestamped Markdown report into `results/`.

## What I Learned

- **Calibration data changed my mind about things intuition had settled.**
  The two original signals never actually pointed in opposite directions on
  my calibration set. The real finding was that one of them swung around far
  more than the other, which turns out to be a more useful thing to weight
  against than disagreement would have been.
- **Fixing one failure mode reliably opens another.** Giving the model
  signal more weight fixed label coverage and closed several evasion
  attacks, and it also brought back a false positive on dense technical
  writing. That trade is written down in
  [docs/DECISIONS.md](docs/DECISIONS.md) as a cost, not buried.
- **A criterion that passes can still be lying to you.** My 0-out-of-10
  false positive rate looked clean until I noticed most of those samples
  were landing on "unsure" rather than "human". The pass was partly a
  symptom of the same imbalance that was failing a different criterion.
- **All three signals share one blind spot, and I didn't plan that.** Each
  one fails hardest on plain, ordinary writing. That isn't a coincidence.
  It's what happens when every measure is built around how unusual
  something looks, because plain writing is the thing with nothing unusual
  in it to measure.
- **A results table can mislead without containing a single wrong number.**
  My attack report printed confidence under a column headed "Score", so a
  correct `ai` call showed up as 0.331, which is below the AI threshold and
  looks wrong in exactly the way that invites a bad conclusion. Every value
  in the table was right. The heading wasn't.
- **Next time** I'd write the false positive check so it also requires
  reaching the correct label some minimum share of the time, instead of only
  requiring that it avoid the wrong one.

## Roadmap

- [x] Three calibrated signals, combined and labelled
- [x] Audit log and appeal path
- [x] Rate limiting, attack testing, acceptance criteria
- [x] Per-creator reputation, batch submission, stats endpoint
- [x] Input limits and payload validation hardened against the attack set
- [ ] A fourth signal aimed at plain, information-dense prose, which is the
      one acceptance criterion still missed (see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md))
- [ ] Rate-limit storage that survives a restart, needed to run more than one process
- [ ] Real identity verification, deferred on purpose (see [docs/DECISIONS.md](docs/DECISIONS.md))

Full documentation starts at [docs/PROJECT.md](docs/PROJECT.md), or see the
[docs index](docs/README.md).

## Acknowledgments

- [Codepath](https://github.com/codepath/ai201-project4-provenance-guard-starter-v2026), the original starter template