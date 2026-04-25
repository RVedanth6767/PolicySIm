"""modules/arguments.py — Structured debate argument generator."""

from utils.ai_client import run_module

_SYSTEM = (
    "You are an expert MUN debate coach who has trained delegates at HMUN, NMUN, "
    "and THIMUN. You craft razor-sharp arguments that win Best Delegate awards."
)


def _build_prompt(country: str, topic: str, brief_summary: str) -> str:
    return f"""Country: {country}
Topic: {topic}
Position Context: {brief_summary}

Generate exactly 4 structured debate arguments for {country}'s delegation.
Use this format for EVERY argument — no deviation:

**ARGUMENT 1: [TITLE IN CAPS]**
- **Opening Line:** [One punchy podium sentence]
- **Evidence & Reasoning:** [2-3 sentences of substantive reasoning]
- **Closing Assert:** [One declarative sentence to land the point]

**ARGUMENT 2: [TITLE IN CAPS]**
- **Opening Line:** [One punchy podium sentence]
- **Evidence & Reasoning:** [2-3 sentences]
- **Closing Assert:** [One declarative sentence]

**ARGUMENT 3: [TITLE IN CAPS]**
- **Opening Line:** [One punchy podium sentence]
- **Evidence & Reasoning:** [2-3 sentences]
- **Closing Assert:** [One declarative sentence]

**ARGUMENT 4: [TITLE IN CAPS]**
- **Opening Line:** [One punchy podium sentence]
- **Evidence & Reasoning:** [2-3 sentences]
- **Closing Assert:** [One declarative sentence]

Each argument must be distinct, assertive, diplomatically worded, and grounded in real-world geopolitical or economic logic."""


def _mock(country: str, topic: str) -> str:
    return f"""**ARGUMENT 1: SOVEREIGNTY AND EQUITABLE BURDEN-SHARING**
- **Opening Line:** The international community cannot solve {topic} by placing disproportionate obligations on nations that contributed least to the problem.
- **Evidence & Reasoning:** Historical data consistently shows that top industrialised economies account for the majority of cumulative impact on {topic}, yet current frameworks demand equal sacrifice from all signatories. {country} stands with the Global South in insisting that responsibility be calibrated to historical contribution, not merely current capacity.
- **Closing Assert:** Any framework that ignores this principle is not multilateralism — it is an inequitable status quo dressed in diplomatic language.

**ARGUMENT 2: TECHNOLOGY TRANSFER AS A NON-NEGOTIABLE PILLAR**
- **Opening Line:** Commitments without capacity are nothing more than performative diplomacy.
- **Evidence & Reasoning:** For {country} and peer nations to implement ambitious targets on {topic}, access to cutting-edge technology at accessible costs is essential. Existing intellectual property barriers and high licensing fees systematically exclude developing nations from the tools they need. {country} calls for a binding technology-transfer mechanism as a precondition, not an afterthought.
- **Closing Assert:** This committee must ensure that the gap between ambition and implementation is bridged by resources, not rhetoric.

**ARGUMENT 3: MONITORING MUST BE TRANSPARENT AND REPRESENTATIVE**
- **Opening Line:** Trust in any resolution depends entirely on whether every signatory believes the oversight mechanism is fair.
- **Evidence & Reasoning:** Historically, monitoring bodies on {topic} have been dominated by a handful of powerful states, creating structural bias in enforcement. {country} proposes rotating representation, independent verification, and public reporting as the three pillars of a credible compliance framework. Compliance failures in unbalanced systems are rational responses to structural unfairness, not acts of bad faith.
- **Closing Assert:** Legitimacy is earned through equity, and this delegation will not support any mechanism that fails that test.

**ARGUMENT 4: PHASED IMPLEMENTATION PROTECTS DEVELOPMENT**
- **Opening Line:** Progress on {topic} must not come at the cost of the economic futures of billions of people.
- **Evidence & Reasoning:** Immediate sweeping mandates would force {country} and comparable nations to choose between international compliance and domestic stability. A phased, milestone-based approach — as piloted in previous multilateral frameworks — allows genuine progress while protecting development pathways. {country} is not opposing ambition; it is protecting the conditions under which ambition can actually be achieved.
- **Closing Assert:** The delegation calls on this committee to build a framework the entire world can sustain, not only the nations that can absorb the cost."""


def generate_arguments(country: str, topic: str, brief_summary: str = "") -> str:
    """Return 4 structured debate arguments as formatted markdown."""
    return run_module(
        prompt=_build_prompt(country, topic, brief_summary),
        system=_SYSTEM,
        mock_fn=lambda: _mock(country, topic),
        label="Arguments",
    )
