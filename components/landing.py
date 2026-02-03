"""Landing page sections: scam-checker theme, hero, stats, sample demos, how-it-works, trending, trust."""
import streamlit as st
from db.queries import get_stats_today, get_trending_categories
from components.nav import set_page, PAGE_SCAM_CHECKER, PAGE_PRICING, PAGE_COMMUNITY
from components.theme import ALERT_RED, ALERT_AMBER, SAFE_GREEN, ACCENT_CYAN, BG_CARD, BORDER_ACCENT, BORDER_TECH, RADIUS, TEXT_MUTED, TEXT_PRIMARY

# Realistic PH scam sample messages (clickable "Try this message" demos)
SAMPLE_SCAM_MESSAGES = [
    {
        "label": "GCash / e-wallet phishing",
        "icon": "📱",
        "text": "GCash: Your account will be suspended in 24hrs. Verify now: bit.ly/gcash-verify-now to avoid lockout. Do not share this code with anyone. OTP: 123456",
    },
    {
        "label": "Fake job offer",
        "icon": "💼",
        "text": "Hi! We're hiring for Work From Home Data Encoder. Earn 25k-40k/week. No experience needed. Pay 500 pesos registration fee to get started. Reply YES to receive link.",
    },
    {
        "label": "Loan scam",
        "icon": "💰",
        "text": "CONGRATULATIONS! You are approved for 50,000 pesos loan. No collateral. Send 1,500 processing fee to GCash 09XX XXX XXXX to release funds today. Limited slots!",
    },
    {
        "label": "Romance / investment scam",
        "icon": "❤️",
        "text": "I'm Mark from UK, we met on FB. I have a crypto trading platform that doubles money in 2 weeks. I already made 2M. Join me, minimum 10k pesos. I will help you.",
    },
    {
        "label": "SSS / gov't impersonation",
        "icon": "🏛️",
        "text": "SSS: You have unclaimed benefits worth 15,000 pesos. Claim before Dec 31. Click here to verify your membership: sss-claim.ph. Enter your SSS number and OTP sent to your phone.",
    },
]


