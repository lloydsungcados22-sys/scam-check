"""Pricing & Upgrade: plan cards (theme), GCash/Maya instructions, receipt/ref submission."""
import streamlit as st
from services.payments import get_payment_config, get_plans_config
from services.auth import get_email_from_session, validate_email
from db.queries import insert_upgrade_request, ensure_user
from components.theme import ALERT_RED, BG_CARD, RADIUS, TEXT_MUTED, TEXT_PRIMARY


def _render_payment_section(pay, show_full_numbers: bool):
    """Render payment instructions and upgrade form. show_full_numbers=True shows GCash/Maya numbers from secrets."""
    gcash_number = pay.get("gcash_number") or "—"
    maya_number = pay.get("maya_number") or "—"
    gcash_name = pay.get("gcash_name") or "—"
    maya_name = pay.get("maya_name") or "—"
    if show_full_numbers:
        st.subheader("💳 Payment details — GCash or Maya")
        st.caption("Send payment using the details below, then submit your receipt or reference number.")
        st.markdown(
            f"""
            <div style="background: {BG_CARD}; border-radius: 12px; padding: 1.25rem; margin: 0.5rem 0; border-left: 4px solid {ALERT_RED};">
                <p style="color: #e2e8f0; margin: 0 0 0.5rem 0;"><strong>GCash:</strong> Send to <strong>{gcash_number}</strong> ({gcash_name})</p>
                <p style="color: #e2e8f0; margin: 0;"><strong>Maya:</strong> Send to <strong>{maya_number}</strong> ({maya_name})</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.subheader("How to pay (GCash or Maya)")
        st.caption("Click an upgrade button above to see payment numbers and submit your receipt.")
        st.markdown(
            f"""
            <div style="background: {BG_CARD}; border-radius: 12px; padding: 1.25rem; margin: 0.5rem 0; border-left: 4px solid {ALERT_RED};">
                <p style="color: #e2e8f0; margin: 0 0 0.5rem 0;"><strong>GCash:</strong> ({gcash_name})</p>
                <p style="color: #e2e8f0; margin: 0;"><strong>Maya:</strong> ({maya_name})</p>
            </div>
            <p style="color: {TEXT_MUTED}; font-size: 0.9rem;">Click <strong>Upgrade via GCash / Maya</strong> above to see the full payment number and submit your receipt.</p>
            """,
            unsafe_allow_html=True,
        )
    st.subheader("Submit payment (receipt / reference)")
    email = get_email_from_session()
    if not email:
        email = st.text_input("Your email", placeholder="you@example.com", key="pricing_email")
        if not validate_email(email) and email:
            st.error("Enter a valid email.")
    else:
        st.info(f"Logged in as **{email}**")
    upgrade_plan = st.session_state.get("upgrade_plan")
    plan_options = ["premium", "pro"]
    default_idx = plan_options.index(upgrade_plan) if upgrade_plan in plan_options else 0
    plan = st.selectbox("Plan", plan_options, index=default_idx, key="pricing_plan")
    method = st.radio("Payment method", ["GCash", "Maya"], key="pricing_method")
    ref = st.text_input("Reference number (from GCash/Maya)", placeholder="e.g. 1234567890", key="pricing_ref")
    receipt_file = st.file_uploader("Or upload receipt screenshot (optional)", type=["png", "jpg", "jpeg"], key="pricing_receipt")
    if st.button("Submit upgrade request", key="pricing_submit"):
        if not email or not validate_email(email):
            st.error("Please enter a valid email.")
        else:
            ensure_user(email)
            receipt_path = ""
            if receipt_file:
                import os
                os.makedirs("receipts", exist_ok=True)
                path = os.path.join("receipts", f"{email.replace('@', '_')}_{plan}_{receipt_file.name}")
                with open(path, "wb") as f:
                    f.write(receipt_file.getvalue())
                receipt_path = path
            rid = insert_upgrade_request(
                email=email.strip().lower(),
                plan=plan,
                method=method,
                ref=ref or "",
                receipt_path=receipt_path,
            )
            st.success(f"Request #{rid} submitted. We'll verify and activate your plan soon.")


def run():
    st.title("💰 Pricing & Upgrade")
    pay = get_payment_config()
    plans = get_plans_config()
    upgrade_plan = st.session_state.get("upgrade_plan")
    show_payment = st.session_state.get("show_payment_section", False)
    go_to_payment = bool(upgrade_plan or show_payment)

    for p in plans:
        with st.container():
            st.markdown(
                f"""
                <div style="
                    border-radius: {RADIUS}; padding: 1.25rem; margin: 0.5rem 0;
                    background: {BG_CARD}; border-left: 4px solid {ALERT_RED};
                    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
                ">
                    <h3 style="color: {ALERT_RED};">{p['name']}</h3>
                    <p style="font-size: 1.5rem; color: {TEXT_PRIMARY};">₱{p['price_php']} <small style="color: {TEXT_MUTED};">/{p['billing']}</small></p>
                    <ul style="color: {TEXT_MUTED}; padding-left: 1.25rem;">
                        {"".join(f"<li>{f}</li>" for f in p['features'])}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if p["key"] != "free":
                if st.button(f"Upgrade via GCash / Maya — {p['name']}", key=f"upgrade_{p['key']}"):
                    st.session_state["upgrade_plan"] = p["key"]
                    st.session_state["show_payment_section"] = True
                    st.rerun()

    st.markdown("---")
    _render_payment_section(pay, show_full_numbers=go_to_payment)
