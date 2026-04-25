"""utils/formatter.py — Text cleanup and parsing helpers for AI output."""

import re


def clean_text(text: str) -> str:
    """Strip surrounding whitespace and collapse 3+ blank lines to two."""
    text = text.strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def format_output(raw: str) -> str:
    """Canonical formatter used by every module."""
    return clean_text(raw)


def extract_sections(text: str) -> dict[str, str]:
    """Parse **BOLD HEADERS** into a {title: body} mapping."""
    pattern = r"\*\*(.+?)\*\*\s*\n(.*?)(?=\*\*|\Z)"
    matches = re.findall(pattern, text, flags=re.DOTALL)
    if not matches:
        return {"full": clean_text(text)}
    return {title.strip(): body.strip() for title, body in matches}


def safe_parse(raw: str, fallback_label: str = "Output") -> str:
    """Return cleaned text, or a user-facing message if raw is empty."""
    if not raw or not raw.strip():
        return f"⚠️ **{fallback_label}**: No content was returned. Please try again."
    return format_output(raw)
