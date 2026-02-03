"""Verdict card and shareable snippet — high-impact scam-checker theme."""
import html
import re
import streamlit as st
import streamlit.components.v1 as components
from components.theme import ALERT_RED, ALERT_AMBER, SAFE_GREEN, BG_CARD, TEXT_PRIMARY, TEXT_MUTED, RADIUS


def _verdict_color(verdict: str) -> str:
    if verdict == "SAFE":
        return SAFE_GREEN
    if verdict == "SCAM":
        return ALERT_RED
    return ALERT_AMBER  # SUSPICIOUS


def _strip_html(s: str) -> str:
    """Remove HTML tags so AI-returned HTML is shown as plain text."""
    if not s or not isinstance(s, str):
        return ""
    t = str(s)
    # Remove tags (repeat for nested tags)
    for _ in range(5):
        t = re.sub(r"<[^>]*>", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _escape(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def _build_full_share_text(result: dict, message: str = "") -> str:
    """Build complete shareable text: message + verdict + reasons + actions + notes (all plain text, no HTML)."""
    verdict = (result.get("verdict") or "SUSPICIOUS").upper()
    confidence = result.get("confidence", 0)
    category = _strip_html(str(result.get("category") or "Unknown"))
    reasons = result.get("reasons") or []
    actions = result.get("recommended_actions") or []
    warning_message = _strip_html((result.get("warning_message") or "").strip())
    red_flags = result.get("red_flags") or []
    safety_notes = _strip_html((result.get("safety_notes") or "").strip())

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "🛡️ CheckMoYan — Scam Check Result",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"VERDICT: {verdict} ({confidence}%)",
        f"Category: {category}",
        "",
    ]
    if (message or "").strip():
        lines.append("MESSAGE CHECKED:")
        lines.append((message or "").strip()[:2000])
        lines.append("")
    lines.append("Why it looks like this:")
    for r in reasons[:8]:
        lines.append("  • " + _strip_html(str(r)))
    lines.append("")
    lines.append("What to do next:")
    for i, a in enumerate(actions[:6], 1):
        lines.append(f"  {i}. " + _strip_html(str(a)))
    if red_flags:
        lines.append("")
        lines.append("Red flags: " + ", ".join(_strip_html(str(f)) for f in red_flags[:5]))
    if safety_notes:
        lines.append("")
        lines.append("Note: " + safety_notes)
    if warning_message:
        lines.append("")
        lines.append("⚠️ " + warning_message)
    lines.append("")
    lines.append("— Check if it's a scam: CheckMoYan")
    return "\n".join(lines)


def verdict_card(result: dict, message: str = ""):
    """Render big verdict card: label, confidence, category, reasons, actions, red flags, copy/share section."""
    verdict = (result.get("verdict") or "SUSPICIOUS").upper()
    confidence = result.get("confidence", 0)
    category = _strip_html(str(result.get("category") or "Unknown"))
    reasons = result.get("reasons") or []
    recommended_actions = result.get("recommended_actions") or []
    warning_message = result.get("warning_message") or ""
    red_flags = result.get("red_flags") or []
    safety_notes = _strip_html((result.get("safety_notes") or "").strip())
    color = _verdict_color(verdict)

    reasons_esc = "".join(f"<li>{_escape(_strip_html(str(r)))}</li>" for r in reasons[:8])
    actions_esc = "".join(f"<li>{_escape(_strip_html(str(a)))}</li>" for a in recommended_actions[:6])
    red_flags_esc = ", ".join(_escape(_strip_html(str(f))) for f in red_flags[:5]) if red_flags else ""
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

    # Share section: full message + verdict (always show when we have a result)
    full_text = _build_full_share_text(result, message)
    st.subheader("Copy or share this result")
    st.caption("Message + verdict. Select the text and press Ctrl+C (Cmd+C) to copy, or use Download.")
    st.text_area(
        "Full result (message + verdict)",
        value=full_text,
        height=220,
        key="share_snippet_area",
        label_visibility="collapsed",
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            label="Download (message + verdict)",
            data=full_text,
            file_name="checkmoyan_verdict.txt",
            mime="text/plain",
            key="download_verdict_btn",
        )
    with col2:
        # One-click copy via browser clipboard (text in hidden textarea to avoid quote/HTML issues)
        text_escaped = html.escape(full_text)
        copy_html = f"""
        <textarea id="sharecopy" style="display:none; width:100%; height:0;" readonly>{text_escaped}</textarea>
        <button id="copybtn" style="
            padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600;
            background: #ef4444; color: white; border: none; cursor: pointer;
        " onclick="
            var el = document.getElementById('sharecopy');
            var text = el.value;
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(function() {{
                    var b = document.getElementById('copybtn');
                    b.textContent = 'Copied!';
                    b.style.background = '#10b981';
                    setTimeout(function() {{ b.textContent = 'Copy to clipboard'; b.style.background = '#ef4444'; }}, 2000);
                }}).catch(function() {{ el.select(); document.execCommand('copy'); }});
            }} else {{
                el.select();
                document.execCommand('copy');
            }}
        ">Copy to clipboard</button>
        """
        components.html(copy_html, height=44)

    return None


def share_snippet(verdict: str, confidence: int, category: str, warning_message: str) -> str:
    """Generate short shareable text for friends."""
    w = _strip_html((warning_message or "").strip())
    return f"⚠️ CheckMoYan verdict: {verdict} ({confidence}%) — {category}\n\n{w}\n\n— Check if it's a scam: CheckMoYan"
