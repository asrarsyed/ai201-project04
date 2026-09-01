#!/usr/bin/env python3
"""
The Flask web service. Wires the three signals (detector, stylometry,
phrasing), the rule that combines and labels them (scoring), and the audit
log (audit) together behind a small set of HTTP routes.

    python -m authentiwrite.app

Routes:

    POST /ping             liveness check, no scoring
    POST /submit           score one piece of text
    POST /submit/batch     score a list of {text, creator_id} items
    POST /appeal           flag a decision for review
    GET  /log              the audit log
    GET  /health           service and model status
    GET  /content/<id>     latest status for one content_id
    GET  /creator/<id>     one writer's history
    GET  /stats            totals across the whole log
"""

import uuid

from flask import Flask, jsonify, request

from . import audit, config, creators, detector, phrasing, scoring, stylometry

app = Flask(__name__)


# ── Rate limiting ─────────────────────────────────────────────────────────────
# Switched on and off by config.RATE_LIMITING_ENABLED. When it's off,
# _LimiterOff turns @limiter.limit(...) into a decorator that does nothing, so
# the route code doesn't need an if/else wrapped around it. The storage backend
# is set explicitly to keep Flask-Limiter quiet on startup. In-memory storage
# is fine for one process and wrong for anything running as more than one.


class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It turns @limiter.limit(...) into a decorator that hands the route back
    untouched, so adding that line before you flip the setting does nothing
    instead of crashing on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against. It uses creator_id, and falls back to
        the caller's address only when the payload isn't a dict or has no
        usable creator_id. Counting against creator_id rather than IP is what
        stops a script from dodging the limit by changing source addresses.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object, such as a bare list
        # or a string, has no .get method. Without this check the key function
        # raises BEFORE the route runs, and a malformed request turns into a
        # 500 that looks like the handler crashed when it never ran at all.
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """A refused request still gets logged, so a flood of 429s leaves a trace instead of silence."""
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        audit.log_rejection(
            creator_id=payload.get("creator_id", "unknown"),
            reason="rate_limited",
            limit=str(exc.description),
        )
        return jsonify(
            {
                "error": "rate_limited",
                "message": "Too many submissions. Try again shortly.",
                "limit": str(exc.description),
            }
        ), 429


# ── Liveness ──────────────────────────────────────────────────────────────────


@app.post("/ping")
def ping():
    """A small echo route for checking the service is up, separate from scoring."""
    payload = _json_object() or {}
    return jsonify(
        {
            "ok": True,
            "you_sent": payload.get("message"),
            "service": "authentiwrite",
        }
    )


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    loaded = detector._model is not None
    return jsonify(
        {
            "ok": True,
            "detector_model": config.DETECTOR_MODEL,
            "detector_loaded": loaded,
            "rate_limiting": config.RATE_LIMITING_ENABLED,
            "log_entries": len(audit.read_entries()),
        }
    )


# ── Scoring ───────────────────────────────────────────────────────────────────


@app.post("/submit")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """
    Score one piece of text and log the decision.

    Expects JSON: {"text": "...", "creator_id": "..."}

    Returns: {"content_id", "guess", "confidence", "label",
              "model_score", "style_score", "pattern_score", "creator_note"}

    All three signal scores come back in the response rather than only going
    to the log, because scripts/run_attacks.py and scripts/run_eval.py read
    them from here.
    """
    payload = _json_object()
    if payload is None:
        return jsonify(
            {
                "error": "invalid_input",
                "message": "Request body must be a JSON object.",
            }
        ), 400

    text = payload.get("text", "")
    creator_id = payload.get("creator_id")

    error = _validate_text(text) or _validate_creator_id(creator_id)
    if error:
        audit.log_rejection(
            creator_id=creator_id if isinstance(creator_id, str) else "unknown",
            reason="invalid_text",
        )
        return jsonify({"error": "invalid_input", "message": error}), 400

    return jsonify(_score_and_log(text, creator_id))


def _json_object() -> dict | None:
    """
    The request body, but only if it's a JSON *object*.

    `request.get_json(silent=True)` hands back whatever parsed, and for a body
    that's a JSON array that means a list. A non-empty list is truthy, so the
    usual `or {}` trick passes it straight through to code that then calls
    `.get()` on it. Returning None here lets the route answer with a 400
    instead of raising an AttributeError the caller sees as a 500.
    """
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else None


