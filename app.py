"""app.py — PolicySim Diplomat: AI Research Assistant for MUN Conferences."""

import os
import sys
import re

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from config import APP_TITLE, APP_ICON, USE_MOCK, BRIEF_SUMMARY_LENGTH
from db.database import init_db
from utils.auth import login_user, register_user
from utils.countries import UN_MEMBER_STATES
from utils.history import get_user_history, save_speech
from modules.evaluator import generate_evaluation
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
from utils.ai_client import run_module


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


def _render_auth() -> None:
    left_spacer, center_col, right_spacer = st.columns([1.2, 1.6, 1.2])
    with center_col:
        st.markdown(
            """
<div class="auth-shell fade-in">
  <div class="auth-card">
    <div class="auth-title-wrap">
      <div class="auth-eyebrow">🔐 Secure Access</div>
      <h1 class="auth-title">Welcome to PolicySim Diplomat</h1>
      <p class="auth-subtitle">Sign in or create your account to enter your premium MUN intelligence workspace.</p>
    </div>
</div>
</div>
""",
            unsafe_allow_html=True,
        )
        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            with st.form("login_form", clear_on_submit=False):
                login_username = st.text_input("Username", key="login_username")
                login_password = st.text_input("Password", type="password", key="login_password")
                login_submit = st.form_submit_button("Login", use_container_width=True)

            if login_submit:
                user_id = login_user(login_username, login_password)
                if user_id:
                    st.session_state["user_id"] = user_id
                    st.session_state["username"] = login_username.strip()
                    st.session_state["auth_toast"] = "Login successful. Loading your dashboard..."
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with register_tab:
            with st.form("register_form", clear_on_submit=True):
                reg_username = st.text_input("Choose Username", key="reg_username")
                reg_password = st.text_input("Choose Password", type="password", key="reg_password")
                register_submit = st.form_submit_button("Register", use_container_width=True)

            if register_submit:
                if register_user(reg_username, reg_password):
                    st.toast("Registration successful. You can now log in.", icon="✅")
                    st.success("Registration successful. You can now log in.")
                else:
                    st.error("Registration failed. Use a unique username and non-empty credentials.")


_load_css()
init_db()

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
        "evaluation": None,
        "analysed": False,
        "app_started": False,
        "user_id": None,
        "username": None,
        "auth_toast": None,
        "simulation_active": False,
        "crisis_history": [],
        "current_crisis": "",
        "user_responses": [],
        "ai_feedback": [],
        "round_number": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _generate_crisis_prompt(committee: str, agenda: str, country: str) -> str:
    return (
        f"Generate a realistic UN-style geopolitical crisis scenario for {committee}, "
        f"involving {agenda}, affecting {country}. Keep it concise and urgent."
    )


def _generate_next_crisis_prompt(last_crisis: str, country: str) -> str:
    return (
        f"Based on previous crisis: {last_crisis},\n"
        f"generate an escalation or new development affecting {country}."
    )


def _build_crisis_evaluation_prompt(country: str, user_input: str, current_crisis: str) -> str:
    return f"""Evaluate the following diplomatic response from {country} in a UN committee.
Provide:
- Strengths
- Weaknesses
- Strategic improvement
- Realism score out of 10

Response: {user_input}
Crisis: {current_crisis}
"""


def _extract_section(text: str, section_name: str, stop_sections: list[str]) -> str:
    section_pattern = rf"\*\*{section_name}\*\*|{section_name}:?"
    start_match = re.search(section_pattern, text, flags=re.IGNORECASE)
    if not start_match:
        return ""
    start = start_match.end()
    end = len(text)
    for stop in stop_sections:
        stop_match = re.search(rf"\*\*{stop}\*\*|{stop}:?", text[start:], flags=re.IGNORECASE)
        if stop_match:
            end = min(end, start + stop_match.start())
    return text[start:end].strip(" \n:-")


def _parse_crisis_feedback(feedback_text: str) -> dict:
    strengths = _extract_section(
        feedback_text,
        "Strengths",
        ["Weaknesses", "Strategic improvement", "Realism score"],
    )
    weaknesses = _extract_section(
        feedback_text,
        "Weaknesses",
        ["Strategic improvement", "Realism score"],
    )
    suggestions = _extract_section(
        feedback_text,
        "Strategic improvement",
        ["Realism score"],
    )
    score_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:/|out of)\s*10", feedback_text, flags=re.IGNORECASE)
    score = score_match.group(1) if score_match else "N/A"
    return {
        "strengths": strengths or "No strengths extracted.",
        "weaknesses": weaknesses or "No weaknesses extracted.",
        "suggestions": suggestions or "No strategic improvement extracted.",
        "score": score,
        "raw": feedback_text.strip(),
    }


