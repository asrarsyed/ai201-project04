"""
The append-only audit log: one JSON object per line in logs/audit.jsonl.

A decision always carries the same nine core fields (timestamp, content_id,
creator_id, guess, model_score, style_score, combined_score, label, status),
so decisions written from different code paths can be compared directly.
Appeals and rejections carry the identifying fields and mark themselves with
their own `event`.

    from authentiwrite import audit

    audit.log_decision(content_id=..., creator_id=..., guess="ai", ...)
    entries = audit.read_entries(limit=50)
"""

import json
import threading
from datetime import datetime, timezone

from . import config

_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_decision(
    content_id: str,
    creator_id: str,
    guess: str | None = None,
    model_score: float | None = None,
    style_score: float | None = None,
    combined_score: float | None = None,
    label: str | None = None,
    status: str = "decided",
    **extra,
) -> dict:
    """
    Write one decision to the audit log with the nine standard fields:
    timestamp, content_id, creator_id, guess, model_score, style_score,
    combined_score, label, status.

    `status` changes over an item's life. It starts as `decided` when the item
    is first judged, and becomes `under_review` once the writer appeals. Any
    extra keyword arguments get written too, which is how pattern_score gets
    in there.
    """
    entry = {
        "timestamp": _now(),
        "content_id": content_id,
        "creator_id": creator_id,
        "guess": guess,
        "model_score": model_score,
        "style_score": style_score,
        "combined_score": combined_score,
        "label": label,
        "status": status,
    }
    entry.update(extra)
    return _append(entry)


def log_appeal(content_id: str, creator_id: str, reasoning: str) -> dict:
    """
    Record an appeal as a new entry after the original decision instead of
    editing that decision. Keeping the log append-only preserves what was
    first decided, the fact that someone challenged it, and the order the two
    happened in.
    """
    return _append(
        {
            "timestamp": _now(),
            "content_id": content_id,
            "creator_id": creator_id,
            "event": "appeal",
            "status": "under_review",
            "reasoning": reasoning,
        }
    )


def log_rejection(creator_id: str, reason: str, **extra) -> dict:
    """
    Record a request that never became a decision, either because it was rate
    limited or because the input was rejected. Rejections get logged because a
    request that fails quietly and leaves no trace looks exactly like a
    request that was never sent.
    """
    return _append(
        {
            "timestamp": _now(),
            "creator_id": creator_id,
            "event": "rejected",
            "status": "rejected",
            "reason": reason,
            **extra,
        }
    )


def _append(entry: dict) -> dict:
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False)
    with _lock, config.AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return entry


def read_entries(limit: int | None = None) -> list[dict]:
    """
    Read the log back, oldest first. `limit` keeps the most recent N.

    A line that won't parse gets skipped instead of raising, because a log you
    can't read at all because of one bad row is worse than a log with a gap in
    it.
    """
    if not config.AUDIT_LOG.exists():
        return []

    entries = []
    for line in config.AUDIT_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return entries[-limit:] if limit else entries


def clear() -> int:
    """Wipe the log. Useful between attack runs. Returns how many entries went."""
    count = len(read_entries())
    if config.AUDIT_LOG.exists():
        config.AUDIT_LOG.unlink()
    return count


def entries_for(content_id: str) -> list[dict]:
    """Every entry touching one content id, in order."""
    return [e for e in read_entries() if e.get("content_id") == content_id]