def _validate_text(text) -> str | None:
    """Returns an error message if `text` is unusable, else None."""
    if not isinstance(text, str) or len(text.split()) < 3:
        return "text is required and must be at least a few words long."
    # Every submission costs a scoring pass, and the model signal cuts the
    # text off at config.DETECTOR_MAX_TOKENS anyway. Text past this limit buys
    # no extra signal and is only a way to make the service do unlimited work.
    if len(text) > config.MAX_TEXT_CHARS:
        return f"text may not exceed {config.MAX_TEXT_CHARS:,} characters."
    return None


def _validate_creator_id(creator_id) -> str | None:
    """
    Returns an error message if `creator_id` is unusable, else None.

    A creator_id that isn't a string, such as an object or a number, used to
    score normally and get written straight into the log, where no ordinary
    lookup could ever find it again. Both `GET /creator/<id>` and
    creators.record_guess() key on a string. A record that goes quietly
    missing is worse than a 400, so this gets checked as carefully as `text`
    does. Leaving it out is still fine: an anonymous submission is a real
    case, but one nobody can look up isn't.
    """
    if creator_id is None:
        return None
    if not isinstance(creator_id, str) or not creator_id.strip():
        return "creator_id must be a non-empty string when provided."
    return None


def _score_and_log(text: str, creator_id: str) -> dict:
    """
    The scoring core of /submit. Runs all three signals, combines them,
    labels the result, logs it, and builds the response body. /submit/batch
    calls this too, so both routes decide the same way.
    """
    content_id = str(uuid.uuid4())
    model_score = detector.model_signal(text)
    style_score = stylometry.style_signal(text)
    pattern_score = phrasing.pattern_signal(text)
    combined_score = scoring.combine_signals(model_score, style_score, pattern_score)
    guess, label = scoring.score_to_label(combined_score)
    confidence = round(abs(combined_score - 0.5) * 2, 4)

    audit.log_decision(
        content_id=content_id,
        creator_id=creator_id,
        guess=guess,
        model_score=model_score,
        style_score=style_score,
        combined_score=combined_score,
        label=label,
        status="decided",
        pattern_score=pattern_score,
    )
    creators.record_guess(creator_id, guess)

    return {
        "content_id": content_id,
        "guess": guess,
        "confidence": confidence,
        "label": label,
        "model_score": model_score,
        "style_score": style_score,
        "pattern_score": pattern_score,
        "creator_note": creators.verification_note(creator_id),
    }


@app.post("/submit/batch")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit_batch():
    """
    Score a list of {text, creator_id} items in one request.

    Each item is checked and scored on its own, exactly the way /submit does
    it. One bad item gets its own rejection entry and doesn't stop the rest.
    The list is capped at config.BATCH_MAX_ITEMS, and this route carries the
    same rate limit as /submit. Without its own limiter line, one batch
    request could run BATCH_MAX_ITEMS scoring passes while counting as a
    single call against /submit's limit.
    """
    payload = _json_object()
    if payload is None:
        return jsonify(
            {
                "error": "invalid_input",
                "message": "Request body must be a JSON object.",
            }
        ), 400

    items = payload.get("items")

    if not isinstance(items, list) or not items:
        return jsonify(
            {
                "error": "invalid_input",
                "message": "items must be a non-empty list of {text, creator_id}.",
            }
        ), 400

    if len(items) > config.BATCH_MAX_ITEMS:
        return jsonify(
            {
                "error": "invalid_input",
                "message": f"items may not exceed {config.BATCH_MAX_ITEMS} per batch.",
            }
        ), 400

    results = []
    for item in items:
        if not isinstance(item, dict):
            results.append({"error": "invalid_input", "message": "each item must be an object."})
            continue

        text = item.get("text", "")
        creator_id = item.get("creator_id")
        error = _validate_text(text) or _validate_creator_id(creator_id)
        if error:
            audit.log_rejection(
                creator_id=creator_id if isinstance(creator_id, str) else "unknown",
                reason="invalid_text",
            )
            results.append({"error": "invalid_input", "message": error})
            continue

        results.append(_score_and_log(text, creator_id))

    return jsonify({"count": len(results), "results": results})


