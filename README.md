# PolicySim Diplomat — AI Research Assistant for MUN Conferences

PolicySim Diplomat is a Streamlit app that helps Model UN delegates generate country-specific briefing content in seconds. It produces structured outputs for policy briefs, arguments, speeches, and rebuttals using Claude (with rich mock fallback for demos).

## Features

- Country intelligence brief with official position, alliances, and red lines
- Structured 4-point argument generator for moderated caucus and debate rounds
- Opening speech generator tuned to selected duration
- Rebuttal builder for rapid responses to opposing positions
- Demo-safe architecture with API fallback to mock mode
- Premium dark diplomatic UI with clear tabbed workflow

## Tech Stack

- Python 3.10+
- Streamlit
- Anthropic Python SDK

## Installation

```bash
git clone <your-repo-url>
cd PolicySIm
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install streamlit anthropic
```

## How to Run

```bash
streamlit run app.py
```

## Example Use Case (MUN Scenario)

A delegate representing **India** in **UNGA** on **Climate Finance for Developing Nations** can:

1. Generate a country brief to define policy stance and negotiating limits.
2. Create four podium-ready arguments for caucus interventions.
3. Produce a timed opening speech for formal session.
4. Generate a rebuttal after pasting an opposing delegate’s argument.

## Demo Flow

1. Select your country.
2. Enter agenda topic and committee.
3. Click **Analyse**.
4. Use four output tabs: Brief, Arguments, Speech, Rebuttal.
5. Copy and adapt text to your conference style.

## Future Improvements

- Citation-backed factual grounding per section
- Export to DOCX/PDF
- Saving and comparing multiple drafting iterations
- Committee-specific prompt packs
