"""Post-processing utilities to make generated speeches sound more natural."""

from __future__ import annotations

import re

OPENERS = [
    "Let us be clear,",
    "We must acknowledge that",
    "The reality is,",
]

TRANSITIONS = ["However,", "Furthermore,"]

CLOSINGS = [
    "Let this committee choose resolve over rhetoric, and action over delay.",
    "History will judge not what we promised, but what we delivered together.",
    "Our words matter today only if they become measurable commitments tomorrow.",
]


def _split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if not cleaned:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]


def humanize_speech(text: str) -> str:
    """Humanize speech text while preserving diplomatic tone and coherence."""
    sentences = _split_sentences(text)
    if len(sentences) < 3:
        return text

    if not any(sentences[0].startswith(phrase) for phrase in OPENERS):
        sentences[1] = f"{OPENERS[0]} {sentences[1][0].lower() + sentences[1][1:] if len(sentences[1]) > 1 else sentences[1]}"

    mid_idx = min(max(len(sentences) // 2, 2), len(sentences) - 2)
    if not any(token in sentences[mid_idx] for token in TRANSITIONS):
        sentences[mid_idx] = f"{TRANSITIONS[mid_idx % len(TRANSITIONS)]} {sentences[mid_idx]}"

    if len(sentences) >= 6 and not any(close in sentences[-1] for close in CLOSINGS):
        sentences.append(CLOSINGS[len(sentences) % len(CLOSINGS)])

    rebuilt = []
    for idx, sentence in enumerate(sentences):
        rebuilt.append(sentence)
        if idx in {1, 4}:
            rebuilt.append("")

    return "\n\n".join(chunk for chunk in rebuilt if chunk is not None).strip()
