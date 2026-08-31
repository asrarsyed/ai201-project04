#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      ← YOU BUILD THIS (Milestone 3, 4, 5)
    POST /appeal      ← YOU BUILD THIS (Milestone 5)
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

import uuid

from flask import Flask, jsonify, request

import audit
import config
import creators
import detector
import phrasing
import scoring
import stylometry

app = Flask(__name__)


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# Off until you turn it on. In unit 8, Milestone 1:
#
#   1. Set RATE_LIMITING_ENABLED = True in config.py (or AI201_RATE_LIMITS=1)
#   2. Choose your numbers there
#   3. Uncomment the @limiter.limit(...) line on /submit below, AND the
#      matching line on /submit/batch (Stretch feature) — batch does up to
#      BATCH_MAX_ITEMS scoring passes per request, so leaving its limiter
#      commented out while /submit's is on defeats the limit entirely.
#
# The order doesn't matter. While limiting is off, that decorator is a no-op
# that quietly does nothing, so uncommenting it early costs you nothing — but
# it also means no 429 until you've done step 1.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.


class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route
    untouched, so uncommenting the line before you flip the setting is
    harmless instead of a crash on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against.

        Falling back to the caller's address is the easy version. Unit 8's
        stretch asks about per-creator limits instead — and the difference
        matters: one script can look like a thousand callers, and one household
        can look like one.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
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
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
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


# ── The worked example. Already works. Don't edit. ────────────────────────────


@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify(
        {
            "ok": True,
            "you_sent": payload.get("message"),
            "service": "provenance-guard",
        }
    )


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

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


# ── YOU BUILD THIS ────────────────────────────────────────────────────────────


@app.post("/submit")
# @limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """
    Take a piece of text, decide about it, log the decision, answer.
    ← TODO — Milestones 3, 4 and 5

    Expects JSON:
        {"text": "...", "creator_id": "..."}

    Should return JSON with, at minimum:
        {"content_id": "...", "guess": "...", "confidence": 0.0, "label": "...",
         "model_score": 0.0, "style_score": 0.0}

    ⚠️ **Both signal scores go in the response, not just the log.** Unit 8's
    `run_attacks.py` and `run_eval.py` read `model_score` and `style_score`
    straight off this response and put them in your reports. Leave them out and
    every row of next week's evidence says `null` — which is exactly the
    diagnostic you need to name a stage and a mechanism. You do not want to
    find that out after running the attack set.

    ─────────────────────────────────────────────────────────────────────────
    Build it in three passes. Do not skip ahead — the ordering is how you tell
    a broken route from a broken signal.

    **Milestone 3 — the route answers.**
      1. Return a hardcoded response. Confirm `curl` gets it back before you
         add any logic at all.
      2. Then pull `text` and `creator_id` out of the payload.
      3. Then call ONE signal — `detector.model_signal(text)` — and put the
         real number in. Leave confidence and label as placeholders.
      4. Log every submission with `audit.log_decision(...)`. The content_id
         matters: `/appeal` needs it, and a student who skips it rebuilds this
         whole flow later.

    **Milestone 4 — the second signal and the score.**
      5. Add `stylometry.style_signal(text)`.
      6. Combine them with `scoring.combine_signals(...)`.
      7. Log BOTH signal scores alongside the combined one, and put them in the
         response too. Next week you can't diagnose anything without them.

    **Milestone 5 — the label.**
      8. `scoring.score_to_label(...)` and put the real label in the response.

    ─────────────────────────────────────────────────────────────────────────
    Worth deciding early, because unit 8's attack set will decide it for you:
    what should this do when `text` is missing, empty, or enormous? A crash on
    a malformed input is one of the most common real failures there is.
    """
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    creator_id = payload.get("creator_id")

    error = _validate_text(text)
    if error:
        audit.log_rejection(creator_id=creator_id or "unknown", reason="invalid_text")
        return jsonify({"error": "invalid_input", "message": error}), 400

    return jsonify(_score_and_log(text, creator_id))


def _validate_text(text) -> str | None:
    """Returns an error message if `text` is unusable, else None."""
    if not isinstance(text, str) or len(text.split()) < 3:
        return "text is required and must be at least a few words long."
    return None


def _score_and_log(text: str, creator_id: str) -> dict:
    """
    The scoring core of /submit: run all signals, combine, label, log, and
    build the response body. Shared with /submit/batch so both routes decide
    the same way.
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
# Same limiter as /submit, and deliberately so: batch does up to
# BATCH_MAX_ITEMS scoring passes per request, so without its own limit line
# it would be a free way around the per-minute cap on /submit — one request,
# unlimited scoring work inside it. Uncomment together with /submit's line.
# @limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit_batch():
    """
    Score multiple texts in one call. ← Stretch feature

    Expects JSON:
        {"items": [{"text": "...", "creator_id": "..."}, ...]}

    Each item is validated and scored exactly like /submit, independently —
    one bad item in the batch gets its own rejection entry and doesn't stop
    the rest. Capped at BATCH_MAX_ITEMS so a single request can't be used to
    dodge per-request rate limiting by smuggling in an unbounded amount of
    work.
    """
    payload = request.get_json(silent=True) or {}
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
        error = _validate_text(text)
        if error:
            audit.log_rejection(creator_id=creator_id or "unknown", reason="invalid_text")
            results.append({"error": "invalid_input", "message": error})
            continue

        results.append(_score_and_log(text, creator_id))

    return jsonify({"count": len(results), "results": results})