@app.post("/appeal")
def appeal():
    """
    A writer disputes a decision. This moves the item to under_review and
    adds a new entry to the log. The original "decided" entry is left alone.

    Expects JSON: {"content_id": "...", "reasoning": "..."}
    """
    payload = _json_object()
    if payload is None:
        return jsonify(
            {
                "error": "invalid_input",
                "message": "Request body must be a JSON object.",
            }
        ), 400

    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")

    entries = audit.entries_for(content_id) if isinstance(content_id, str) else []
    if not entries:
        return jsonify(
            {
                "error": "not_found",
                "message": "No submission found with that content_id.",
            }
        ), 404

    creator_id = entries[0].get("creator_id")
    audit.log_appeal(content_id=content_id, creator_id=creator_id, reasoning=reasoning)

    return jsonify(
        {
            "content_id": content_id,
            "status": "under_review",
            "message": "Your appeal has been recorded and the decision is under review.",
        }
    )


@app.get("/content/<content_id>")
def get_content(content_id):
    """
    One item's current status, taken from the most recent log entry for this
    id rather than the first. A submission that was appealed later shows
    "under_review". The original "decided" entry is still in /log, untouched.
    """
    entries = audit.entries_for(content_id)
    if not entries:
        return jsonify(
            {"error": "not_found", "message": "No submission found with that content_id."}
        ), 404

    latest = dict(entries[-1])
    latest["creator_note"] = creators.verification_note(latest.get("creator_id"))
    return jsonify(latest)


@app.get("/creator/<creator_id>")
def get_creator(creator_id):
    """
    One writer's history, grouped by content_id. A submission and any appeal
    against it come back together, along with the item's current status,
    rather than as one flat list.
    """
    entries = [e for e in audit.read_entries() if e.get("creator_id") == creator_id]
    if not entries:
        return jsonify(
            {"error": "not_found", "message": "No entries found for that creator_id."}
        ), 404

    by_content = {}
    for e in entries:
        cid = e.get("content_id")
        by_content.setdefault(cid, []).append(e)

    items = [
        {"content_id": cid, "current_status": history[-1].get("status"), "history": history}
        for cid, history in by_content.items()
    ]

    return jsonify(
        {
            "creator_id": creator_id,
            "submission_count": len(items),
            "creator_note": creators.verification_note(creator_id),
            "items": items,
        }
    )


@app.get("/stats")
def get_stats():
    """
    Totals worked out from the audit log when you ask for them. There's no
    separate store behind this, so these numbers can't drift away from /log.
    Rejections are counted apart from decisions because they never got a
    score.
    """
    entries = audit.read_entries()

    decisions = [
        e for e in entries if e.get("status") in ("decided", "under_review") and e.get("guess")
    ]
    appeals = [e for e in entries if e.get("event") == "appeal"]
    rejections = [e for e in entries if e.get("event") == "rejected"]

    guess_counts = {}
    for e in decisions:
        guess_counts[e["guess"]] = guess_counts.get(e["guess"], 0) + 1

    def _avg(key):
        values = [e[key] for e in decisions if isinstance(e.get(key), (int, float))]
        return round(sum(values) / len(values), 4) if values else None

    return jsonify(
        {
            "total_entries": len(entries),
            "decisions": len(decisions),
            "appeals": len(appeals),
            "rejections": len(rejections),
            "appeal_rate": round(len(appeals) / len(decisions), 4) if decisions else None,
            "guess_distribution": guess_counts,
            "average_scores": {
                "model_score": _avg("model_score"),
                "style_score": _avg("style_score"),
                "pattern_score": _avg("pattern_score"),
                "combined_score": _avg("combined_score"),
            },
        }
    )


# ── The audit log ─────────────────────────────────────────────────────────────


@app.get("/log")
def get_log():
    """The audit log, most recent last."""
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"AuthentiWrite on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f"  curl -X POST http://{config.HOST}:{config.PORT}/ping \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"message": "hello"}\'')
    print()
    # debug=True hands out an interactive debugger, so it stays local only.
    # See config.py.
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