_init_state()

if st.session_state.get("auth_toast"):
    st.toast(st.session_state["auth_toast"], icon="✅")
    st.session_state["auth_toast"] = None

if not st.session_state["user_id"]:
    _render_auth()
    st.stop()

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
  <div class="topnav-status"><span class="status-dot"></span>{'Demo Mode Active' if USE_MOCK else 'AI Active'} · Logged in as {st.session_state['username']}</div>
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
            speech_text = generate_speech(country, topic, committee, duration, tone=config["tone"], focus=config["focus"])
            st.session_state["speech"] = speech_text
            evaluation = generate_evaluation(country, topic, speech_text)
            st.session_state["evaluation"] = evaluation
            save_speech(st.session_state["user_id"], country, topic, committee, speech_text, evaluation)
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

    tab_brief, tab_args, tab_speech, tab_rebuttal, tab_crisis, tab_history = st.tabs(
        [
            f"📡 {committee} Intelligence Brief",
            f"⚔ {committee} Debate Points",
            f"🎤 {committee} Podium Speech",
            "🔄 Live Counter",
            "Crisis Simulation",
            "📜 History",
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

        if "evaluation" in st.session_state and st.session_state["evaluation"]:
            st.markdown(
                """
    <div class="eval-card">
        <div class="eval-title">🎯 AI Speech Evaluation</div>
    </div>
    """,
                unsafe_allow_html=True,
            )
            st.markdown(st.session_state["evaluation"])

    with tab_rebuttal:
        render_rebuttal_tab(
            analysed=st.session_state["analysed"],
            country=country,
            topic=topic,
            brief=st.session_state["brief"] or "",
            rebuttal=st.session_state["rebuttal"],
            generate_fn=lambda opp, pos: generate_rebuttal(country, topic, opp, pos),
        )

    with tab_crisis:
        st.markdown("## 🌍 Crisis Simulation Mode")
        st.caption("Respond to evolving geopolitical crises in real-time.")
        st.markdown(f"**Current Round:** {st.session_state.get('round_number', 0)}")

        control_col1, control_col2 = st.columns(2)
        with control_col1:
            start_simulation_clicked = st.button("Start Simulation", use_container_width=True)
        with control_col2:
            next_crisis_clicked = st.button(
                "Next Crisis",
                use_container_width=True,
                disabled=not st.session_state.get("simulation_active", False),
            )

        if start_simulation_clicked:
            if not topic.strip():
                st.error("Please enter an agenda to start Crisis Simulation.")
            else:
                st.session_state["simulation_active"] = True
                st.session_state["round_number"] = 1
                st.session_state["crisis_history"] = []
                st.session_state["user_responses"] = []
                st.session_state["ai_feedback"] = []
                with st.spinner("Simulating geopolitical developments..."):
                    first_crisis = run_module(
                        prompt=_generate_crisis_prompt(committee, topic, country),
                        system="You are a UN crisis director simulating real-time geopolitical developments.",
                        mock_fn=lambda: (
                            f"Urgent briefing: A rapidly escalating regional dispute tied to {topic} "
                            f"has triggered cross-border instability and emergency deliberations in {committee}, "
                            f"with immediate implications for {country}."
                        ),
                        label="Crisis Simulation",
                    )
                st.session_state["current_crisis"] = first_crisis
                st.session_state["crisis_history"].append(first_crisis)

        if next_crisis_clicked and st.session_state.get("simulation_active", False):
            last_crisis = st.session_state.get("current_crisis", "")
            if last_crisis:
                st.session_state["round_number"] = st.session_state.get("round_number", 0) + 1
                with st.spinner("Simulating geopolitical developments..."):
                    next_crisis = run_module(
                        prompt=_generate_next_crisis_prompt(last_crisis, country),
                        system="You are a UN crisis director escalating scenarios in realistic, concise updates.",
                        mock_fn=lambda: (
                            f"Escalation update: Following prior developments, regional actors have intensified "
                            f"their posture, increasing humanitarian and diplomatic pressure on {country}."
                        ),
                        label="Crisis Escalation",
                    )
                st.session_state["current_crisis"] = next_crisis
                st.session_state["crisis_history"].append(next_crisis)

        response_input = st.text_input("Your Response", key="crisis_user_response")
        submit_response_clicked = st.button(
            "Submit Response",
            use_container_width=True,
            disabled=not st.session_state.get("simulation_active", False),
        )

        if submit_response_clicked:
            if not response_input.strip():
                st.error("Please enter a diplomatic response before submitting.")
            elif not st.session_state.get("current_crisis"):
                st.error("No active crisis found. Start the simulation first.")
            else:
                st.session_state["user_responses"].append(response_input.strip())
                with st.spinner("Simulating geopolitical developments..."):
                    feedback_text = run_module(
                        prompt=_build_crisis_evaluation_prompt(
                            country=country,
                            user_input=response_input.strip(),
                            current_crisis=st.session_state["current_crisis"],
                        ),
                        system=(
                            "You are an experienced MUN crisis committee chair. Return concise and practical feedback "
                            "with clear sections for Strengths, Weaknesses, Strategic improvement, and Realism score out of 10."
                        ),
                        mock_fn=lambda: """Strengths:
- Balanced diplomatic tone
- Actionable immediate proposal

Weaknesses:
- Limited coalition-building detail
- Missing enforcement mechanism

Strategic improvement:
- Add named bilateral and multilateral follow-up steps with timelines.

Realism score out of 10: 8/10""",
                        label="Crisis Feedback",
                    )
                parsed_feedback = _parse_crisis_feedback(feedback_text)
                st.session_state["ai_feedback"].append(parsed_feedback)
                st.session_state["crisis_user_response"] = ""

        if st.session_state.get("current_crisis"):
            st.markdown("### 🚨 Crisis Update:")
            st.write(st.session_state["current_crisis"])

        if st.session_state["ai_feedback"]:
            latest_feedback = st.session_state["ai_feedback"][-1]
            st.success(f"**Strengths:**\n{latest_feedback['strengths']}")
            st.warning(f"**Weaknesses:**\n{latest_feedback['weaknesses']}")
            st.info(f"**Suggestions:**\n{latest_feedback['suggestions']}")
            st.metric("Realism Score", f"{latest_feedback['score']}/10")

        if st.session_state["crisis_history"]:
            st.markdown("---")
            for idx, crisis_text in enumerate(st.session_state["crisis_history"], start=1):
                st.markdown(f"#### Round {idx}: Crisis Update")
                with st.chat_message("assistant"):
                    st.markdown(f"🚨 {crisis_text}")
                    if idx - 1 < len(st.session_state["ai_feedback"]):
                        feedback = st.session_state["ai_feedback"][idx - 1]
                        st.markdown(
                            f"**Strengths:** {feedback['strengths']}\n\n"
                            f"**Weaknesses:** {feedback['weaknesses']}\n\n"
                            f"**Strategic Improvement:** {feedback['suggestions']}\n\n"
                            f"**Realism Score:** {feedback['score']}/10"
                        )
                if idx - 1 < len(st.session_state["user_responses"]):
                    with st.chat_message("user"):
                        st.markdown(st.session_state["user_responses"][idx - 1])
                st.divider()

    with tab_history:
        st.markdown("### Your Speech Archive")
        history_rows = get_user_history(st.session_state["user_id"])
        if not history_rows:
            st.info("No speeches saved yet. Generate your first intelligence brief to start building history.")
        else:
            for row in history_rows:
                header = f"{row['country']} · {row['committee']} · {row['created_at']}"
                with st.expander(header):
                    st.markdown(f"**Topic:** {row['topic']}")
                    st.markdown(f"**Committee:** {row['committee']}")
                    st.markdown(f"**Country:** {row['country']}")
                    st.markdown(f"**Generated:** {row['created_at']}")
                    st.markdown("---")
                    st.markdown(row["speech"])
                    if row["evaluation"]:
                        st.markdown("### 🎯 AI Speech Evaluation")
                        st.markdown(row["evaluation"])

st.markdown('<div class="ps-footer">PolicySim Diplomat · Built for Delegates, by Diplomats</div>', unsafe_allow_html=True)
