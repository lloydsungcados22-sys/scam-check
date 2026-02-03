"""Community Alerts (Trending Scams): enhanced background, readable theme cards, scam details."""
import html
import streamlit as st
from db.queries import get_trending_categories
from db.schema import get_conn
from components.theme import ALERT_RED, BG_CARD, RADIUS, TEXT_MUTED, TEXT_PRIMARY

# Readable text and enhanced Community Alerts background
CARD_TEXT = "#e2e8f0"
CARD_LABEL = "#f1f5f9"
PAGE_BG = "linear-gradient(180deg, #1e3a5f 0%, #0f172a 40%, #0c1222 100%)"
CARD_BG = "#334155"

# Short descriptions for common scam types (safe for display)
SCAM_DETAILS = {
    "gcash phishing": "Fake GCash links, OTP requests, or \"verify account\" messages. Never share OTP or click links from SMS.",
    "fake job offer": "Too-good job posts, upfront fees, or \"training\" payments. Real employers don’t ask for money.",
    "loan scam": "Instant loans with high fees, or \"processing\" charges before release. Use licensed lenders only.",
    "romance scam": "Fake relationships leading to money requests or \"emergency\" help. Be wary of strangers asking for cash.",
    "investment scam": "Guaranteed returns, crypto or \"exclusive\" deals. If it’s too good to be true, it usually is.",
    "sss/philhealth impersonation": "Fake SSS/PhilHealth links or \"benefits\" forms. Use only official sites and hotlines.",
    "bank otp scam": "Calls or SMS pretending to be your bank asking for OTP or card details. Banks never ask for OTP.",
    "maya phishing": "Fake Maya app links or \"verify\" messages. Don’t click links; open the app directly.",
    "unknown": "Other suspicious patterns. When in doubt, don’t click links or send money.",
}


def _esc(s):
    """Escape for HTML to prevent injection and stray tags."""
    if s is None:
        return ""
    return html.escape(str(s).strip())


def _row_cat(row):
    """Get category from row (dict or tuple from SQLite/Snowflake)."""
    if hasattr(row, "get"):
        return (row.get("category") or row.get("CATEGORY") or "")
    try:
        return (row[0] if len(row) > 0 else "")
    except (IndexError, TypeError):
        return ""


def _row_summary(row):
    if hasattr(row, "get"):
        return (row.get("summary") or row.get("SUMMARY") or "")
    try:
        return (row[1] if len(row) > 1 else "")
    except (IndexError, TypeError):
        return ""


def _row_ts(row):
    if hasattr(row, "get"):
        return (row.get("ts") or row.get("TS") or "")
    try:
        return (row[2] if len(row) > 2 else "")
    except (IndexError, TypeError):
        return ""


def run():
    st.markdown(
        f"""
        <div style="
            background: {PAGE_BG}; border-radius: 16px; padding: 1.5rem 1.5rem 1rem 1.5rem; margin: 0 0 1.5rem 0;
            border: 1px solid rgba(6, 182, 212, 0.25); box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        ">
            <h1 style="color: {CARD_LABEL}; margin: 0 0 0.25rem 0;">📢 Trending Scams</h1>
            <p style="color: {CARD_TEXT}; margin: 0; font-size: 0.95rem;">Trending scam categories and anonymized alerts. Stay informed.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        trending = get_trending_categories(10)
    except Exception:
        trending = [
            {"category": "GCash phishing", "count": 12},
            {"category": "Fake job offer", "count": 8},
            {"category": "Loan scam", "count": 6},
        ]

    st.subheader("Trending scams this week")
    for r in trending:
        cat = (r.get("category") or r.get("CATEGORY") or "Unknown").strip()
        count = r.get("count") or r.get("COUNT") or 0
        detail = SCAM_DETAILS.get(cat.lower(), SCAM_DETAILS.get("unknown", "Stay alert. Don’t share OTP or send money to strangers."))
        st.markdown(
            f"""
            <div style="
                background: {CARD_BG}; border-radius: {RADIUS}; padding: 0.85rem 1.25rem; margin: 0.4rem 0;
                border-left: 4px solid {ALERT_RED}; box-shadow: 0 2px 10px rgba(0,0,0,0.25);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                    <span style="color: {CARD_LABEL}; font-size: 1rem; font-weight: 500;">{_esc(cat)}</span>
                    <span style="color: {ALERT_RED}; font-weight: 700; font-size: 0.95rem;">{_esc(str(count))} reports</span>
                </div>
                <p style="color: {CARD_TEXT}; font-size: 0.85rem; margin: 0.4rem 0 0 0;">{_esc(detail)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.subheader("Recent alerts")
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT category, summary, ts FROM community_alerts ORDER BY ts DESC LIMIT 10")
        rows = cur.fetchall()
        conn.close()
        for row in rows:
            cat = _esc(_row_cat(row))
            summary = _esc(_row_summary(row))
            ts = _esc(str(_row_ts(row)))
            st.markdown(
                f"""
                <div style="
                    background: {CARD_BG}; border-radius: {RADIUS}; padding: 0.75rem 1rem; margin: 0.35rem 0;
                    color: {CARD_TEXT}; font-size: 0.95rem;
                ">
                    <strong style="color: {CARD_LABEL};">{cat}</strong> — {summary or "—"} <span style="color: {TEXT_MUTED}; font-size: 0.85rem;">{ts}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    except Exception:
        st.info("No alerts yet. Check back later.")
