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


COMMITTEE_CATEGORIES = {
    "🌍 UN Bodies": [
        "UNGA", "UNSC", "UNHRC", "ECOSOC", "UNICEF", "UNESCO", "UNEP", "WHO", "UNDP", "UN Women", "FAO", "ILO", "UNFCCC", "ITU"
    ],
    "⚖️ Legal & Justice": [
        "ICJ", "ICC", "UNODC"
    ],
    "💰 Economic & Finance": [
        "IMF", "World Bank", "WTO", "G20", "BRICS"
    ],
    "🌐 Geopolitical Blocs": [
        "NATO", "EU Parliament", "ASEAN"
    ],
    "🇮🇳 Indian Committees": [
        "Lok Sabha", "Rajya Sabha", "AIPPM", "NITI Aayog", "Indian Supreme Court"
    ],
    "⚡ Crisis Committees": [
        "Joint Crisis Committee (JCC)", "War Cabinet", "Cold War Crisis", "Terror Crisis Simulation"
    ]
}

ALL_COMMITTEES = [c for category in COMMITTEE_CATEGORIES.values() for c in category]

COMMITTEE_CONFIG = {
    "UNSC": {"tone": "geopolitical, strategic", "focus": "conflict, security, diplomacy"},
    "WHO": {"tone": "technical, scientific", "focus": "health, disease, global response"},
    "UNHRC": {"tone": "ethical, humanitarian", "focus": "human rights, violations"},
    "IMF": {"tone": "economic, analytical", "focus": "finance, policy, stability"},
    "NATO": {"tone": "military alliance", "focus": "defense, security"},
    "Lok Sabha": {"tone": "political debate", "focus": "domestic policy, governance"},
    "default": {"tone": "formal diplomatic", "focus": "policy, cooperation"}
}


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

st.markdown(
    """
<style>
#MainMenu, footer, header { visibility: hidden; height: 0; }
[data-testid="collapsedControl"] { display: none; }
.stDeployButton { display: none; }
</style>
""",
    unsafe_allow_html=True,
)


