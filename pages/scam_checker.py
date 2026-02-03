"""Scam Checker: paste message, channel/language, full AI analysis, explainable verdict, share."""
import streamlit as st
import json
from services.auth import get_email_from_session, set_email_session, validate_email
from services.usage import can_user_check, get_daily_limit, get_usage_today, record_check
from services.analysis import analyze_message
from components.verdict import verdict_card, share_snippet
from components.ui import primary_cta, toast_success, toast_error
from components.theme import ALERT_RED, BG_CARD, BORDER_ACCENT, RADIUS, TEXT_MUTED, TEXT_PRIMARY
from db.queries import ensure_user


def run():
    # Pre-fill from landing "Try this message" demo
    if "demo_message" in st.session_state:
        st.session_state["scam_message"] = st.session_state.pop("demo_message", "")

    st.title("🛡️ CheckMoYan — Scam Checker")
    st.caption("Paste a suspicious message. Full AI analysis with an explainable verdict: reasons, red flags, and what to do next.")

    # Email (minimal auth for free mode)
    email = get_email_from_session()
    if not email:
        with st.expander("Enter your email (for free daily checks)", expanded=True):
            e = st.text_input("Email", placeholder="you@example.com", key="scam_email")
            if st.button("Continue", key="scam_email_btn"):
                if validate_email(e):
                    set_email_session(e)
                    ensure_user(e)
                    st.rerun()
                else:
                    st.error("Please enter a valid email.")
        # Allow anonymous check with lower limit
        email = "anonymous"

    if email and email != "anonymous":
        limit = get_daily_limit(email)
        used = get_usage_today(email)
        st.caption(f"Checks today: {used} / {limit}")

    # Inputs (value can be pre-filled from landing demo via session_state["scam_message"])
    message = st.text_area(
        "Paste the suspicious message",
        placeholder="Paste SMS, Messenger, or email text here...",
        height=140,
        key="scam_message",
    )
    col1, col2 = st.columns(2)
    with col1:
        channel = st.selectbox(
            "Channel (optional)",
            ["", "SMS", "Messenger", "Email", "Call Script"],
            key="scam_channel",
        )
    with col2:
        language = st.selectbox(
            "Language (optional)",
            ["", "English", "Tagalog", "Mixed"],
            key="scam_language",
        )

    allow_learning = st.checkbox(
        "Allow anonymized learning to improve community alerts (default: off)",
        value=False,
        key="scam_learning",
    )

    if primary_cta("CheckMoYan", key="scam_analyze"):
        if not message or not message.strip():
            toast_error("Please paste a message to check.")
        else:
            can_do, err = can_user_check(email)
            if not can_do:
                toast_error(err)
            else:
                try:
                    api_key = (st.secrets.get("OPENAI_API_KEY") or "").strip()
                except Exception:
                    api_key = ""
                if not api_key:
                    toast_error("OpenAI API key not configured. Add OPENAI_API_KEY to .streamlit/secrets.toml.")
                else:
                    with st.spinner("Analyzing with AI (OpenAI)..."):
                        result = analyze_message(
                            message.strip(),
                            channel=channel or "",
                            language=language or "",
                            api_key=api_key,
                        )
                    record_check(
                        email=email,
                        verdict=result.get("verdict", "SUSPICIOUS"),
                        confidence=result.get("confidence", 0),
                        category=result.get("category", ""),
                        signals_json=json.dumps(result.get("reasons", [])[:3]),
                        msg_hash=result.get("msg_hash", ""),
                    )
                    st.session_state["last_result"] = result
                    st.session_state["last_message"] = message.strip()
                    # New key so share section (message + verdict) updates when CheckMoYan is clicked again
                    st.session_state["last_result_key"] = hash((message.strip(), result.get("verdict", ""), result.get("msg_hash", "")))
                    st.rerun()

    if st.session_state.get("last_result"):
        st.markdown("---")
        st.markdown(
            '<span style="background: #1e293b; color: #22c55e; padding: 0.25rem 0.6rem; border-radius: 8px; font-size: 0.85rem;">✓ Explainable verdict (AI from secrets)</span>',
            unsafe_allow_html=True,
        )
        st.subheader("Verdict")
        # Use saved message so share section has message + verdict even if user clears the box
        last_message = st.session_state.get("last_message") or st.session_state.get("scam_message") or ""
        result_key = st.session_state.get("last_result_key", 0)
        verdict_card(st.session_state["last_result"], message=last_message, result_key=result_key)

    st.markdown("---")
    st.caption("We do not store your full message. Only verdict and category are saved. AI can be wrong — verify with official channels (GCash, Maya, banks, SSS, PhilHealth).")
