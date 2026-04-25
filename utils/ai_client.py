"""utils/ai_client.py — Anthropic API wrapper and module execution helper."""

from typing import Callable

import anthropic

from config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS, USE_MOCK
from utils.formatter import format_output, safe_parse


def call_claude(prompt: str, system: str = "") -> str:
    """
    Send a prompt to Claude and return the plain-text response.
    Raises RuntimeError if no text block is found in the response.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    kwargs: dict = {
        "model": MODEL_NAME,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)

    for block in response.content:
        if hasattr(block, "text"):
            return block.text

    raise RuntimeError("Claude returned no text content.")


def run_module(
    prompt: str,
    system: str,
    mock_fn: Callable[[], str],
    label: str,
) -> str:
    """
    Standard execution pipeline shared by every generator module.
    """
    if USE_MOCK:
        return format_output(mock_fn())

    try:
        raw = call_claude(prompt, system=system)
        return safe_parse(format_output(raw), fallback_label=label)
    except Exception as exc:
        warning = f"⚠️ **{label} generation failed:** {exc}\n\n"
        return warning + format_output(mock_fn())
