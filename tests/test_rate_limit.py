"""
Rate limiting.

The limiter counts against `creator_id` from the request body rather than the
caller's IP. That closes the one gap an attacker can't get around by changing
source addresses. These tests are the reason `client` resets limiter state
everywhere else, because here the limit gets tripped on purpose.
"""

import pytest

from authentiwrite import audit, config

pytestmark = [
    pytest.mark.usefixtures("fake_signals", "reset_limiter"),
    pytest.mark.skipif(
        not config.RATE_LIMITING_ENABLED,
        reason="rate limiting is switched off in config.py",
    ),
]

ORDINARY = "This is an ordinary sentence written by an ordinary person today."


def _submit(client, creator_id):
    return client.post("/submit", json={"text": ORDINARY, "creator_id": creator_id})


def test_the_per_minute_limit_is_enforced(client):
    """Exactly RATE_LIMIT_PER_MINUTE get through; the next one is refused."""
    codes = [_submit(client, "flooder").status_code for _ in range(config.RATE_LIMIT_PER_MINUTE + 3)]
    assert codes[: config.RATE_LIMIT_PER_MINUTE] == [200] * config.RATE_LIMIT_PER_MINUTE
    assert set(codes[config.RATE_LIMIT_PER_MINUTE :]) == {429}


def test_the_limit_is_per_creator_not_global(client):
    """One writer hitting their limit must not lock out everyone else."""
    for _ in range(config.RATE_LIMIT_PER_MINUTE + 1):
        _submit(client, "noisy")
    assert _submit(client, "noisy").status_code == 429
    assert _submit(client, "quiet").status_code == 200


def test_rotating_creator_id_does_not_evade_the_limit_for_one_creator(client):
    """
    Counting against creator_id is what makes the limit mean anything. A
    script can change its id, but then it is no longer submitting as that
    writer.
    """
    for _ in range(config.RATE_LIMIT_PER_MINUTE):
        assert _submit(client, "target").status_code == 200
    assert _submit(client, "target").status_code == 429
    assert _submit(client, "target").status_code == 429


def test_a_rate_limited_request_is_still_logged(client):
    """A flood of blocked requests should leave a trace, not silence."""
    for _ in range(config.RATE_LIMIT_PER_MINUTE + 2):
        _submit(client, "flooder")

    rate_limited = [e for e in audit.read_entries() if e.get("reason") == "rate_limited"]
    assert rate_limited, "no rate_limited entry was written"
    assert rate_limited[0]["creator_id"] == "flooder"


def test_the_429_body_explains_itself(client):
    for _ in range(config.RATE_LIMIT_PER_MINUTE + 1):
        response = _submit(client, "flooder")
    body = response.get_json()
    assert body["error"] == "rate_limited"
    assert "limit" in body
