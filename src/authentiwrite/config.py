"""
Everything tunable in one place: host and port, which detector model to use,
the signal weights, the label thresholds, the rate limits, and the file paths.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


# ─── The service ─────────────────────────────────────────────────────────────

# `127.0.0.1` is loopback, meaning only this machine can reach it. A host
# serving outside traffic needs `0.0.0.0`, and the env var provides that
# without changing the default for local curl calls.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Flask's debug mode hands anyone who can reach the service an interactive
# Python prompt inside the process. That's safe on loopback and dangerous
# anywhere else, so it switches itself off as soon as HOST isn't loopback.
DEBUG = os.getenv("AUTHENTIWRITE_DEBUG", "1") == "1" and HOST in ("127.0.0.1", "localhost")


# ─── The local model ─────────────────────────────────────────────────────────
# Signal one runs a language model on this machine. No account, no key. The
# first run downloads about 550 MB. What it measures is how predictable the
# text is to a language model, on the idea that text a model finds easy to
# predict is more likely to be text a model wrote. See detector.py for the
# blind spot that comes with that idea.
#
# The first call is slow, roughly 10 to 20 seconds while the model loads into
# memory. After that a submission takes a second or two.

DETECTOR_MODEL = os.getenv("AUTHENTIWRITE_DETECTOR_MODEL", "gpt2")

# Longer text gives a steadier reading but takes longer to score. 400 tokens
# is roughly 300 words, which is enough for the signal to mean something.
DETECTOR_MAX_TOKENS = 400


# ─── Input bounds ─────────────────────────────────────────────────────────────
# The largest a single submission can be, in characters. The model signal cuts
# text off at DETECTOR_MAX_TOKENS (about 300 words) regardless, so anything
# past that adds no extra signal. This limit exists to cap the work the style
# and pattern passes do, since both of them scan the whole string.
#
# 25,000 characters is roughly a 4,000-word piece. That's longer than more or
# less any single submission a writing platform receives, and still small
# enough that scanning it is cheap. Set well above real use and well below
# unlimited. See app.py::_validate_text.

MAX_TEXT_CHARS = 25_000


# ─── Scoring weights ──────────────────────────────────────────────────────────
# How much each signal counts toward the combined score. See docs/DECISIONS.md
# for how these numbers were chosen and later revised.

WEIGHT_MODEL_SIGNAL = 0.45
WEIGHT_STYLE_SIGNAL = 0.40
WEIGHT_PATTERN_SIGNAL = 0.15


# ─── Label thresholds ─────────────────────────────────────────────────────────
# Where one label turns into another. Scores run from 0.0 (confidently human)
# to 1.0 (confidently AI).
#
#   score < HUMAN_THRESHOLD          -> high-confidence human
#   between the two                  -> unsure
#   score > AI_THRESHOLD             -> high-confidence AI
#
# See docs/DECISIONS.md for the false-positive trade-off behind these values.

HUMAN_THRESHOLD = 0.35
AI_THRESHOLD = 0.55

# A weighted average can only land somewhere between its inputs. So if any one
# signal is stuck at a constant, the combined score can never leave the range
# that constant implies, no matter what the other signals say.
# scoring.label_ranges() prints the bands as currently configured.


# ─── Rate limiting ────────────────────────────────────────────────────────────
# See docs/DECISIONS.md for why these particular numbers.

RATE_LIMITING_ENABLED = True

RATE_LIMIT_PER_MINUTE = 6
RATE_LIMIT_PER_DAY = 120

# Flask-Limiter warns loudly if this isn't set. In-memory storage is fine for
# a single process. A restart forgets every count, and separate instances
# wouldn't share limits with each other.
RATE_LIMIT_STORAGE = "memory://"

# ─── Batch submission ─────────────────────────────────────────────────────────
# /submit/batch scores several texts in one call. Each item still costs one
# model pass, one style pass, and one phrase pass, so a batch with no cap
# would be the rate limit with extra steps. Capped on its own, separately from
# RATE_LIMIT_PER_MINUTE.

BATCH_MAX_ITEMS = 20


# ─── Paths ───────────────────────────────────────────────────────────────────

LOG_DIR = ROOT / "logs"
AUDIT_LOG = LOG_DIR / "audit.jsonl"
RESULTS_DIR = ROOT / "results"

# Per-creator reputation counts. This is current state rather than an
# append-only log, so it lives in its own small file instead of in
# audit.jsonl. See creators.py.
CREATORS_STORE = LOG_DIR / "creators.json"
