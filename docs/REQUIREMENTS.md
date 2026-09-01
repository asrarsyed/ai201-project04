# Requirements

## Functional requirements

- `POST /submit` scores one `{text, creator_id}` and returns a
  `content_id`, `guess`, `confidence`, `label`, and every per-signal score
  (`model_score`, `style_score`, `pattern_score`).
- `POST /appeal` moves a submission's status to `under_review` and adds a
  new log entry without changing the original decision.
- `GET /log` returns the audit log as JSON.
- Every decision and every rejection goes into an append-only audit log
  with a consistent set of fields. See [ARCHITECTURE.md](ARCHITECTURE.md).
- `GET /content/<id>`, `GET /creator/<id>`, `GET /stats`, and
  `POST /submit/batch` provide read and bulk access on top of the same
  scoring and logging core.

## Non-functional requirements

- **Rate limiting.** 6 requests a minute and 120 a day per `creator_id`
  rather than per IP address. See [DECISIONS.md](DECISIONS.md) for the
  reasoning.
- **Nothing hosted.** The detector model runs locally. The service needs no
  API key and makes no network call to score text.
- **Malformed input never reaches the model.** Invalid payloads get
  rejected before any signal runs. That means the body has to be a JSON
  object rather than a bare array or string, `text` has to be a string of
  at least 3 words and at most `config.MAX_TEXT_CHARS`, and `creator_id`,
  when it's there at all, has to be a non-empty string.
- **Debug mode only on loopback.** Flask's debug mode switches itself off
  the moment the service binds to anything other than `127.0.0.1` or
  `localhost`.

## Acceptance criteria

These are the five measurable targets the service gets judged against.
Results and diagnoses are in [RESEARCH.md](RESEARCH.md).

| # | Criterion | Target | Current |
|---|---|---|---|
| 1 | False positives | Across three trials, no more than 1 of 10 human-written samples is labelled high-confidence AI. | MET, 0 of 10 |
| 2 | Score spread | The average combined score of an AI sample set beats the average of a human sample set by at least 30 points, in every trial. | **MISSED, 16.6 points** |
| 3 | Label coverage | All three labels each show up at least once across the samples in Criterion 2. | MET, 3 of 3 |
| 4 | Appeal path | 100% of valid appeals change status and create a logged entry. | MET, 5 of 5 |
| 5 | Bad input | 100% of requests with missing, empty, malformed, or oversized text return a 4xx and never reach any signal. | MET, 4 of 4 |

**Why these targets:**

- **Criterion 1 is the strictest** because wrongly accusing a real writer
  costs more than missing AI-generated text. That imbalance is the centre
  of the whole project. See [DECISIONS.md](DECISIONS.md).
- **Criteria 2 and 3** reuse the same 15-sample set of 10 human and 5 AI
  texts, so one calibration pass answers both "is there real separation
  here" and "can every label actually be reached".
- **Criterion 4** treats an appeal that visibly changes nothing as the same
  thing as having no appeal process at all.
- **Criterion 5** exists because running the model on input of any size is
  both a correctness risk and a way to exhaust resources.

## Constraints

- The detector model runs on CPU, inside the process. No GPU assumed.
- Rate-limit counters live in memory (`memory://`), so limits reset on
  restart and aren't shared between instances. That's a documented
  limitation rather than a bug. See [ARCHITECTURE.md](ARCHITECTURE.md).
- Python 3.11 to 3.13. Version 3.14 isn't supported by the pinned
  dependencies.
