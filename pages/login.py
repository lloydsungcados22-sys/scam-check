"""Login for Premium and Pro users: enter email to access your plan and unlimited checks."""
import streamlit as st
from services.auth import get_email_from_session, set_email_session, validate_email
from db.queries import get_user_plan, ensure_user
from components.nav import set_page, PAGE_SCAM_CHECKER, PAGE_PRICING
from components.theme import BG_CARD, RADIUS, SAFE_GREEN, TEXT_MUTED, TEXT_PRIMARY


def run():
    st.title("🔑 Login — Premium & Pro")
    st.caption("Enter the email linked to your Premium or Pro account to access unlimited checks.")

    email = get_email_from_session()
    if email:
        plan_info = get_user_plan(email)
        plan = (plan_info.get("plan") or "free").lower()
        premium_until = plan_info.get("premium_until")
        st.info(f"**Logged in as** {email} — **Plan:** {plan.title()}" + (f" (until {premium_until})" if premium_until else ""))
        if plan in ("premium", "pro"):
            st.success("You have unlimited checks. Use **Check a Message** to analyze messages.")
            if st.button("Go to Scam Checker", type="primary", key="login_go_check"):
                set_page(PAGE_SCAM_CHECKER)
        else:
            st.caption("Upgrade to Premium or Pro for unlimited checks.")
            if st.button("See Pricing / Upgrade", key="login_go_pricing"):
                set_page(PAGE_PRICING)
        if st.button("Use a different email", key="login_switch_email"):
            st.session_state["user_email"] = ""
            st.rerun()
        return

    with st.form("login_form"):
        e = st.text_input("Email", placeholder="you@example.com", key="login_email")
        if st.form_submit_button("Login"):
            if not e or not validate_email(e):
                st.error("Please enter a valid email.")
            else:
                ensure_user(e.strip().lower())
                set_email_session(e.strip().lower())
                st.rerun()

    st.markdown("---")
    st.markdown(
        f"""
        <div style="background: {BG_CARD}; border-radius: {RADIUS}; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid {SAFE_GREEN};">
            <p style="color: {TEXT_MUTED}; margin: 0; font-size: 0.9rem;">
                <strong style="color: {SAFE_GREEN};">Premium & Pro users:</strong> Use the same email you used when upgrading. 
                Your plan is linked to that email. Don’t have an account? Use <strong>Check a Message</strong> with any email for free (limited checks), or <strong>Pricing</strong> to upgrade.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
