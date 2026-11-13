"""
utils/database.py
------------------
SQLite persistence layer for InsightIQ user accounts. Handles
connection management, schema creation, and simple CRUD helpers used
by utils/auth.py. Kept separate from auth.py so the storage layer
could be swapped later (e.g. Postgres) without touching auth logic.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent / "insightiq.db"


def get_connection() -> sqlite3.Connection:
    """Open a new connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the users table if it doesn't already exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                name           TEXT NOT NULL,
                email          TEXT NOT NULL UNIQUE,
                password_hash  TEXT NOT NULL,
                business_name  TEXT,
                created_at     TEXT NOT NULL
            )
            """
        )
        conn.commit()


def email_exists(email: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        return row is not None


def create_user(name: str, email: str, password_hash: str, business_name: str) -> None:
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (name, email, password_hash, business_name, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name.strip(), email.strip().lower(), password_hash, business_name.strip(), created_at),
        )
        conn.commit()


def get_user_by_email(email: str):
    """Return a dict for the matching user, or None."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None
