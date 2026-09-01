"""
The two stores: the append-only audit log and the per-creator reputation tally.

Both of these hold up promises the service makes to writers: that a decision
is on the record, and that an appeal never overwrites it. So the ways they can
fail get tested directly here, not only through the routes.
"""

import pytest

from authentiwrite import audit, config, creators

pytestmark = pytest.mark.usefixtures("isolated_logs")


# ── audit log ─────────────────────────────────────────────────────────────────


def test_reading_a_log_that_does_not_exist_yet_returns_empty():
    assert audit.read_entries() == []


def test_entries_come_back_oldest_first():
    for i in range(3):
        audit.log_decision(content_id=f"c{i}", creator_id="asrar", guess="human")
    assert [e["content_id"] for e in audit.read_entries()] == ["c0", "c1", "c2"]


def test_limit_keeps_the_most_recent():
    for i in range(5):
        audit.log_decision(content_id=f"c{i}", creator_id="asrar", guess="human")
    assert [e["content_id"] for e in audit.read_entries(limit=2)] == ["c3", "c4"]


def test_a_decision_carries_the_standard_fields():
    audit.log_decision(
        content_id="c1", creator_id="asrar", guess="ai",
        model_score=0.8, style_score=0.4, combined_score=0.6, label="…",
    )
    entry = audit.read_entries()[0]
    for field in (
        "timestamp", "content_id", "creator_id", "guess",
        "model_score", "style_score", "combined_score", "label", "status",
    ):
        assert field in entry


def test_extra_fields_are_written_through():
    audit.log_decision(content_id="c1", creator_id="asrar", guess="ai", pattern_score=0.33)
    assert audit.read_entries()[0]["pattern_score"] == 0.33


def test_one_corrupt_line_does_not_take_down_the_log():
    """
    A log you can't read at all because of one bad row is worse than a log
    with a gap in it. The entries either side must still come back.
    """
    audit.log_decision(content_id="c1", creator_id="asrar", guess="human")
    with config.AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write("{not json at all\n")
    audit.log_decision(content_id="c2", creator_id="asrar", guess="human")

    entries = audit.read_entries()
    assert [e["content_id"] for e in entries] == ["c1", "c2"]


def test_blank_lines_are_skipped():
    audit.log_decision(content_id="c1", creator_id="asrar", guess="human")
    with config.AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write("\n\n")
    assert len(audit.read_entries()) == 1


def test_entries_for_returns_only_that_content_id_in_order():
    audit.log_decision(content_id="c1", creator_id="asrar", guess="human")
    audit.log_decision(content_id="c2", creator_id="asrar", guess="ai")
    audit.log_appeal(content_id="c1", creator_id="asrar", reasoning="mine")

    entries = audit.entries_for("c1")
    assert len(entries) == 2
    assert entries[0]["status"] == "decided"
    assert entries[1]["event"] == "appeal"


def test_an_appeal_appends_rather_than_edits():
    audit.log_decision(content_id="c1", creator_id="asrar", guess="ai")
    before = dict(audit.read_entries()[0])
    audit.log_appeal(content_id="c1", creator_id="asrar", reasoning="mine")
    assert audit.read_entries()[0] == before


def test_non_ascii_survives_a_round_trip():
    audit.log_decision(content_id="c1", creator_id="asrar", guess="human", label="ümlaut ✓ 🙂")
    assert audit.read_entries()[0]["label"] == "ümlaut ✓ 🙂"


# ── creators ──────────────────────────────────────────────────────────────────


def test_a_new_creator_has_zeroed_counts():
    assert creators.get_record("nobody") == {"ai_count": 0, "human_count": 0, "unsure_count": 0}


@pytest.mark.parametrize("guess", ["ai", "human", "unsure"])
def test_each_guess_increments_its_own_counter(guess):
    creators.record_guess("asrar", guess)
    assert creators.get_record("asrar")[f"{guess}_count"] == 1


def test_an_unknown_guess_is_a_no_op():
    creators.record_guess("asrar", "maybe")
    assert sum(creators.get_record("asrar").values()) == 0


@pytest.mark.parametrize("creator_id", [None, "", "   ", 42, {"id": "x"}])
def test_an_unusable_creator_id_is_a_no_op(creator_id):
    """Nothing to attribute the decision to means nothing to update."""
    assert creators.record_guess(creator_id, "human") == {}


def test_verified_means_more_human_guesses_than_ai():
    creators.record_guess("asrar", "human")
    assert creators.is_verified("asrar")
    creators.record_guess("asrar", "ai")
    assert not creators.is_verified("asrar"), "a tie is not a majority"


def test_a_creator_with_no_history_is_not_verified():
    """0 is not greater than 0, so a first-time writer isn't vouched for."""
    assert not creators.is_verified("brand_new")


def test_verification_note_is_none_without_a_creator_id():
    assert creators.verification_note(None) is None
    assert creators.verification_note("  ") is None


def test_verification_note_pluralises():
    creators.record_guess("asrar", "unsure")
    note = creators.verification_note("asrar")
    assert "unsure 1 time." in note, "a count of 1 should not read '1 times'"
    assert "0 times" in note


def test_a_corrupt_store_degrades_to_empty_rather_than_raising():
    """A bad store shouldn't take down every route that reads reputation."""
    config.CREATORS_STORE.write_text("{not json", encoding="utf-8")
    assert creators.get_record("asrar")["human_count"] == 0


def test_a_store_that_is_not_an_object_degrades_to_empty():
    config.CREATORS_STORE.write_text('["not", "a", "dict"]', encoding="utf-8")
    assert creators.get_record("asrar")["human_count"] == 0


@pytest.mark.parametrize("bad", ['{"asrar": {"human_count": "lots"}}',
                                 '{"asrar": {"human_count": -5}}',
                                 '{"asrar": {"human_count": true}}',
                                 '{"asrar": "not a record"}'])
def test_a_malformed_record_is_normalised_not_trusted(bad):
    config.CREATORS_STORE.write_text(bad, encoding="utf-8")
    assert creators.get_record("asrar")["human_count"] == 0


def test_counts_survive_a_reload():
    creators.record_guess("asrar", "human")
    creators.record_guess("asrar", "human")
    assert creators.get_record("asrar")["human_count"] == 2
