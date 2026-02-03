"""
CheckMoYan — Is this a scam? Paste it. We'll explain it.
Main entry: session_state-based routing, no sidebar. Top nav only.
"""
import streamlit as st
from db.schema import init_db
from services.auth import get_email_from_session, is_admin_logged_in
from components.nav import (
    get_current_page,
    set_page,
    render_nav,
    PAGE_HOME,
    PAGE_SCAM_CHECKER,
    PAGE_COMMUNITY,
    PAGE_PRICING,
    PAGE_LOGIN,
    PAGE_ADMIN,
)

# Initialize DB on startup
init_db()

st.set_page_config(
    page_title="CheckMoYan — Scam Checker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Global theme: high-impact scam-checker style (bold contrast, alert accents, mobile-first)
from components.theme import inject_theme
inject_theme()

# Initialize page from redirect (e.g. landing CTAs)
if "nav_redirect" in st.session_state:
    target = st.session_state.nav_redirect
    st.session_state["page"] = target
    del st.session_state["nav_redirect"]
    st.rerun()

# Ensure page is set
if "page" not in st.session_state:
    st.session_state["page"] = PAGE_HOME

# Top navigation (no sidebar) — Admin always visible so users can open "Log in to Admin"
render_nav(show_admin=True)
st.markdown("---")

# Route to page content
page = get_current_page()

if page == PAGE_HOME:
    from pages.landing import run
    run()
elif page == PAGE_SCAM_CHECKER:
    from pages.scam_checker import run
    run()
elif page == PAGE_PRICING:
    from pages.pricing import run
    run()
elif page == PAGE_COMMUNITY:
    from pages.community import run
    run()
elif page == PAGE_LOGIN:
    from pages.login import run
    run()
elif page == PAGE_ADMIN:
    from pages.admin import run
    run()
else:
    from pages.landing import run
    run()
