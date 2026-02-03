"""CRUD for CheckMoYan when using SQLite (no SNOWFLAKE in secrets)."""
from ._sqlite_schema import get_conn
from datetime import datetime


def ensure_user(email: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (email, plan) VALUES (?, 'free')",
        (email.strip().lower(),),
    )
    conn.commit()
    conn.close()


def get_user_plan(email: str) -> dict:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT plan, premium_until FROM users WHERE email = ?",
        (email.strip().lower(),),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"plan": "free", "premium_until": None}
    return {"plan": row["plan"], "premium_until": row["premium_until"]}


def set_user_plan(email: str, plan: str, premium_until: str = None) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET plan = ?, premium_until = ? WHERE email = ?",
        (plan, premium_until, email.strip().lower()),
    )
    conn.commit()
    conn.close()


def record_usage(email: str) -> None:
    ensure_user(email)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO usage (email, date, checks_count) VALUES (?, ?, 1)
           ON CONFLICT(email, date) DO UPDATE SET checks_count = checks_count + 1""",
        (email.strip().lower(), today),
    )
    conn.commit()
    conn.close()


def get_usage_today(email: str) -> int:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT checks_count FROM usage WHERE email = ? AND date = ?",
        (email.strip().lower(), today),
    )
    row = cur.fetchone()
    conn.close()
    return row["checks_count"] if row else 0


def insert_scan(
    email: str,
    verdict: str,
    confidence: int,
    category: str,
    signals_json: str,
    msg_hash: str,
) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO scans (email, verdict, confidence, category, signals_json, msg_hash)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (email.strip().lower(), verdict, confidence, category or "", signals_json, msg_hash or ""),
    )
    sid = cur.lastrowid
    conn.commit()
    conn.close()
    return sid


def get_stats_today() -> dict:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM scans WHERE date(ts) = ?", (today,))
    messages_analyzed = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM scans WHERE date(ts) = ? AND verdict = 'SCAM'", (today,))
    scams_detected = cur.fetchone()["n"]
    cur.execute(
        """SELECT category, COUNT(*) AS c FROM scans WHERE date(ts) = ? AND category != ''
           GROUP BY category ORDER BY c DESC LIMIT 1""",
        (today,),
    )
    row = cur.fetchone()
    top_category = row["category"] if row else "GCash phishing"
    conn.close()
    return {
        "messages_analyzed": messages_analyzed,
        "scams_detected": scams_detected,
        "top_category": top_category,
    }


def get_trending_categories(limit: int = 5) -> list:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT category, COUNT(*) AS count FROM scans
           WHERE date(ts) >= date('now', '-7 days') AND category != ''
           GROUP BY category ORDER BY count DESC LIMIT ?""",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [{"category": r["category"], "count": r["count"]} for r in rows]


def insert_upgrade_request(
    email: str,
    plan: str,
    method: str,
    ref: str = None,
    receipt_path: str = None,
) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO upgrade_requests (email, plan, method, ref, receipt_path, status)
           VALUES (?, ?, ?, ?, ?, 'pending')""",
        (email.strip().lower(), plan, method, ref or "", receipt_path or ""),
    )
    uid = cur.lastrowid
    conn.commit()
    conn.close()
    return uid


def list_upgrade_requests(status: str = None) -> list:
    conn = get_conn()
    cur = conn.cursor()
    if status:
        cur.execute(
            "SELECT * FROM upgrade_requests WHERE status = ? ORDER BY ts DESC",
            (status,),
        )
    else:
        cur.execute("SELECT * FROM upgrade_requests ORDER BY ts DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_upgrade_request(req_id: int) -> dict:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM upgrade_requests WHERE id = ?", (req_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_upgrade_request(
    req_id: int,
    status: str,
    admin_notes: str = None,
    approved_until: str = None,
) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """UPDATE upgrade_requests SET status = ?, admin_notes = ?, approved_until = ?
           WHERE id = ?""",
        (status, admin_notes or "", approved_until or "", req_id),
    )
    conn.commit()
    conn.close()


def get_app_setting(key: str) -> str:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return (row["value"] if row else "") or ""


def set_app_setting(key: str, value: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    conn.commit()
    conn.close()
