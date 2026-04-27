"""Authentication helpers for PolicySim users."""

from __future__ import annotations

import hashlib
import sqlite3

from db.database import get_connection


def hash_password(password: str) -> str:
    """Hash a plaintext password using SHA256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username: str, password: str) -> bool:
    """Register a user. Returns True if successful, False if username exists/invalid."""
    username = (username or "").strip()
    password = password or ""
    if not username or not password:
        return False

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hash_password(password)),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def login_user(username: str, password: str) -> int | None:
    """Return user id if credentials are valid, otherwise None."""
    username = (username or "").strip()
    password = password or ""
    if not username or not password:
        return None

    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, hash_password(password)),
        ).fetchone()

    return int(row["id"]) if row else None