def hero_section():
    """High-impact hero: headline, subheadline, security/warning vibe."""
    st.markdown(
        f"""
        <div style="
            text-align: center; padding: 2rem 0 1.5rem 0;
            background: linear-gradient(135deg, rgba(239,68,68,0.1) 0%, rgba(6,182,212,0.06) 50%, transparent 100%);
            border-radius: 16px; border: 1px solid {BORDER_ACCENT}; border-top: 2px solid {ACCENT_CYAN};
            margin-bottom: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 24px rgba(6,182,212,0.08);
        ">
            <div style="display: inline-block; background: linear-gradient(90deg, {ALERT_RED}, #c026d3); color: white; padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.8rem; margin-bottom: 0.75rem; font-weight: 600;">⚠️ SCAM CHECKER</div>
            <h1 style="font-size: clamp(1.75rem, 5vw, 2.75rem); margin: 0; color: {TEXT_PRIMARY}; font-weight: 700;">
                CheckMoYan — Is this a scam?
            </h1>
            <p style="font-size: 1.15rem; color: {TEXT_MUTED}; margin: 0.75rem auto 0; max-width: 520px;">
                Paste any message. Get an AI verdict with clear reasons and what to do next.
            </p>
            <div style="margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center;">
                <span style="background: {BG_CARD}; color: {ACCENT_CYAN}; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.85rem; border: 1px solid {BORDER_TECH};">🛡️ AI-Powered</span>
                <span style="background: {BG_CARD}; color: {ALERT_AMBER}; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.85rem;">🇵🇭 Philippines</span>
                <span style="background: {BG_CARD}; color: {SAFE_GREEN}; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.85rem;">🔒 Privacy-First</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def cta_section():
    """Primary + secondary CTAs above the fold."""
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🛡️ Check a Message Now", type="primary", key="landing_cta_check", use_container_width=True):
            set_page(PAGE_SCAM_CHECKER)
    with col2:
        if st.button("💰 See Pricing / Upgrade", type="primary", key="landing_cta_pricing", use_container_width=True):
            set_page(PAGE_PRICING)
    with col3:
        if st.button("📢 Trending Scams", key="landing_cta_trending", use_container_width=True):
            set_page(PAGE_COMMUNITY)
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)


def sample_scams_section():
    """Clickable 'Try this message' demo cards — realistic PH scam samples."""
    st.markdown(
        f"""
        <div style="margin: 1.5rem 0;">
            <h3 style="color: {TEXT_PRIMARY}; margin-bottom: 0.5rem;">⚠️ Try a sample message</h3>
            <p style="color: {TEXT_MUTED}; font-size: 0.9rem; margin-bottom: 1rem;">Click to open the Scam Checker with this message pre-filled. See how AI explains the verdict.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for i, sample in enumerate(SAMPLE_SCAM_MESSAGES):
        snippet = (sample["text"][:120] + "...").replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background: {BG_CARD}; border-radius: {RADIUS}; padding: 1rem; margin: 0.5rem 0;
                    border-left: 4px solid {ALERT_RED}; box-shadow: 0 4px 14px rgba(0,0,0,0.2);
                ">
                    <div style="color: {ALERT_RED}; font-weight: 600; font-size: 0.9rem;">{sample['icon']} {sample['label']}</div>
                    <p style="color: {TEXT_MUTED}; font-size: 0.85rem; margin: 0.5rem 0 0 0; line-height: 1.4;">{snippet}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Try this message", key=f"demo_{i}", type="primary", use_container_width=True):
                st.session_state["demo_message"] = sample["text"]
                set_page(PAGE_SCAM_CHECKER)
        st.markdown("<div style='height: 0.25rem;'></div>", unsafe_allow_html=True)


def live_stats_section():
    """Live stats cards from SQLite: checks today, scams detected, top category."""
    try:
        stats = get_stats_today()
        analyzed = stats.get("messages_analyzed", 0)
        scams = stats.get("scams_detected", 0)
        top = stats.get("top_category", "GCash phishing")
    except Exception:
        analyzed, scams, top = 0, 0, "GCash phishing"

    st.markdown(
        f"""
        <div style="margin: 1rem 0;">
            <h3 style="color: {TEXT_PRIMARY}; font-size: 1rem; margin-bottom: 0.75rem;">📊 Live Stats</h3>
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 1rem;">
                <div style="
                    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
                    padding: 1rem 1.5rem; border-radius: 12px; min-width: 140px; text-align: center;
                    border-left: 4px solid #e94560;
                ">
                    <div style="font-size: 1.75rem; font-weight: bold; color: #e94560;">{analyzed}</div>
                    <div style="font-size: 0.8rem; color: #a0a0a0;">Checks today</div>
                </div>
                <div style="
                    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
                    padding: 1rem 1.5rem; border-radius: 12px; min-width: 140px; text-align: center;
                    border-left: 4px solid #ff6b6b;
                ">
                    <div style="font-size: 1.75rem; font-weight: bold; color: #ff6b6b;">{scams}</div>
                    <div style="font-size: 0.8rem; color: #a0a0a0;">Scams detected today</div>
                </div>
                <div style="
                    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
                    padding: 1rem 1.5rem; border-radius: 12px; min-width: 140px; text-align: center;
                    border-left: 4px solid #ffc107;
                ">
                    <div style="font-size: 0.95rem; font-weight: bold; color: #ffc107;">{top}</div>
                    <div style="font-size: 0.8rem; color: #a0a0a0;">Top category today</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def three_step_section():
    """How it works: 3 steps + safety tips."""
    st.markdown(
        f"""
        <div style="margin: 1.5rem 0;">
            <h3 style="color: {TEXT_PRIMARY}; margin-bottom: 1rem;">How it works</h3>
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 1rem;">
                <div style="flex: 1; min-width: 150px; background: {BG_CARD}; padding: 1.25rem; border-radius: {RADIUS}; text-align: center; border-left: 4px solid {ALERT_RED};">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📋</div>
                    <strong style="color: {ALERT_RED};">1. Paste</strong>
                    <p style="font-size: 0.85rem; color: {TEXT_MUTED}; margin: 0.35rem 0 0 0;">Paste the suspicious message (SMS, Messenger, email)</p>
                </div>
                <div style="flex: 1; min-width: 150px; background: {BG_CARD}; padding: 1.25rem; border-radius: {RADIUS}; text-align: center; border-left: 4px solid {ALERT_RED};">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
                    <strong style="color: {ALERT_RED};">2. AI explains</strong>
                    <p style="font-size: 0.85rem; color: {TEXT_MUTED}; margin: 0.35rem 0 0 0;">Get verdict (Safe / Suspicious / Scam) + reasons</p>
                </div>
                <div style="flex: 1; min-width: 150px; background: {BG_CARD}; padding: 1.25rem; border-radius: {RADIUS}; text-align: center; border-left: 4px solid {ALERT_RED};">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📤</div>
                    <strong style="color: {ALERT_RED};">3. Share & warn</strong>
                    <p style="font-size: 0.85rem; color: {TEXT_MUTED}; margin: 0.35rem 0 0 0;">Copy warning message and share with others</p>
                </div>
            </div>
            <p style="color: {ALERT_AMBER}; font-size: 0.9rem; margin-top: 1rem; text-align: center;">💡 Safety tip: We don't store your full message — only verdict and category to protect your privacy.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def trending_section():
    """Trending scams this week (cards)."""
    try:
        rows = get_trending_categories(5)
    except Exception:
        rows = [
            {"category": "GCash phishing", "count": 12},
            {"category": "Fake job offer", "count": 8},
            {"category": "Loan scam", "count": 6},
        ]

    items = "".join(
        f"""
        <div style="
            background: {BG_CARD}; padding: 0.75rem 1rem; border-radius: {RADIUS}; margin: 0.35rem 0;
            border-left: 4px solid {ALERT_RED}; display: flex; justify-content: space-between; align-items: center;
        ">
            <span style="color: {TEXT_MUTED};">{r["category"]}</span>
            <span style="color: {ALERT_RED}; font-weight: bold;">{r["count"]} reports</span>
        </div>
        """
        for r in rows
    )
    st.markdown(
        f"""
        <div style="margin: 1.5rem 0;">
            <h3 style="color: {TEXT_PRIMARY}; margin-bottom: 0.75rem;">📢 Trending scams this week</h3>
            <div style="max-width: 400px; margin: 0 auto;">
                {items}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def trust_section():
    """Trust elements: privacy note, disclaimer, community impact."""
    st.markdown(
        f"""
        <div style="
            margin-top: 2rem; padding: 1.25rem; text-align: center;
            background: {BG_CARD}; border-radius: {RADIUS}; border-left: 4px solid {SAFE_GREEN};
        ">
            <p style="color: {TEXT_MUTED}; font-size: 0.9rem; margin: 0 0 0.5rem 0;">
                <strong style="color: {SAFE_GREEN};">🔒 We don't store your full message by default.</strong> Only verdict and category are saved.
            </p>
            <p style="color: {TEXT_MUTED}; font-size: 0.85rem; margin: 0.5rem 0 0 0;">
                AI can be wrong. Always verify with official channels (banks, GCash, Maya, SSS, PhilHealth).
            </p>
            <p style="color: {TEXT_MUTED}; font-size: 0.85rem; margin: 0.25rem 0 0 0;">
                You control what you share. CheckMoYan — built for the Philippines.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sticky_bottom_cta():
    """Bottom CTA that routes to Scam Checker (Streamlit button so routing works)."""
    st.markdown("---")
    if st.button("🛡️ Check a message now", type="primary", key="landing_sticky_cta", use_container_width=True):
        set_page(PAGE_SCAM_CHECKER)
