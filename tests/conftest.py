"""
Shared fixtures.

Every test that touches a route or the audit log gets a throwaway log
directory. Without that, running the suite would append to the real
logs/audit.jsonl and logs/creators.json, which hold the recorded evidence
behind docs/RESEARCH.md.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from authentiwrite import config  # noqa: E402


@pytest.fixture
def isolated_logs(tmp_path, monkeypatch):
    """Point every filesystem path in config at a per-test temp directory."""
    monkeypatch.setattr(config, "LOG_DIR", tmp_path)
    monkeypatch.setattr(config, "AUDIT_LOG", tmp_path / "audit.jsonl")
    monkeypatch.setattr(config, "CREATORS_STORE", tmp_path / "creators.json")
    monkeypatch.setattr(config, "RESULTS_DIR", tmp_path / "results")
    return tmp_path


@pytest.fixture
def client(isolated_logs):
    """
    A Flask test client whose writes land in the temp log directory.

    The rate limiter's in-memory counters live on the module-level app, so
    without help they carry across tests. A suite making more than
    RATE_LIMIT_PER_MINUTE requests would start getting 429s that have nothing
    to do with what's being tested. So the counters get reset between tests.
    test_rate_limit.py is where the limiter gets exercised on purpose.
    """
    from authentiwrite import app as appmod

    appmod.app.config["TESTING"] = True
    _reset_rate_limiter(appmod)
    return appmod.app.test_client()


def _reset_rate_limiter(appmod):
    """Clear the limiter's counters, if rate limiting is switched on."""
    limiter = getattr(appmod, "limiter", None)
    storage = getattr(limiter, "storage", None)
    if storage is not None:
        storage.reset()


@pytest.fixture
def reset_limiter():
    """Clear limiter state by hand, for tests that trip the limit on purpose."""
    from authentiwrite import app as appmod

    _reset_rate_limiter(appmod)
    yield
    _reset_rate_limiter(appmod)


@pytest.fixture
def fake_signals(monkeypatch):
    """
    Replace the three signals with constants.

    These tests are about how the routes behave, meaning validation, logging,
    labelling, and appeals. The real model signal loads about 550 MB and takes
    seconds per call, which none of that needs. The signal arithmetic itself
    is tested against the real functions in test_scoring.py, so nothing here
    depends on these stub values being realistic.
    """
    from authentiwrite import detector, phrasing, stylometry

    monkeypatch.setattr(detector, "model_signal", lambda text: 0.5)
    monkeypatch.setattr(stylometry, "style_signal", lambda text: 0.5)
    monkeypatch.setattr(phrasing, "pattern_signal", lambda text: 0.0)
