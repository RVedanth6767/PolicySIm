"""config.py — Global configuration for PolicySim Diplomat."""

import os

# ── Anthropic API ─────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL_NAME = "claude-sonnet-4-20250514"
MAX_TOKENS = 1200

# ── App Identity ──────────────────────────────────────────────────────────────
APP_TITLE = "PolicySim Diplomat"
APP_ICON = "🌐"

# ── Feature Flags ─────────────────────────────────────────────────────────────
USE_MOCK = not bool(ANTHROPIC_API_KEY)

# ── Module-level constants ────────────────────────────────────────────────────
BRIEF_SUMMARY_LENGTH = 400
WORDS_PER_MINUTE = 130
