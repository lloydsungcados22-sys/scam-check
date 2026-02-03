"""Snowflake schema and connection. Credentials from .streamlit/secrets.toml [SNOWFLAKE]."""
import streamlit as st
from snowflake.connector import DictCursor


def _get_config():
    """Read Snowflake config from secrets. Returns dict or None if not configured."""
    try:
        cfg = st.secrets.get("SNOWFLAKE")
        if not cfg or not isinstance(cfg, dict):
            return None
        account = cfg.get("account") or cfg.get("ACCOUNT")
        user = cfg.get("user") or cfg.get("USER")
        password = cfg.get("password") or cfg.get("PASSWORD")
        warehouse = cfg.get("warehouse") or cfg.get("WAREHOUSE")
        database = cfg.get("database") or cfg.get("DATABASE")
        schema = cfg.get("schema") or cfg.get("SCHEMA")
        if account and user and password:
            return {
                "account": account,
                "user": user,
                "password": password,
                "warehouse": warehouse or "COMPUTE_WH",
                "database": database or "CHECKMOYAN",
                "schema": schema or "PUBLIC",
                "role": cfg.get("role") or cfg.get("ROLE"),
            }
    except Exception:
        pass
    return None


class _SnowflakeConnWrapper:
    """Wraps Snowflake connection so cursor() returns DictCursor (dict-like rows)."""
    def __init__(self, conn):
        self._conn = conn
    def cursor(self):
        return self._conn.cursor(DictCursor)
    def commit(self):
        return self._conn.commit()
    def close(self):
        return self._conn.close()


def get_conn():
    """Return a Snowflake connection (DictCursor). Raises if SNOWFLAKE not in secrets."""
    import snowflake.connector
    cfg = _get_config()
    if not cfg:
        raise RuntimeError("SNOWFLAKE not configured in secrets.toml")
    conn = snowflake.connector.connect(
        account=cfg["account"],
        user=cfg["user"],
        password=cfg["password"],
        warehouse=cfg["warehouse"],
        database=cfg["database"],
        schema=cfg["schema"],
        role=cfg.get("role"),
    )
    return _SnowflakeConnWrapper(conn)


def init_db():
    """Create CheckMoYan tables in Snowflake if they don't exist; seed dummy data once."""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR(255) PRIMARY KEY,
            plan VARCHAR(50) NOT NULL DEFAULT 'free',
            premium_until DATE,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            email VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            checks_count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (email, date)
        )
    """)

    cur.execute("CREATE SEQUENCE IF NOT EXISTS scans_seq START 1 INCREMENT 1")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER NOT NULL PRIMARY KEY DEFAULT scans_seq.NEXTVAL,
            email VARCHAR(255) NOT NULL,
            ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            verdict VARCHAR(50) NOT NULL,
            confidence INTEGER NOT NULL,
            category VARCHAR(255),
            signals_json VARCHAR(65535),
            msg_hash VARCHAR(255)
        )
    """)

    cur.execute("CREATE SEQUENCE IF NOT EXISTS upgrade_requests_seq START 1 INCREMENT 1")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS upgrade_requests (
            id INTEGER NOT NULL PRIMARY KEY DEFAULT upgrade_requests_seq.NEXTVAL,
            email VARCHAR(255) NOT NULL,
            plan VARCHAR(50) NOT NULL,
            method VARCHAR(50),
            ref VARCHAR(255),
            receipt_path VARCHAR(1024),
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            admin_notes VARCHAR(65535),
            approved_until DATE
        )
    """)

    cur.execute("CREATE SEQUENCE IF NOT EXISTS community_alerts_seq START 1 INCREMENT 1")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS community_alerts (
            id INTEGER NOT NULL PRIMARY KEY DEFAULT community_alerts_seq.NEXTVAL,
            category VARCHAR(255) NOT NULL,
            summary VARCHAR(65535),
            ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key VARCHAR(255) PRIMARY KEY,
            value VARCHAR(65535) NOT NULL DEFAULT ''
        )
    """)

    conn.commit()
    _seed_dummy_data(cur)
    conn.commit()
    cur.close()
    conn.close()


def _first_value(row):
    """Get first value from a DictCursor row (COUNT(*), NEXTVAL, etc.)."""
    if row is None:
        return None
    return next(iter(row.values()), None)


def _seed_dummy_data(cur):
    """Seed dummy scans and alerts for live stats and trending on first run."""
    cur.execute("SELECT COUNT(*) AS cnt FROM scans")
    if (_first_value(cur.fetchone()) or 0) > 0:
        return

    from datetime import datetime, timedelta
    today = (datetime.utcnow()).strftime("%Y-%m-%d")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    categories = [
        "GCash phishing", "Fake job offer", "Loan scam", "Romance scam",
        "Investment scam", "SSS/PhilHealth impersonation", "Bank OTP scam", "Maya phishing",
    ]
    verdicts = ["SCAM", "SCAM", "SCAM", "SUSPICIOUS", "SAFE"]

    for i in range(30):
        d = today if i % 3 else yesterday
        cur.execute(
            """INSERT INTO scans (email, ts, verdict, confidence, category, signals_json, msg_hash)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
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
            "INSERT INTO community_alerts (category, summary) VALUES (%s, %s)",
            (cat, f"Watch out for {cat} messages this week."),
        )