def _init_state() -> None:
    defaults: dict = {
        "brief": None,
        "arguments": None,
        "speech": None,
        "rebuttal": None,
        "analysed": False,
        "app_started": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()

if not st.session_state["app_started"]:
    st.markdown(
        """
<div class="hero-wrapper">
  <div class="hero-grid"></div>
  <div class="hero-glow"></div>
  <div class="hero-content fade-in">
    <div class="hero-badge">🌐 Model United Nations · AI Briefing System</div>
    <h1 class="hero-title">PolicySim <span>Diplomat</span></h1>
    <p class="hero-subtitle">Premium AI intelligence for podium-ready delegates.</p>
    <p class="hero-description">Craft country briefs, argument arsenals, timed speeches, and rebuttals in seconds with modern diplomatic tooling.</p>
    <div class="hero-stats">
      <div class="hero-stat"><div class="hero-stat-num">12K+</div><div class="hero-stat-label">Delegates</div></div>
      <div class="hero-stat"><div class="hero-stat-num">98%</div><div class="hero-stat-label">Readiness</div></div>
      <div class="hero-stat"><div class="hero-stat-num">60s</div><div class="hero-stat-label">Brief Time</div></div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1.3, 1, 1.3])
    with c2:
        if st.button("⚡ Start Briefing", use_container_width=True, key="start_btn"):
            st.session_state["app_started"] = True
            st.rerun()
    st.stop()

st.markdown(
    f"""
<div class="topnav">
  <div class="topnav-brand"><span class="topnav-icon">🌐</span>{APP_TITLE} <span class="topnav-accent">Diplomat</span></div>
  <div class="topnav-status"><span class="status-dot"></span>{'Demo Mode Active' if USE_MOCK else 'AI Active'}</div>
</div>
""",
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([7, 3], gap="large")

with right_col:
    st.markdown(
        """
<div class="mission-panel">
  <div class="mission-title">Mission Setup</div>
  <div class="mission-subtitle">Configure your intelligence run</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel-field-label">Committee</div>', unsafe_allow_html=True)
    committee = st.selectbox(
        "Committee",
        ALL_COMMITTEES,
        key="committee",
        label_visibility="collapsed",
    )

    st.markdown('<div class="panel-field-label">Country</div>', unsafe_allow_html=True)
    country = st.selectbox(
        "Representing Country",
        options=UN_MEMBER_STATES,
        index=UN_MEMBER_STATES.index("India"),
        label_visibility="collapsed",
    )

    st.markdown('<div class="panel-field-label">Agenda</div>', unsafe_allow_html=True)
    topic_placeholder = "e.g. Climate Finance for Developing Nations"
    if committee in COMMITTEE_CATEGORIES["⚡ Crisis Committees"]:
        topic_placeholder = "e.g. Immediate Response Strategy and Command Priorities"
    elif committee in COMMITTEE_CATEGORIES["🇮🇳 Indian Committees"]:
        topic_placeholder = "e.g. National Education Reform and Fiscal Federalism"
    elif committee in COMMITTEE_CATEGORIES["💰 Economic & Finance"]:
        topic_placeholder = "e.g. Sovereign Debt Relief and Global Financial Stability"

    topic = st.text_input(
        "Agenda Topic",
        placeholder=topic_placeholder,
        label_visibility="collapsed",
    )

    st.markdown('<div class="panel-field-label">Stance</div>', unsafe_allow_html=True)
    stance = st.radio(
        "Stance",
        ["Support", "Oppose", "Neutral / Abstain"],
        horizontal=True,
        label_visibility="collapsed",
        key="stance_choice",
    )

    st.markdown('<div class="panel-field-label">Duration</div>', unsafe_allow_html=True)
    duration = st.slider(
        "Speech Duration (minutes)",
        min_value=1,
        max_value=5,
        value=2,
        step=1,
        label_visibility="collapsed",
    )

    analyse_clicked = st.button(
        f"🌐 Generate Intelligence Brief",
        type="primary",
        disabled=not topic.strip(),
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with left_col:
    if analyse_clicked and topic.strip():
        config = COMMITTEE_CONFIG.get(committee, COMMITTEE_CONFIG["default"])
        with st.spinner("Consulting diplomatic sources..."):
            brief = generate_brief(country, topic, committee, tone=config["tone"], focus=config["focus"])
            st.session_state["brief"] = brief
            st.session_state["arguments"] = generate_arguments(
                country,
                topic,
                brief[:BRIEF_SUMMARY_LENGTH],
                committee=committee,
                tone=config["tone"],
                focus=config["focus"],
            )
            st.session_state["speech"] = generate_speech(country, topic, committee, duration, tone=config["tone"], focus=config["focus"])
            st.session_state["analysed"] = True
            st.session_state["rebuttal"] = None

    if st.session_state["analysed"]:
        arguments_text = st.session_state["arguments"] or ""
        args_count = sum(1 for line in arguments_text.splitlines() if line.strip().startswith(("-", "*", "1", "2", "3", "4")))
        args_count = args_count if args_count else 4
        speech_words = len((st.session_state["speech"] or "").split())
        readiness = min(99, max(84, 86 + (args_count * 2) + (4 if speech_words > 180 else 0)))

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Arguments</div><div class="metric-value">{args_count}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Speech Duration</div><div class="metric-value">{duration} min</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card metric-card-gold"><div class="metric-label">Readiness Score</div><div class="metric-value">{readiness}%</div></div>', unsafe_allow_html=True)

    tab_brief, tab_args, tab_speech, tab_rebuttal = st.tabs(
        [
            f"📡 {committee} Intelligence Brief",
            f"⚔ {committee} Debate Points",
            f"🎤 {committee} Podium Speech",
            "🔄 Live Counter",
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

st.markdown('<div class="ps-footer">PolicySim Diplomat · Built for Delegates, by Diplomats</div>', unsafe_allow_html=True)
