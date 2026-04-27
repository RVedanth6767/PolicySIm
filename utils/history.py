"""Speech history persistence helpers."""

from __future__ import annotations

from db.database import get_connection


def save_speech(
    user_id: int,
    country: str,
    topic: str,
    committee: str,
    speech: str,
    evaluation: str | None = None,
) -> None:
    """Save a generated speech for a user."""
    if not user_id or not (country and topic and committee and speech):
        return

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO history (user_id, country, topic, committee, speech, evaluation)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                country.strip(),
                topic.strip(),
                committee.strip(),
                speech.strip(),
                (evaluation or "").strip() or None,
            ),
        )
        conn.commit()


def get_user_history(user_id: int):
    """Return most recent speeches for a user."""
    if not user_id:
        return []

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, country, topic, committee, speech, evaluation, created_at
            FROM history
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()
    return rows
