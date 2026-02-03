"""Top navigation: pill/card buttons, session_state-based routing. No sidebar."""
import streamlit as st

PAGE_HOME = "Home"
PAGE_SCAM_CHECKER = "Scam Checker"
PAGE_COMMUNITY = "Community Alerts"
PAGE_PRICING = "Pricing"
PAGE_LOGIN = "Login"
PAGE_ADMIN = "Admin"

NAV_ITEMS = [
    ("Home", PAGE_HOME, "🏠"),
    ("Check a Message", PAGE_SCAM_CHECKER, "🛡️"),
    ("Trending Scams", PAGE_COMMUNITY, "📢"),
    ("Pricing", PAGE_PRICING, "💰"),
    ("Login", PAGE_LOGIN, "🔑"),
]


def get_current_page() -> str:
    """Return current page from session_state; default Home."""
    return st.session_state.get("page", PAGE_HOME)


def set_page(page: str) -> None:
    """Set current page and rerun."""
    st.session_state["page"] = page
    st.rerun()


def render_nav(show_admin: bool = False):
    """Render top nav as pill-style buttons. Admin only if show_admin."""
    current = get_current_page()
    items = list(NAV_ITEMS)
    if show_admin:
        items.append(("Admin", PAGE_ADMIN, "🔐"))

    # Pill row: one column per item (wraps on mobile)
    n = len(items)
    cols = st.columns(n)
    for i, (label, page_id, icon) in enumerate(items):
        with cols[i]:
            is_active = current == page_id
            if st.button(
                f"{icon} {label}",
                key=f"nav_{page_id}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                set_page(page_id)


def render_nav_cards(show_admin: bool = False):
    """Card-style nav grid (mobile-friendly): one button per card."""
    current = get_current_page()
    items = list(NAV_ITEMS)
    if show_admin:
        items.append(("Admin", PAGE_ADMIN, "🔐"))

    n = len(items)
    cols = st.columns(min(n, 4))
    for i, (label, page_id, icon) in enumerate(items):
        with cols[i % len(cols)]:
            is_active = current == page_id
            if st.button(
                f"{icon}  {label}",
                key=f"navcard_{page_id}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                set_page(page_id)
