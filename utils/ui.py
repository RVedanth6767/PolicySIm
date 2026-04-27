"""utils/ui.py — Reusable Streamlit rendering helpers."""

from typing import Callable

import streamlit as st


def section_label(text: str) -> None:
    st.markdown(f'<div class="ps-section-label">{text}</div>', unsafe_allow_html=True)


def output_card(content: str, extra_style: str = "") -> None:
    style_attr = f' style="{extra_style}"' if extra_style else ""
    st.markdown(f'<div class="ps-output-card"{style_attr}>{content}</div>', unsafe_allow_html=True)


def copy_hint(text: str) -> None:
    st.markdown(f'<div class="ps-copy-hint">{text}</div>', unsafe_allow_html=True)


def placeholder(label: str, icon: str, description: str, tags: list[str]) -> None:
    tag_html = "".join([f'<span class="tag">{t}</span>' for t in tags])
    st.markdown(
        f"""
<div class="empty-state">
  <div class="empty-state-icon">{icon}</div>
  <div class="empty-state-title">{label}</div>
  <div class="empty-state-desc">{description}</div>
  <div class="empty-state-tags">{tag_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_brief_tab(analysed: bool, brief: str, country: str, topic: str) -> None:
    if not analysed:
        placeholder(
            label="Intelligence Brief",
            icon="📡",
            description="Generate a complete geopolitical assessment with policy leverage points and coalition signals.",
            tags=["Alliance Matrix", "Voting History", "Position Analysis"],
        )
        return

    section_label(f"Diplomatic Intelligence Brief — {country} on {topic}")
    output_card(brief)
    copy_hint("Select all text to copy to clipboard")


def render_arguments_tab(analysed: bool, arguments: str, country: str) -> None:
    if not analysed:
        placeholder(
            label="Debate Points",
            icon="⚔",
            description="Receive numbered, high-impact interventions with legal framing and precedence support.",
            tags=["UN Charter", "Resolution Citations", "Legal Framing"],
        )
        return

    section_label(f"Debate Arsenal — {country}")
    points = [line.strip(" -•") for line in arguments.splitlines() if line.strip()]
    for idx, point in enumerate(points, 1):
        st.markdown(
            f'<div class="argument-card"><div class="argument-num">{idx:02d}</div><div class="argument-text">{point}</div></div>',
            unsafe_allow_html=True,
        )
    copy_hint("Each argument is podium-ready")


def render_speech_tab(analysed: bool, speech: str, country: str, committee: str, duration: int) -> None:
    if not analysed:
        placeholder(
            label="Podium Speech",
            icon="🎤",
            description="Draft a fluent opening speech calibrated to your committee protocol and speaking window.",
            tags=["Timed Delivery", "Protocol-ready", "Delegation Voice"],
        )
        return

    word_count = len(speech.split())
    section_label(f"Opening Speech — {country} · {duration} min · {committee}")
    output_card(speech.replace("\n", "<br>"), extra_style="font-size:1.04rem;line-height:1.9;")
    copy_hint(f"~{word_count} words — read aloud to check pacing")
    st.download_button(
        "⬇ Download Speech",
        data=speech,
        file_name=f"speech_{country.replace(' ', '_')}.txt",
        mime="text/plain",
    )


def render_rebuttal_tab(
    analysed: bool,
    country: str,
    topic: str,
    brief: str,
    rebuttal: str | None,
    generate_fn: Callable[[str, str], str],
) -> None:
    if not analysed:
        placeholder(
            label="Live Counter",
            icon="🔄",
            description="Build concise counterarguments in real-time as opposing delegations take the floor.",
            tags=["Fast Response", "Counter Framing", "Floor-ready"],
        )
        return

    section_label("Counterargument Builder")
    opposing = st.text_area(
        "Opposing argument",
        placeholder=(
            'e.g. "The delegate argues that developed states should carry all financial obligations for climate adaptation..."'
        ),
        height=130,
        key="opposing_input",
        label_visibility="collapsed",
    )

    if st.button("⚡ Generate Counter", key="rebuttal_btn", disabled=not opposing.strip(), use_container_width=True):
        own_pos = (brief or "")[:300]
        st.session_state["rebuttal"] = generate_fn(opposing, own_pos)

    if rebuttal:
        st.markdown('<div class="pace-bar-label">Response Readiness</div>', unsafe_allow_html=True)
        st.progress(88)
        output_card(rebuttal)
        copy_hint(f"Prepared rebuttal for {country} on {topic}")
    elif not opposing.strip():
        st.caption("Enter the opposing argument above and click Generate Counter.")
