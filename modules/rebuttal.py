"""modules/rebuttal.py — Formal MUN rebuttal generator."""

from utils.ai_client import run_module

_SYSTEM = (
    "You are an expert MUN debate trainer specialising in quick-response diplomacy. "
    "You craft rebuttals that are sharp, respectful, and devastatingly logical."
)

_EMPTY_INPUT_MSG = "⚠️ Please enter the opposing delegate's argument above."


def _build_prompt(country: str, topic: str, opposing_argument: str, own_position: str) -> str:
    return f"""You are the delegate for {country} in a MUN debate on {topic}.

Opposing argument: "{opposing_argument}"

Your country's position: {own_position}

Write a formal rebuttal using EXACTLY these four sections:

**ACKNOWLEDGMENT**
[One sentence showing you heard the delegate — respectful, not sycophantic]

**COUNTER-POINT 1**
[Challenge a factual or logical flaw — specific, cite real concepts or examples]

**COUNTER-POINT 2**
[Offer {country}'s alternative framing — reposition the narrative]

**REDIRECT**
[One strong sentence steering the room back to your key priority]

Constraints: under 150 words total; deliverable in 90 seconds; confident, diplomatic, no personal attacks."""


def _mock(country: str, topic: str) -> str:
    return f"""**ACKNOWLEDGMENT**
The delegation of {country} thanks the previous speaker and acknowledges the sincerity with which their argument was presented.

**COUNTER-POINT 1**
However, the assertion that the proposed measures would deliver equitable outcomes is not supported by evidence. Historical precedent in comparable multilateral frameworks demonstrates that top-down mandates without differentiated responsibility clauses consistently produce partial compliance and diplomatic friction — not the cohesion this committee seeks.

**COUNTER-POINT 2**
{country}'s position offers a more sustainable alternative: a consent-based, milestone-driven approach that achieves the same long-term objectives while preserving the developmental autonomy of nations that did not create this problem but are asked to absorb its costs.

**REDIRECT**
This committee must ask itself not whether to act, but whether to act in a way the entire international community can sustain — and on that question, {country}'s proposal provides the only credible answer."""


def generate_rebuttal(country: str, topic: str, opposing_argument: str, own_position: str = "") -> str:
    """Return a structured rebuttal as formatted markdown."""
    if not opposing_argument.strip():
        return _EMPTY_INPUT_MSG

    return run_module(
        prompt=_build_prompt(country, topic, opposing_argument, own_position),
        system=_SYSTEM,
        mock_fn=lambda: _mock(country, topic),
        label="Rebuttal",
    )
