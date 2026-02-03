"""Verdict card and shareable snippet — high-impact scam-checker theme."""
import streamlit as st
from components.theme import ALERT_RED, ALERT_AMBER, SAFE_GREEN, BG_CARD, TEXT_PRIMARY, TEXT_MUTED, RADIUS


def _verdict_color(verdict: str) -> str:
    if verdict == "SAFE":
        return SAFE_GREEN
    if verdict == "SCAM":
        return ALERT_RED
    return ALERT_AMBER  # SUSPICIOUS


def _escape(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def verdict_card(result: dict):
    """Render big verdict card: label, confidence, category, reasons, actions, red flags, copy warning."""
    verdict = (result.get("verdict") or "SUSPICIOUS").upper()
    confidence = result.get("confidence", 0)
    category = result.get("category") or "Unknown"
    reasons = result.get("reasons") or []
    recommended_actions = result.get("recommended_actions") or []
    warning_message = result.get("warning_message") or ""
    red_flags = result.get("red_flags") or []
    safety_notes = (result.get("safety_notes") or "").strip()
    color = _verdict_color(verdict)

    reasons_esc = "".join(f"<li>{_escape(r)}</li>" for r in reasons[:8])
    actions_esc = "".join(f"<li>{_escape(a)}</li>" for a in recommended_actions[:6])
    red_flags_esc = ", ".join(_escape(f) for f in red_flags[:5]) if red_flags else ""
    list_color = "#e2e8f0"

    st.markdown(
        f"""
        <div style="
            border-radius: 16px; padding: 1.5rem; margin: 1rem 0;
            background: {BG_CARD}; border: 2px solid {color};
            box-shadow: 0 8px 24px rgba(0,0,0,0.35);
        ">
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <span style="font-size: 1.5rem; font-weight: bold; color: {color}; padding: 0.25rem 0.75rem; border-radius: 8px; background: rgba(255,255,255,0.06);">{verdict}</span>
                <span style="color: {list_color};">Confidence: <strong style="color: {TEXT_PRIMARY};">{confidence}%</strong></span>
                <span style="color: {list_color};">Category: <strong style="color: {ALERT_AMBER};">{_escape(category)}</strong></span>
            </div>
            <hr style="border-color: rgba(255,255,255,0.1); margin: 1rem 0;" />
            <h4 style="color: {TEXT_PRIMARY}; margin: 0 0 0.5rem 0;">Why it looks like this</h4>
            <ul style="color: {list_color}; margin: 0 0 1rem 0; padding-left: 1.25rem; line-height: 1.5;">{reasons_esc}</ul>
            <h4 style="color: {TEXT_PRIMARY}; margin: 0 0 0.5rem 0;">What to do next</h4>
            <ol style="color: {list_color}; margin: 0 0 1rem 0; padding-left: 1.25rem; line-height: 1.5;">{actions_esc}</ol>
            {"<p style=\"color: " + ALERT_AMBER + "; font-size: 0.9rem;\">🚩 Red flags: " + red_flags_esc + "</p>" if red_flags else ""}
            {"<p style=\"color: " + list_color + "; font-size: 0.9rem; margin-top: 0.5rem;\">" + _escape(safety_notes) + "</p>" if safety_notes else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Copy warning message button
    if warning_message:
        snippet = share_snippet(verdict, confidence, category, warning_message)
        st.text_area("Copy warning message to share", value=snippet, height=100, key="share_snippet_area")
        if st.button("Copy to clipboard", key="copy_warning"):
            st.session_state["clipboard_copy"] = snippet
            st.success("Copied! Paste in Messenger or SMS to warn others.")

    return None


def share_snippet(verdict: str, confidence: int, category: str, warning_message: str) -> str:
    """Generate short shareable text for friends."""
    return f"⚠️ CheckMoYan verdict: {verdict} ({confidence}%) — {category}\n\n{warning_message}\n\n— Check if it's a scam: CheckMoYan"
