"""Minimal auth: email session for Free mode, admin password for Admin."""
import re
import streamlit as st

EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_RE.match(email.strip()))


def get_email_from_session() -> str:
    """Return current user email from session_state, or empty string."""
    return (st.session_state.get("user_email") or "").strip().lower()


def set_email_session(email: str) -> None:
    """Set user email in session_state (validated)."""
    if validate_email(email):
        st.session_state["user_email"] = email.strip().lower()
    else:
        st.session_state["user_email"] = ""


def is_admin_logged_in() -> bool:
    return bool(st.session_state.get("admin_logged_in"))


def check_admin_password(password: str, secrets_password: str) -> bool:
    if not secrets_password or not password:
        return False
    return password.strip() == secrets_password.strip()


def require_admin(secrets_password: str) -> bool:
    """If not logged in, show login form and return False. If logged in, return True."""
    if is_admin_logged_in():
        return True
    pw = st.secrets.get("ADMIN_PASSWORD") or secrets_password
    with st.form("admin_login"):
        p = st.text_input("Admin password", type="password")
        if st.form_submit_button("Login"):
            if check_admin_password(p, pw):
                st.session_state["admin_logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid password.")
    return False
