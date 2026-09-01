"""
The HTTP routes: validation, scoring, the appeal path, and the audit log.

Every test here uses the `isolated_logs` fixture through `client`, so nothing
writes to the real logs/ directory. The three signals are stubbed to fixed
values by `fake_signals`, since these tests are about how the routes behave
rather than about what the signals return.
"""

import json

import pytest

from authentiwrite import audit, config, creators

pytestmark = pytest.mark.usefixtures("fake_signals")

ORDINARY = "This is an ordinary sentence written by an ordinary person today."


# ── /submit: input validation ─────────────────────────────────────────────────


@pytest.mark.parametrize(
    "body, why",
    [
        ({}, "no text field at all"),
        ({"text": ""}, "empty text"),
        ({"text": "   "}, "whitespace only"),
        ({"text": "two words"}, "under the three-word minimum"),
        ({"text": 12345}, "text is a number"),
        ({"text": ["a", "b"]}, "text is a list"),
        ({"text": None}, "text is null"),
    ],
)
def test_bad_text_is_rejected_with_400(client, body, why):
    response = client.post("/submit", json=body)
    assert response.status_code == 400, why
    assert response.get_json()["error"] == "invalid_input"


def test_oversized_text_is_rejected_before_scoring(client):
    """
    Criterion 5. Text past config.MAX_TEXT_CHARS must not reach the signals.
    A submission with no size limit is a way to exhaust resources, not just a
    correctness problem.
    """
    response = client.post(
        "/submit", json={"text": "word " * config.MAX_TEXT_CHARS, "creator_id": "huge"}
    )
    assert response.status_code == 400
    assert "exceed" in response.get_json()["message"]


