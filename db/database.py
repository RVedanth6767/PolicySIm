"""SQLite database setup and connection helpers for PolicySim."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "policysim.db"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with Row objects enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize required tables for auth and user speech history."""
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                country TEXT NOT NULL,
                topic TEXT NOT NULL,
                committee TEXT NOT NULL,
                speech TEXT NOT NULL,
                evaluation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        columns = {row["name"] for row in conn.execute("PRAGMA table_info(history)").fetchall()}
        if "evaluation" not in columns:
            conn.execute("ALTER TABLE history ADD COLUMN evaluation TEXT")

        conn.commit()
