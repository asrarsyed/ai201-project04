"""
Per-creator reputation: a running tally of what this service's own three
signals have said about one creator_id over time. It gets shown back to the
reader rather than folded into the score.

This is not a credential system and there's no identity check anywhere in it.
"Verified" here only means this service's own past guesses lean human
(human_count > ai_count), worked out fresh from the counts on every read
rather than stored as a flag of its own.

    from authentiwrite import creators

    creators.record_guess("asrar", "human")
    note = creators.verification_note("asrar")

This lives in one JSON file (logs/creators.json) instead of the audit log,
because it holds current state, what's true about a creator right now, rather
than a history of events. A small dict keyed by creator_id answers a lookup
straight away instead of scanning the whole log. The trade-off is that it's a
second store, and keeping it in step with the log is manual: every /submit
call has to remember to call record_guess.
"""

import json
import threading

from . import config

_lock = threading.Lock()


def _empty_record() -> dict:
    return {"ai_count": 0, "human_count": 0, "unsure_count": 0}


def _normalize_record(value) -> dict:
    """
    Force whatever was stored for one creator back into a valid record rather
    than trusting it. Someone editing the file by hand, a later change to the
    format, or a write interrupted partway through could all leave a record
    with the wrong shape or with counts that aren't numbers. This is the one
    place that gets checked, so everything below can assume a clean dict
    without checking again.
    """
    if not isinstance(value, dict):
        return _empty_record()

    record = _empty_record()
    for key in record:
        count = value.get(key, 0)
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            continue  # leave that field at 0 rather than trust a bad value
        record[key] = count
    return record


def _load() -> dict:
    """
    The whole store, guaranteed to be a dict of str to dict with valid
    records. Never a bare list, never a record missing a key or holding a
    count that isn't a number. Bad input turns into empty or zeroed values
    instead of raising, because a corrupted store shouldn't take down every
    route that reads reputation.
    """
    if not config.CREATORS_STORE.exists():
        return {}
    try:
        raw = json.loads(config.CREATORS_STORE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if not isinstance(raw, dict):
        return {}

    return {
        creator_id: _normalize_record(value)
        for creator_id, value in raw.items()
        if isinstance(creator_id, str)
    }


def _save(data: dict) -> None:
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    config.CREATORS_STORE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def record_guess(creator_id: str, guess: str) -> dict:
    """
    Bump one creator's counters after a decision. `guess` is "ai", "human", or
    "unsure". Anything else does nothing, since those are the only three
    labels scoring.score_to_label produces.

    This also does nothing if creator_id is missing or blank. A submission
    with no creator_id can't be attributed to anyone, so there's nothing to
    update.
    """
    if not isinstance(creator_id, str) or not creator_id.strip():
        return {}

    if guess not in ("ai", "human", "unsure"):
        return {}

    with _lock:
        data = _load()
        record = data.setdefault(creator_id, _empty_record())
        record[f"{guess}_count"] += 1
        _save(data)
        return dict(record)


def get_record(creator_id: str) -> dict:
    """A creator's raw counts, zeroed if they have no history yet."""
    data = _load()
    return data.get(creator_id, _empty_record())


def is_verified(creator_id: str) -> bool:
    """
    Verified means this service's own guesses have called this creator human
    more often than AI. It's a strict majority, worked out from the current
    counts rather than stored as a flag. A brand-new creator with no history
    at all (0 human, 0 AI) is not verified, because 0 is not greater than 0.
    """
    record = get_record(creator_id)
    return record["human_count"] > record["ai_count"]


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def verification_note(creator_id: str) -> str | None:
    """
    The sentence a reader sees next to a decision. Returns None when there's
    no creator_id to attribute it to. No identity means no note, rather than a
    guess.
    """
    if not isinstance(creator_id, str) or not creator_id.strip():
        return None

    record = get_record(creator_id)
    verified = record["human_count"] > record["ai_count"]
    status = "verified human" if verified else "unverified human"

    return (
        f"This writer is {status}. "
        f"Deemed AI {_plural(record['ai_count'], 'time')}, "
        f"deemed human {_plural(record['human_count'], 'time')}, "
        f"and unsure {_plural(record['unsure_count'], 'time')}."
    )