def test_text_just_under_the_limit_is_accepted(client):
    """The limit has to let real writing through, not just block the extremes."""
    text = "word " * (config.MAX_TEXT_CHARS // 10)
    assert len(text) < config.MAX_TEXT_CHARS
    assert client.post("/submit", json={"text": text, "creator_id": "big"}).status_code == 200


def test_json_array_body_is_a_400_not_a_500(client):
    """
    Regression test. A JSON-array body is truthy, so
    `get_json(silent=True) or {}` handed a list straight to code that called
    .get() on it. That raised an AttributeError nothing caught, which the
    caller saw as a 500. This is RQ07 in the attack set.
    """
    response = client.post("/submit", data=json.dumps(["text", "creator_id"]),
                           content_type="application/json")
    assert response.status_code == 400


def test_unparseable_body_is_a_400_not_a_500(client):
    response = client.post("/submit", data="{not json at all",
                           content_type="application/json")
    assert response.status_code == 400


@pytest.mark.parametrize("creator_id", [{"id": "x"}, ["a"], 42, ""], ids=["dict", "list", "int", "empty"])
def test_non_string_creator_id_is_rejected(client, creator_id):
    """
    Regression test. A creator_id that wasn't a string scored fine and went
    straight into the log, where no ordinary lookup could find it again. The
    record went missing without any error. This is RQ06 in the attack set.
    """
    response = client.post("/submit", json={"text": ORDINARY, "creator_id": creator_id})
    assert response.status_code == 400


def test_missing_creator_id_is_still_allowed(client):
    """An anonymous submission is a real case. One nobody can look up isn't."""
    response = client.post("/submit", json={"text": ORDINARY})
    assert response.status_code == 200
    assert response.get_json()["creator_note"] is None


# ── /submit: the happy path ───────────────────────────────────────────────────


def test_submit_returns_the_documented_shape(client):
    body = client.post("/submit", json={"text": ORDINARY, "creator_id": "asrar"}).get_json()
    for field in (
        "content_id", "guess", "confidence", "label",
        "model_score", "style_score", "pattern_score", "creator_note",
    ):
        assert field in body, f"missing {field}"
    assert body["guess"] in ("ai", "human", "unsure")
    assert 0.0 <= body["confidence"] <= 1.0


def test_each_submission_gets_its_own_content_id(client):
    first = client.post("/submit", json={"text": ORDINARY, "creator_id": "a"}).get_json()
    second = client.post("/submit", json={"text": ORDINARY, "creator_id": "a"}).get_json()
    assert first["content_id"] != second["content_id"]


def test_a_decision_is_written_to_the_audit_log(client):
    body = client.post("/submit", json={"text": ORDINARY, "creator_id": "asrar"}).get_json()
    entries = audit.entries_for(body["content_id"])
    assert len(entries) == 1
    assert entries[0]["status"] == "decided"
    assert entries[0]["creator_id"] == "asrar"


def test_a_rejection_is_logged_too(client):
    """A request that fails quietly looks exactly like a request nobody sent."""
    client.post("/submit", json={"text": "no", "creator_id": "asrar"})
    rejections = [e for e in audit.read_entries() if e.get("event") == "rejected"]
    assert len(rejections) == 1


# ── /appeal ───────────────────────────────────────────────────────────────────


def test_appeal_moves_status_and_logs_without_editing_the_original(client):
    """
    Criterion 4, plus the append-only promise. The original decision entry has
    to survive being challenged, without being edited.
    """
    submitted = client.post("/submit", json={"text": ORDINARY, "creator_id": "asrar"}).get_json()
    content_id = submitted["content_id"]
    original = dict(audit.entries_for(content_id)[0])

    response = client.post("/appeal", json={"content_id": content_id, "reasoning": "I wrote it."})
    assert response.status_code == 200
    assert response.get_json()["status"] == "under_review"

    entries = audit.entries_for(content_id)
    assert len(entries) == 2
    assert entries[0] == original, "the original decision was modified"
    assert entries[1]["event"] == "appeal"
    assert entries[1]["status"] == "under_review"


def test_appeal_for_unknown_content_id_is_404(client):
    response = client.post("/appeal", json={"content_id": "nope", "reasoning": "x"})
    assert response.status_code == 404


@pytest.mark.parametrize("content_id", [None, {"a": 1}, 42], ids=["null", "dict", "int"])
def test_appeal_with_an_unusable_content_id_is_404_not_a_crash(client, content_id):
    response = client.post("/appeal", json={"content_id": content_id, "reasoning": "x"})
    assert response.status_code == 404


def test_appealed_item_reports_under_review(client):
    submitted = client.post("/submit", json={"text": ORDINARY, "creator_id": "asrar"}).get_json()
    client.post("/appeal", json={"content_id": submitted["content_id"], "reasoning": "mine"})
    body = client.get(f"/content/{submitted['content_id']}").get_json()
    assert body["status"] == "under_review"


# ── /submit/batch ─────────────────────────────────────────────────────────────


def test_batch_scores_every_item(client):
    items = [{"text": ORDINARY, "creator_id": f"w{i}"} for i in range(3)]
    body = client.post("/submit/batch", json={"items": items}).get_json()
    assert body["count"] == 3
    assert all("content_id" in r for r in body["results"])


def test_one_bad_item_does_not_stop_the_rest(client):
    items = [{"text": ORDINARY, "creator_id": "ok"}, {"text": "no"}, {"text": ORDINARY}]
    results = client.post("/submit/batch", json={"items": items}).get_json()["results"]
    assert "content_id" in results[0]
    assert results[1]["error"] == "invalid_input"
    assert "content_id" in results[2]


def test_batch_rejects_an_oversized_batch(client):
    items = [{"text": ORDINARY, "creator_id": "x"}] * (config.BATCH_MAX_ITEMS + 1)
    assert client.post("/submit/batch", json={"items": items}).status_code == 400


@pytest.mark.parametrize("items", [None, [], "nope", {}], ids=["missing", "empty", "string", "dict"])
def test_batch_rejects_a_bad_items_field(client, items):
    assert client.post("/submit/batch", json={"items": items}).status_code == 400


# ── reads: /content, /creator, /stats, /log ───────────────────────────────────


def test_content_lookup_404s_for_an_unknown_id(client):
    assert client.get("/content/nope").status_code == 404


def test_creator_lookup_groups_history_by_content_id(client):
    submitted = client.post("/submit", json={"text": ORDINARY, "creator_id": "asrar"}).get_json()
    client.post("/appeal", json={"content_id": submitted["content_id"], "reasoning": "mine"})

    body = client.get("/creator/asrar").get_json()
    assert body["submission_count"] == 1
    assert len(body["items"][0]["history"]) == 2
    assert body["items"][0]["current_status"] == "under_review"


def test_creator_lookup_404s_for_an_unknown_creator(client):
    assert client.get("/creator/nobody").status_code == 404


def test_stats_counts_decisions_appeals_and_rejections_separately(client):
    submitted = client.post("/submit", json={"text": ORDINARY, "creator_id": "asrar"}).get_json()
    client.post("/appeal", json={"content_id": submitted["content_id"], "reasoning": "mine"})
    client.post("/submit", json={"text": "no"})  # rejected

    body = client.get("/stats").get_json()
    assert body["decisions"] == 1
    assert body["appeals"] == 1
    assert body["rejections"] == 1


def test_log_limit_returns_the_most_recent_entries(client):
    for _ in range(3):
        client.post("/submit", json={"text": ORDINARY, "creator_id": "asrar"})
    body = client.get("/log?limit=2").get_json()
    assert body["count"] == 2


def test_health_reports_service_state(client):
    body = client.get("/health").get_json()
    assert body["ok"] is True
    assert body["detector_model"] == config.DETECTOR_MODEL


def test_ping_echoes(client):
    body = client.post("/ping", json={"message": "hello"}).get_json()
    assert body["ok"] is True
    assert body["you_sent"] == "hello"


# ── reputation ────────────────────────────────────────────────────────────────


def test_creator_note_counts_this_service_own_guesses(client):
    for _ in range(2):
        client.post("/submit", json={"text": ORDINARY, "creator_id": "asrar"})
    record = creators.get_record("asrar")
    assert sum(record.values()) == 2


def test_reputation_never_changes_the_score(client):
    """
    The reputation tally gets shown to the reader and never folded into the
    decision. A writer's history must not move their next score. See
    docs/DECISIONS.md.
    """
    first = client.post("/submit", json={"text": ORDINARY, "creator_id": "repeat"}).get_json()
    for _ in range(4):
        client.post("/submit", json={"text": ORDINARY, "creator_id": "repeat"})
    last = client.post("/submit", json={"text": ORDINARY, "creator_id": "repeat"}).get_json()
    assert first["guess"] == last["guess"]
    assert first["confidence"] == last["confidence"]
