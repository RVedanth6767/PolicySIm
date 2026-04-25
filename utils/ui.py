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


def placeholder(label: str) -> None:
    st.markdown(
        f"""<div class="ps-placeholder">
            ◦ &nbsp; {label.upper()} WILL APPEAR HERE &nbsp; ◦<br>
            <span class="ps-placeholder-sub">
              Select a country and topic, then hit Analyse
            </span>
        </div>""",
        unsafe_allow_html=True,
    )


def render_brief_tab(analysed: bool, brief: str, country: str, topic: str) -> None:
    if not analysed:
        placeholder("country brief")
        return

    section_label(f"Diplomatic Intelligence Brief — {country} on {topic}")
    st.markdown(brief)
    copy_hint("Select all text to copy to clipboard")


def render_arguments_tab(analysed: bool, arguments: str, country: str) -> None:
    if not analysed:
        placeholder("debate arguments")
        return

    section_label(f"4 Structured Debate Arguments — {country}")
    st.markdown(arguments)
    copy_hint("Each argument is podium-ready")


def render_speech_tab(analysed: bool, speech: str, country: str, committee: str, duration: int) -> None:
    if not analysed:
        placeholder("opening speech")
        return

    word_count = len(speech.split())
    section_label(f"Opening Speech — {country} · {duration} min · {committee}")
    output_card(speech, extra_style="font-size:1.08rem;line-height:1.85;font-style:italic;")
    copy_hint(f"~{word_count} words — read aloud to check timing")


def render_rebuttal_tab(
    analysed: bool,
    country: str,
    topic: str,
    brief: str,
    rebuttal: str | None,
    generate_fn: Callable[[str, str], str],
) -> None:
    if not analysed:
        placeholder("rebuttal (run analysis first)")
        return

    section_label("Rebuttal Builder — Paste an opposing argument below")

    opposing = st.text_area(
        "Opposing argument",
        placeholder=(
            'e.g. "The delegate of China argues that developed nations '
            'must bear all financial burden for climate action..."'
        ),
        height=110,
        key="opposing_input",
        label_visibility="collapsed",
    )

    if st.button("⚡  Generate Rebuttal", key="rebuttal_btn", disabled=not opposing.strip()):
        own_pos = (brief or "")[:300]
        st.session_state["rebuttal"] = generate_fn(opposing, own_pos)

    if rebuttal:
        st.markdown("---")
        section_label(f"Prepared Rebuttal — {country}")
        st.markdown(rebuttal)
        copy_hint("Under 150 words — deliverable in 90 seconds")
    elif not opposing.strip():
        st.caption("Enter the opposing argument above and click Generate Rebuttal.")
