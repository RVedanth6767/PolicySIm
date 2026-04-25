"""app.py — PolicySim Diplomat: AI Research Assistant for MUN Conferences."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from config import APP_TITLE, APP_ICON, USE_MOCK, BRIEF_SUMMARY_LENGTH
from utils.countries import UN_MEMBER_STATES
from utils.ui import (
    render_brief_tab,
    render_arguments_tab,
    render_speech_tab,
    render_rebuttal_tab,
)
from modules.brief import generate_brief
from modules.arguments import generate_arguments
from modules.speech import generate_speech
from modules.rebuttal import generate_rebuttal


st.set_page_config(
    page_title=f"{APP_TITLE} — MUN AI Assistant",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _load_css() -> None:
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    try:
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


_load_css()


def _init_state() -> None:
    defaults: dict = {
        "brief": None,
        "arguments": None,
        "speech": None,
        "rebuttal": None,
        "analysed": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()

st.markdown(
    """
<div class="ps-header">
  <h1>🌐 PolicySim Diplomat<span class="ps-badge">BETA</span></h1>
  <p>AI Research Assistant for Model United Nations Conferences</p>
</div>
""",
    unsafe_allow_html=True,
)

_, status_col = st.columns([4, 1])
with status_col:
    css_class = "ps-status-mock" if USE_MOCK else "ps-status-ready"
    label = "⚡ DEMO MODE — No API Key" if USE_MOCK else "✓ AI ENGINE ACTIVE"
    st.markdown(f'<div class="{css_class}">{label}</div>', unsafe_allow_html=True)

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.markdown(
        '<div class="ps-input-panel"><div class="ps-panel-title">🎯 Delegation Brief</div>',
        unsafe_allow_html=True,
    )

    country = st.selectbox(
        "Representing Country",
        options=UN_MEMBER_STATES,
        index=UN_MEMBER_STATES.index("India"),
        help="Select the country you are representing.",
    )
    topic = st.text_input(
        "Agenda Topic",
        placeholder="e.g. Climate Finance for Developing Nations",
        help="Enter the exact topic or agenda item of your committee.",
    )
    committee = st.text_input(
        "Committee Name",
        placeholder="e.g. UNSC, UNGA, ECOSOC, HRC",
        value="UNGA",
        help="Specify which UN committee or body you are in.",
    )
    duration = st.slider(
        "Speech Duration (minutes)",
        min_value=1,
        max_value=5,
        value=2,
        step=1,
        help="Target length for your opening speech.",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    analyse_clicked = st.button(
        f"🚀  Analyse — {country}",
        type="primary",
        disabled=not topic.strip(),
        help="Enter a topic above to begin analysis.",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if not topic.strip():
        st.caption("↑ Enter an agenda topic to unlock analysis.")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("ℹ️ How to use"):
        st.markdown(
            """
1. **Select** your country from the dropdown
2. **Enter** the agenda topic exactly as stated in your committee
3. **Specify** your committee name
4. Hit **Analyse** — four tabs of intelligence are generated

**Tabs:**
- **Brief** — Official position & historical context
- **Arguments** — 4 structured debate arguments
- **Speech** — Full opening speech, podium-ready
- **Rebuttal** — Paste any opposing argument for a counter

*All outputs are designed for direct use at the MUN podium.*
            """
        )

with right_col:
    if analyse_clicked and topic.strip():
        with st.spinner("Consulting diplomatic sources..."):
            brief = generate_brief(country, topic, committee)
            st.session_state["brief"] = brief
            st.session_state["arguments"] = generate_arguments(country, topic, brief[:BRIEF_SUMMARY_LENGTH])
            st.session_state["speech"] = generate_speech(country, topic, committee, duration)
            st.session_state["analysed"] = True
            st.session_state["rebuttal"] = None

    tab_brief, tab_args, tab_speech, tab_rebuttal = st.tabs(
        [
            "📋  Country Brief",
            "⚔️  Arguments",
            "🎤  Opening Speech",
            "🔁  Rebuttal Builder",
        ]
    )

    with tab_brief:
        render_brief_tab(
            analysed=st.session_state["analysed"],
            brief=st.session_state["brief"] or "",
            country=country,
            topic=topic,
        )

    with tab_args:
        render_arguments_tab(
            analysed=st.session_state["analysed"],
            arguments=st.session_state["arguments"] or "",
            country=country,
        )

    with tab_speech:
        render_speech_tab(
            analysed=st.session_state["analysed"],
            speech=st.session_state["speech"] or "",
            country=country,
            committee=committee,
            duration=duration,
        )

    with tab_rebuttal:
        render_rebuttal_tab(
            analysed=st.session_state["analysed"],
            country=country,
            topic=topic,
            brief=st.session_state["brief"] or "",
            rebuttal=st.session_state["rebuttal"],
            generate_fn=lambda opp, pos: generate_rebuttal(country, topic, opp, pos),
        )

st.markdown(
    """
<div class="ps-footer">
  POLICYSIM DIPLOMAT &nbsp;·&nbsp; MUN AI RESEARCH ASSISTANT &nbsp;·&nbsp;
  BUILT FOR DELEGATES, BY DIPLOMATS
</div>
""",
    unsafe_allow_html=True,
)
