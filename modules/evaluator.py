from utils.ai_client import run_module

_SYSTEM = (
    "You are a senior MUN chair and judge who evaluates speeches at HMUN, THIMUN, and Harvard WorldMUN."
)


def _build_prompt(speech: str, country: str, topic: str) -> str:
    return f"""
Country: {country}
Topic: {topic}

Speech:
{speech}

Evaluate this MUN speech like a professional judge.

Return EXACTLY:

**SCORE**
[Number from 1 to 10]

**STRENGTHS**
- [Point 1]
- [Point 2]
- [Point 3]

**IMPROVEMENTS**
- [Specific actionable feedback]
- [Specific actionable feedback]

**FINAL REMARK**
[2-3 sentence overall judge-style comment]

Criteria:
- Diplomacy
- Clarity
- Structure
- Persuasiveness
- Realism (does it sound human and natural?)
"""


def generate_evaluation(country: str, topic: str, speech: str) -> str:
    return run_module(
        prompt=_build_prompt(speech, country, topic),
        system=_SYSTEM,
        mock_fn=lambda: """**SCORE**
8

**STRENGTHS**
- Strong diplomatic tone
- Clear structure
- Good opening

**IMPROVEMENTS**
- Add more real-world references
- Improve emotional engagement

**FINAL REMARK**
A solid and confident speech with strong fundamentals, but it can be elevated with more specificity and rhetorical depth.""",
        label="Speech Evaluation",
    )
