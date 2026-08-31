"""
Per-creator reputation. ← Stretch feature

Not a credential system — no identity check, no "extra step" a writer takes
to prove they're human. This is simpler and more honest about what it is: a
running tally of what this service's own three signals have said about one
creator_id over time, surfaced back to the reader so they can weigh it
themselves rather than have the service make the call silently.

    from creators import record_guess, verification_note

    record_guess("asrar", "human")
    note = verification_note("asrar")
    # "This writer is verified human. Deemed AI 0 times and deemed human 1 time."

Stored as one JSON file, not the audit log — this is current-state
("what's true about this creator right now"), not an append-only event
history. The audit log already has that shape and answering "how many times
has this creator been called AI" from it would mean scanning every entry on
every request. A small dict keyed by creator_id answers it in one lookup,
at the cost of being a second source of truth that has to be kept in sync
with the log by hand (every /submit call has to remember to call
record_guess too).

⚠️ "Verified" here means "this service's own past guesses lean human,"
recomputed live from the counts — not "this person's identity was checked."
A creator flips to verified the moment human_count > ai_count and flips
back the moment that stops being true. It's a reputation signal built from
the same imperfect detector as everything else in this project, not a
trust anchor.
"""

import json
import threading

import config

_lock = threading.Lock()


def _empty_record() -> dict:
    return {"ai_count": 0, "human_count": 0, "unsure_count": 0}


def _normalize_record(value) -> dict:
    """
    Coerce whatever was stored for one creator back into a valid record,
    rather than trust it. A hand-edited file, a future schema change, or a
    write that landed mid-corruption could leave a record with the wrong
    shape or non-numeric counts — this is the one place that gets checked,
    so every reader below can assume a clean dict without checking again.
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
    The whole store, guaranteed to be `dict[str, dict]` with valid records —
    never a bare list, never a record missing a key or holding a non-numeric
    count. Bad input degrades to empty/zeroed rather than raising, since a
    corrupted store shouldn't take down every route that reads reputation.
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
    Bump one creator's counters after a decision. `guess` is "ai", "human",
    or "unsure" — anything else is a no-op, since those are the only three
    labels `scoring.score_to_label` produces.

    No-op if `creator_id` is missing or blank — a submission with no
    creator_id can't be attributed to anyone, so there's nothing to update.
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
    Verified means this service's own guesses have called this creator
    human more often than AI — a strict majority, recomputed from the
    current counts rather than stored as its own flag. A brand-new creator
    with zero history (0 human, 0 AI) is not verified: 0 is not greater
    than 0.
    """
    record = get_record(creator_id)
    return record["human_count"] > record["ai_count"]


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def verification_note(creator_id: str) -> str | None:
    """
    The sentence a reader sees alongside a decision. Returns None if there's
    no creator_id to attribute it to — no identity, no note, rather than
    guessing.
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
