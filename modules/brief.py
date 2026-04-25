"""modules/brief.py — Country position and intelligence brief generator."""

from utils.ai_client import run_module

_SYSTEM = (
    "You are a senior UN diplomat and policy analyst with 20 years of experience "
    "briefing delegations before major multilateral conferences."
)


def _build_prompt(country: str, topic: str, committee: str) -> str:
    return f"""Country: {country}
Topic: {topic}
Committee: {committee}

Generate a structured diplomatic intelligence brief using EXACTLY these bold headers:

**OFFICIAL POSITION**
[2-3 sentences on {country}'s formal stance on {topic}]

**HISTORICAL CONTEXT**
[2-3 sentences on past treaties, votes, or events relevant to {country} and {topic}]

**KEY PRIORITIES**
[3 bullet points — what {country} wants to achieve in {committee}]

**ALLIANCES & BLOCS**
[Regional or ideological groups {country} aligns with on {topic}]

**RED LINES**
[2 specific things {country} will never concede on this topic]

Style: intelligence-brief. Precise, no filler. Grounded in real geopolitics."""


def _mock(country: str, topic: str, committee: str) -> str:
    return f"""**OFFICIAL POSITION**
{country} maintains a pragmatic stance on {topic}, advocating for multilateral cooperation frameworks that balance national sovereignty with shared global responsibilities. The delegation consistently emphasises evidence-based policy and equitable burden-sharing.

**HISTORICAL CONTEXT**
{country} has participated in key international agreements related to {topic} over the past two decades, often acting as a bridge between developed and developing nation blocs. Its voting record in {committee} reflects conditional support tied to implementation guarantees.

**KEY PRIORITIES**
- Secure binding commitments from major powers on resource allocation for {topic}
- Preserve developing-nation exemptions in any new regulatory framework
- Establish an independent monitoring mechanism with equal regional representation

**ALLIANCES & BLOCS**
{country} traditionally aligns with the G77 on {topic} while maintaining pragmatic bilateral channels with major Western powers. In {committee} it frequently co-sponsors resolutions with similarly positioned middle-income states.

**RED LINES**
- Will not accept provisions that impose disproportionate compliance costs on developing economies
- Opposes any language granting external bodies unilateral enforcement powers over domestic policy"""


def generate_brief(country: str, topic: str, committee: str) -> str:
    """Return a formatted markdown country brief, falling back to mock on failure."""
    return run_module(
        prompt=_build_prompt(country, topic, committee),
        system=_SYSTEM,
        mock_fn=lambda: _mock(country, topic, committee),
        label="Country Brief",
    )
