"""Admin: log in with password from secrets.toml (ADMIN_PASSWORD); upgrade requests, user plan, payment config, stats."""
import os
import streamlit as st
from services.auth import is_admin_logged_in, check_admin_password
from services.payments import get_payment_config
from db.queries import (
    list_upgrade_requests,
    update_upgrade_request,
    set_user_plan,
    ensure_user,
    set_payment_config_in_db,
)
from db.schema import get_conn


def run():
    st.title("🔐 Admin")

    # Admin login: password from secrets.toml
    try:
        admin_pass = st.secrets.get("ADMIN_PASSWORD", "")
    except Exception:
        admin_pass = ""

    if not is_admin_logged_in():
        st.markdown(
            """
            <div style="
                background: #1e293b; border-radius: 12px; padding: 1.5rem; margin: 0 0 1rem 0;
                border-left: 4px solid #06b6d4; box-shadow: 0 4px 14px rgba(0,0,0,0.25);
            ">
                <h2 style="color: #f1f5f9; margin: 0 0 0.5rem 0;">Log in to Admin</h2>
                <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">Password is set in .streamlit/secrets.toml (ADMIN_PASSWORD).</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("admin_login_form"):
            p = st.text_input("Admin password", type="password", key="admin_pw", placeholder="Enter password from secrets.toml")
            if st.form_submit_button("Login"):
                if check_admin_password(p, admin_pass):
                    st.session_state["admin_logged_in"] = True
                    st.success("Logged in.")
                    st.rerun()
                else:
                    st.error("Invalid password.")
        return

    if st.button("Logout (Admin)", key="admin_logout"):
        st.session_state["admin_logged_in"] = False
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["Upgrade requests", "Users", "Payment config", "Stats"])

    with tab1:
        status_filter = st.selectbox("Filter", ["pending", "approved", "rejected", "all"], key="admin_status")
        status = None if status_filter == "all" else status_filter
        requests = list_upgrade_requests(status=status)
        for req in requests:
            with st.expander(f"#{req['id']} — {req['email']} — {req['plan']} — {req['status']}"):
                st.write(f"**Method:** {req.get('method')} | **Ref:** {req.get('ref') or '—'} | **TS:** {req.get('ts')}")
                # Display uploaded receipt if path exists and file is present
                receipt_path = (req.get("receipt_path") or "").strip()
                if receipt_path and os.path.isfile(receipt_path):
                    st.subheader("Uploaded receipt")
                    try:
                        st.image(receipt_path, use_container_width=True)
                    except Exception:
                        st.caption(f"File: {receipt_path}")
                elif receipt_path:
                    st.caption(f"Receipt path (file not found): {receipt_path}")
                if req["status"] == "pending":
                    st.markdown("---")
                    approved_until = st.text_input("Premium until (YYYY-MM-DD)", key=f"until_{req['id']}", placeholder="e.g. 2025-12-31")
                    if st.button("Approve", key=f"approve_{req['id']}"):
                        ensure_user(req["email"])
                        update_upgrade_request(
                            req["id"],
                            status="approved",
                            approved_until=approved_until or None,
                        )
                        set_user_plan(req["email"], req["plan"], premium_until=approved_until or None)
                        st.success("Approved.")
                        st.rerun()
                    if st.button("Reject", key=f"reject_{req['id']}"):
                        update_upgrade_request(req["id"], status="rejected")
                        st.rerun()

    with tab2:
        st.subheader("Users")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT email, plan, premium_until, created_at FROM users ORDER BY created_at DESC LIMIT 50")
        rows = cur.fetchall()
        conn.close()
        for row in rows:
            st.write(f"**{row['email']}** — {row['plan']} — until {row['premium_until'] or '—'} — {row['created_at']}")
        st.markdown("---")
        st.subheader("Change user plan")
        with st.form("admin_change_plan"):
            change_email = st.text_input("User email", key="admin_change_email", placeholder="user@example.com")
            change_plan = st.selectbox("New plan", ["free", "premium", "pro"], key="admin_change_plan")
            change_until = st.text_input("Premium until (YYYY-MM-DD, leave empty for free)", key="admin_change_until", placeholder="e.g. 2025-12-31")
            if st.form_submit_button("Update plan"):
                if not change_email or not change_email.strip():
                    st.error("Enter user email.")
                else:
                    ensure_user(change_email.strip())
                    set_user_plan(
                        change_email.strip(),
                        change_plan,
                        premium_until=change_until.strip() or None,
                    )
                    st.success(f"Updated {change_email} to {change_plan}" + (f" until {change_until}" if change_until else "."))
                    st.rerun()

    with tab3:
        st.subheader("Payment configuration")
        st.caption("Configure GCash/Maya and plan pricing. These values appear on the Pricing page.")
        pay = get_payment_config()
        with st.form("admin_payment_config"):
            st.markdown("**GCash**")
            gcash_number = st.text_input("GCash number", value=pay.get("gcash_number") or "", key="admin_gcash_number", placeholder="09XX XXX XXXX")
            gcash_name = st.text_input("GCash name (display)", value=pay.get("gcash_name") or "", key="admin_gcash_name", placeholder="Your name")
            st.markdown("**Maya**")
            maya_number = st.text_input("Maya number", value=pay.get("maya_number") or "", key="admin_maya_number", placeholder="09XX XXX XXXX")
            maya_name = st.text_input("Maya name (display)", value=pay.get("maya_name") or "", key="admin_maya_name", placeholder="Your name")
            st.markdown("**Plans**")
            col1, col2 = st.columns(2)
            with col1:
                premium_price = st.number_input("Premium price (₱)", min_value=0, value=int(pay.get("premium_price_php") or 199), key="admin_premium_price")
                premium_billing = st.text_input("Premium billing label", value=pay.get("premium_billing") or "Month", key="admin_premium_billing", placeholder="Month")
            with col2:
                pro_price = st.number_input("Pro price (₱)", min_value=0, value=int(pay.get("pro_price_php") or 999), key="admin_pro_price")
                pro_billing = st.text_input("Pro billing label", value=pay.get("pro_billing") or "monthly", key="admin_pro_billing", placeholder="monthly")
            st.markdown("**Daily limits**")
            free_limit = st.number_input("Free checks per day", min_value=1, value=int(pay.get("free_daily_limit") or 2), key="admin_free_limit")
            premium_limit = st.number_input("Premium/Pro checks per day (unlimited = 9999)", min_value=1, value=int(pay.get("premium_daily_limit") or 9999), key="admin_premium_limit")
            if st.form_submit_button("Save payment config"):
                set_payment_config_in_db({
                    "gcash_number": (gcash_number or "").strip(),
                    "gcash_name": (gcash_name or "").strip(),
                    "maya_number": (maya_number or "").strip(),
                    "maya_name": (maya_name or "").strip(),
                    "premium_price_php": premium_price,
                    "premium_billing": (premium_billing or "Month").strip(),
                    "pro_price_php": pro_price,
                    "pro_billing": (pro_billing or "monthly").strip(),
                    "free_daily_limit": free_limit,
                    "premium_daily_limit": premium_limit,
                })
                st.success("Payment config saved. It will appear on the Pricing page.")
                st.rerun()

    with tab4:
        st.subheader("Stats")
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS n FROM scans")
        total_scans = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM users")
        total_users = cur.fetchone()["n"]
        conn.close()
        st.metric("Total scans", total_scans)
        st.metric("Total users", total_users)
