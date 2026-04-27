"""modules/speech.py — Formal MUN opening speech generator."""

from config import WORDS_PER_MINUTE
from utils.ai_client import run_module
from utils.humanizer import humanize_speech

_SYSTEM = (
    "You are a UN speechwriter and MUN Best Delegate coach. "
    "Write speeches that sound natural when spoken aloud. "
    "Avoid essay tone. Use rhythm, pauses, and rhetorical emphasis."
)


def _build_prompt(
    country: str,
    topic: str,
    committee: str,
    duration_minutes: int,
    tone: str = "formal diplomatic",
    focus: str = "policy, cooperation",
) -> str:
    word_count = duration_minutes * WORDS_PER_MINUTE
    return f"""Country: {country}
Topic: {topic}
Committee: {committee}
Tone: {tone}
Focus: {focus}
Target duration: {duration_minutes} minute(s) (~{word_count} words)

Write a formal MUN opening speech for {country}'s delegation structured as:

1. **Salutation** — address the Chair and delegates formally
2. **Position Statement** — 2-3 sentences on {country}'s stance on {topic}
3. **First Argument** — developed point with 2-3 sentences of reasoning
4. **Second Argument** — a distinct second point with 2-3 sentences of reasoning
5. **Call to Action** — what {country} proposes this committee should do
6. **Formal Closing** — diplomatic close

Rules:
- Continuous prose paragraphs only — NO bullet points
- Tone: authoritative, collaborative, not combative
- Target ~{word_count} words
- Begin: "Honorable Chair, distinguished delegates, and esteemed guests,"
- End: "I thank you." or equivalent
- Use varied sentence length and spoken cadence
- Maintain persuasive diplomatic tone without sounding robotic
- Avoid repetitive phrasing and formulaic transitions"""


def _mock(country: str, topic: str, committee: str) -> str:
    return f"""Honorable Chair, distinguished delegates, and esteemed guests,

The delegation of {country} rises today to address one of the most consequential issues before this {committee}: {topic}. We do so not merely as representatives of our nation, but as committed members of an international order built on the shared promise of collective responsibility and mutual respect.

{country}'s position on {topic} is clear and consistent. We believe any lasting solution must be rooted in equity, evidence, and the genuine participation of all member states — particularly those whose voices have historically been marginalised in these proceedings. A resolution crafted without inclusive negotiation is not a resolution; it is an imposition, and it will fail accordingly.

On implementation, this delegation draws the committee's attention to a fundamental asymmetry that too often goes unaddressed. The nations with the greatest capacity to act swiftly are not always the nations that bear the greatest burden. {country} has consistently advocated for phased, milestone-based frameworks that protect economic development trajectories while maintaining genuine commitment to our shared goals — not to obstruct progress, but because ambitious language without realistic pathways produces neither compliance nor trust.

Furthermore, {country} calls on this committee to embed a robust, representative monitoring mechanism at the heart of any resolution adopted here. Accountability cannot be selective. The oversight structures we create must reflect the diversity of this body, not the preferences of its most powerful members.

The delegation of {country} stands ready to engage constructively with all partners. We urge every delegation to approach the days ahead with the seriousness, flexibility, and genuine diplomatic will that this issue demands.

I thank you."""


def generate_speech(
    country: str,
    topic: str,
    committee: str,
    duration_minutes: int = 2,
    tone: str = "formal diplomatic",
    focus: str = "policy, cooperation",
) -> str:
    """Return a formatted opening speech as prose markdown."""
    speech = run_module(
        prompt=_build_prompt(country, topic, committee, duration_minutes, tone, focus),
        system=_SYSTEM,
        mock_fn=lambda: _mock(country, topic, committee),
        label="Speech",
    )
    return humanize_speech(speech)
