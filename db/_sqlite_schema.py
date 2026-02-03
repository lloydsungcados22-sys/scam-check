"""SQLite schema and initialization (used when SNOWFLAKE is not in secrets)."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "checkmoyan.db"


def get_conn():
    """Return a connection to the SQLite DB."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist and seed dummy stats for first run."""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            plan TEXT NOT NULL DEFAULT 'free',
            premium_until TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            email TEXT NOT NULL,
            date TEXT NOT NULL,
            checks_count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (email, date),
            FOREIGN KEY (email) REFERENCES users(email)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            ts TEXT NOT NULL DEFAULT (datetime('now')),
            verdict TEXT NOT NULL,
            confidence INTEGER NOT NULL,
            category TEXT,
            signals_json TEXT,
            msg_hash TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS upgrade_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            plan TEXT NOT NULL,
            method TEXT,
            ref TEXT,
            receipt_path TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            ts TEXT NOT NULL DEFAULT (datetime('now')),
            admin_notes TEXT,
            approved_until TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS community_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            summary TEXT,
            ts TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT ''
        )
    """)

    conn.commit()
    _seed_dummy_data(conn, cur)
    conn.commit()
    conn.close()


def _seed_dummy_data(conn, cur):
    """Seed dummy scans and alerts for live stats and trending categories on first run."""
    cur.execute("SELECT COUNT(*) FROM scans")
    if cur.fetchone()[0] > 0:
        return

    from datetime import datetime, timedelta
    today = datetime.utcnow().strftime("%Y-%m-%d")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    categories = [
        "GCash phishing",
        "Fake job offer",
        "Loan scam",
        "Romance scam",
        "Investment scam",
        "SSS/PhilHealth impersonation",
        "Bank OTP scam",
        "Maya phishing",
    ]
    verdicts = ["SCAM", "SCAM", "SCAM", "SUSPICIOUS", "SAFE"]

    for i in range(30):
        d = today if i % 3 else yesterday
        cur.execute(
            """INSERT INTO scans (email, ts, verdict, confidence, category, signals_json, msg_hash)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                "demo@checkmoyan.ph",
                f"{d} 12:00:00",
                verdicts[i % len(verdicts)],
                60 + (i % 40),
                categories[i % len(categories)],
                "[]",
                f"hash_{i}",
            ),
        )

    for cat in categories[:5]:
        cur.execute(
            "INSERT INTO community_alerts (category, summary) VALUES (?, ?)",
            (cat, f"Watch out for {cat} messages this week."),
        )