@app.post("/appeal")
def appeal():
    """
    A writer says you got it wrong. ← TODO — Milestone 5

    Expects JSON:
        {"content_id": "...", "reasoning": "..."}

    Should:
      1. Check the content_id actually exists — `audit.entries_for(id)` tells
         you. A typo here fails silently and looks like a broken endpoint,
         which is the single most common way this milestone eats an hour.
      2. Record the appeal with `audit.log_appeal(...)`, which moves the item
         to `under_review`.
      3. Confirm to the writer. No automatic re-checking needed.

    This is the smallest endpoint in the project and the one that matters most
    to the person on the other end. It's the only thing standing between a
    wrong accusation and nothing at all.
    """
    payload = request.get_json(silent=True) or {}
    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")

    entries = audit.entries_for(content_id) if content_id else []
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


# ── Stretch features ──────────────────────────────────────────────────────────


@app.get("/content/<content_id>")
def get_content(content_id):
    """
    One item's current status. ← Stretch feature

        curl http://127.0.0.1:5000/content/<content_id>

    "Current" means the most recent entry for this id, not the first — a
    submission that was later appealed shows status "under_review", not the
    original "decided". The original decision is still in /log; this just
    answers "where does this stand right now."
    """
    entries = audit.entries_for(content_id)
    if not entries:
        return jsonify({"error": "not_found", "message": "No submission found with that content_id."}), 404

    latest = dict(entries[-1])
    latest["creator_note"] = creators.verification_note(latest.get("creator_id"))
    return jsonify(latest)


@app.get("/creator/<creator_id>")
def get_creator(creator_id):
    """
    One writer's history and current standing. ← Stretch feature

        curl http://127.0.0.1:5000/creator/<creator_id>

    Groups every log entry touching this creator_id by content_id, so a
    submission and any appeal against it are reported together with the
    item's current status, rather than as one flat list a caller has to
    reassemble by hand.
    """
    entries = [e for e in audit.read_entries() if e.get("creator_id") == creator_id]
    if not entries:
        return jsonify({"error": "not_found", "message": "No entries found for that creator_id."}), 404

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
    Aggregate numbers across the whole audit log. ← Stretch feature

        curl http://127.0.0.1:5000/stats

    Everything here is derived from /log, not a separate store — this is a
    read of what's already recorded, not a new source of truth. Rejections
    are counted separately from decisions since they never got a score.
    """
    entries = audit.read_entries()

    decisions = [e for e in entries if e.get("status") in ("decided", "under_review") and e.get("guess")]
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


# ── Already works ─────────────────────────────────────────────────────────────


@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off (unit 8)'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f"  curl -X POST http://{config.HOST}:{config.PORT}/ping \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"message": "hello"}\'')
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
