"""CRUD for CheckMoYan when using Snowflake. Uses %s placeholders and Snowflake SQL."""
from datetime import datetime
from .snowflake_schema import get_conn


def _row_to_dict(row):
    """Convert Snowflake row (tuple or dict) to dict."""
    if row is None:
        return None
    if hasattr(row, "keys"):
        return dict(row)
    return None


def _val(row, *keys):
    """Get value from DictCursor row (Snowflake uses uppercase keys)."""
    if row is None:
        return None
    for k in keys:
        v = row.get(k) if hasattr(row, "get") else None
        if v is not None:
            return v
        uk = k.upper() if isinstance(k, str) else k
        v = row.get(uk) if hasattr(row, "get") else None
        if v is not None:
            return v
    return next(iter(row.values()), None) if row else None


def ensure_user(email: str) -> None:
    """Create user if not exists (plan=free)."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (email, plan) VALUES (%s, 'free')",
            (email.strip().lower(),),
        )
    except Exception:
        pass  # already exists
    conn.commit()
    cur.close()
    conn.close()


def get_user_plan(email: str) -> dict:
    """Return { plan, premium_until } for user."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT plan, premium_until FROM users WHERE email = %s",
        (email.strip().lower(),),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return {"plan": "free", "premium_until": None}
    plan = _val(row, "plan", "PLAN")
    premium_until = _val(row, "premium_until", "PREMIUM_UNTIL")
    return {"plan": plan or "free", "premium_until": str(premium_until) if premium_until else None}


def set_user_plan(email: str, plan: str, premium_until: str = None) -> None:
    """Set user plan and optional premium_until date (YYYY-MM-DD)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET plan = %s, premium_until = %s WHERE email = %s",
        (plan, premium_until, email.strip().lower()),
    )
    conn.commit()
    cur.close()
    conn.close()


def record_usage(email: str) -> None:
    """Increment today's check count for user."""
    ensure_user(email)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """MERGE INTO usage u
           USING (SELECT %s AS email, %s AS dt) s ON u.email = s.email AND u.date = s.dt
           WHEN MATCHED THEN UPDATE SET checks_count = u.checks_count + 1
           WHEN NOT MATCHED THEN INSERT (email, date, checks_count) VALUES (s.email, s.dt, 1)""",
        (email.strip().lower(), today),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_usage_today(email: str) -> int:
    """Return number of checks used today by user."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT checks_count FROM usage WHERE email = %s AND date = %s",
        (email.strip().lower(), today),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return _val(row, "checks_count", "CHECKS_COUNT") or 0


def insert_scan(
    email: str,
    verdict: str,
    confidence: int,
    category: str,
    signals_json: str,
    msg_hash: str,
) -> int:
    """Insert a scan record; return id."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT scans_seq.NEXTVAL AS n")
    sid = _val(cur.fetchone(), "n", "NEXTVAL")
    sid = int(sid) if sid is not None else None
    cur.execute(
        """INSERT INTO scans (id, email, verdict, confidence, category, signals_json, msg_hash)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (sid, email.strip().lower(), verdict, confidence, category or "", signals_json, msg_hash or ""),
    )
    conn.commit()
    cur.close()
    conn.close()
    return sid


def get_stats_today() -> dict:
    """Return { messages_analyzed, scams_detected, top_category } for today."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM scans WHERE DATE(ts) = %s", (today,))
    messages_analyzed = _val(cur.fetchone(), "c", "COUNT(*)") or 0
    cur.execute("SELECT COUNT(*) AS c FROM scans WHERE DATE(ts) = %s AND verdict = 'SCAM'", (today,))
    scams_detected = _val(cur.fetchone(), "c", "COUNT(*)") or 0
    cur.execute(
        """SELECT category, COUNT(*) AS c FROM scans
           WHERE DATE(ts) = %s AND TRIM(COALESCE(category,'')) != ''
           GROUP BY category ORDER BY c DESC LIMIT 1""",
        (today,),
    )
    row = cur.fetchone()
    top_category = _val(row, "category", "CATEGORY") or "GCash phishing"
    cur.close()
    conn.close()
    return {
        "messages_analyzed": messages_analyzed,
        "scams_detected": scams_detected,
        "top_category": top_category,
    }


def get_trending_categories(limit: int = 5) -> list:
    """Return list of { category, count } for recent scans (last 7 days)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT category, COUNT(*) AS count FROM scans
           WHERE DATE(ts) >= DATEADD(day, -7, CURRENT_DATE()) AND TRIM(COALESCE(category,'')) != ''
           GROUP BY category ORDER BY count DESC LIMIT %s""",
        (limit,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"category": _val(r, "category", "CATEGORY"), "count": _val(r, "count", "COUNT") or 0} for r in rows]


def insert_upgrade_request(
    email: str,
    plan: str,
    method: str,
    ref: str = None,
    receipt_path: str = None,
) -> int:
    """Insert upgrade request; return id."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT upgrade_requests_seq.NEXTVAL AS n")
    uid = _val(cur.fetchone(), "n", "NEXTVAL")
    uid = int(uid) if uid is not None else None
    cur.execute(
        """INSERT INTO upgrade_requests (id, email, plan, method, ref, receipt_path, status)
           VALUES (%s, %s, %s, %s, %s, %s, 'pending')""",
        (uid, email.strip().lower(), plan, method, ref or "", receipt_path or ""),
    )
    conn.commit()
    cur.close()
    conn.close()
    return uid


def list_upgrade_requests(status: str = None) -> list:
    """List upgrade requests, optionally filter by status."""
    conn = get_conn()
    cur = conn.cursor()
    if status:
        cur.execute(
            "SELECT * FROM upgrade_requests WHERE status = %s ORDER BY ts DESC",
            (status,),
        )
    else:
        cur.execute("SELECT * FROM upgrade_requests ORDER BY ts DESC")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def get_upgrade_request(req_id: int) -> dict:
    """Get single upgrade request by id."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM upgrade_requests WHERE id = %s", (req_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def update_upgrade_request(
    req_id: int,
    status: str,
    admin_notes: str = None,
    approved_until: str = None,
) -> None:
    """Update upgrade request status and optional notes/expiry."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """UPDATE upgrade_requests SET status = %s, admin_notes = %s, approved_until = %s
           WHERE id = %s""",
        (status, admin_notes or "", approved_until or "", req_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_app_setting(key: str) -> str:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM app_settings WHERE key = %s", (key,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return ""
    v = _val(row, "value", "VALUE")
    return str(v) if v is not None else ""


def set_app_setting(key: str, value: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE app_settings SET value = %s WHERE key = %s", (value, key))
    if cur.rowcount == 0:
        cur.execute("INSERT INTO app_settings (key, value) VALUES (%s, %s)", (key, value))
    conn.commit()
    cur.close()
    conn.close()
