import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("MEMORY_DB", "memory.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row      # rows behave like dicts
    return conn


def init_memory():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                action TEXT NOT NULL,
                target TEXT,
                result_count INTEGER,
                details TEXT
            )
            """
        )


def log_run(action, target=None, result_count=None, details=None):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO analysis_runs (ts, action, target, result_count, details) "
            "VALUES (?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), action, target, result_count, details),
        )


def get_history(limit=50):
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM analysis_runs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]