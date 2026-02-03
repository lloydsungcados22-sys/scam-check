"""Scam + tech theme: attractive alert colors, techy accents, mobile-first. All from secrets for payments/API."""
import streamlit as st

# Scam theme: danger + trust
ALERT_RED = "#ef4444"
ALERT_DARK_RED = "#b91c1c"
ALERT_AMBER = "#f59e0b"
SAFE_GREEN = "#10b981"
SAFE_TEAL = "#14b8a6"

# Tech theme: cyan, purple, dark
ACCENT_CYAN = "#06b6d4"
ACCENT_PURPLE = "#8b5cf6"
BG_DARK = "#0f172a"
BG_DARKER = "#020617"
BG_CARD = "#1e293b"
BG_CARD_HOVER = "#334155"
BORDER_ACCENT = "rgba(239, 68, 68, 0.4)"
BORDER_TECH = "rgba(6, 182, 212, 0.3)"
TEXT_PRIMARY = "#f1f5f9"
TEXT_MUTED = "#94a3b8"
RADIUS = "12px"
SHADOW = "0 4px 14px rgba(0,0,0,0.3)"
GLOW_RED = "0 0 20px rgba(239, 68, 68, 0.25)"
GLOW_CYAN = "0 0 16px rgba(6, 182, 212, 0.2)"


def inject_theme():
    """Inject global CSS: scam + tech style (no hardcoded payment/API — use secrets.toml)."""
    st.markdown(
        f"""
        <style>
            /* Base: techy dark gradient */
            .stApp {{ background: linear-gradient(180deg, {BG_DARK} 0%, {BG_DARKER} 50%, #0c1222 100%); }}
            [data-testid="stSidebar"] {{ display: none !important; }}
            [data-testid="stSidebar"] + div {{ margin-left: 0 !important; }}
            section[data-testid="stSidebar"] {{ display: none !important; }}
            
            /* Typography */
            h1, h2, h3 {{ color: {TEXT_PRIMARY} !important; font-weight: 700 !important; }}
            p {{ color: {TEXT_MUTED} !important; }}
            
            /* Buttons: scam red primary, tech cyan secondary */
            .stButton > button {{
                border-radius: {RADIUS} !important;
                font-weight: 600 !important;
                padding: 0.6rem 1.2rem !important;
                min-height: 44px;
                transition: transform 0.15s, box-shadow 0.15s;
            }}
            .stButton > button[kind="primary"] {{
                background: linear-gradient(135deg, {ALERT_RED}, {ALERT_DARK_RED}) !important;
                border: 1px solid rgba(239, 68, 68, 0.5) !important;
                box-shadow: {SHADOW}, {GLOW_RED};
            }}
            .stButton > button[kind="primary"]:hover {{
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
            }}
            .stButton > button[kind="secondary"] {{
                background: {BG_CARD} !important;
                border: 1px solid {BORDER_TECH} !important;
                color: {ACCENT_CYAN} !important;
            }}
            .stButton > button[kind="secondary"]:hover {{
                box-shadow: {GLOW_CYAN};
            }}
            
            /* Cards */
            [data-testid="stVerticalBlock"] > div {{ border-radius: {RADIUS}; }}
            [data-testid="stExpander"] {{
                background: {BG_CARD};
                border: 1px solid {BORDER_ACCENT};
                border-radius: {RADIUS};
                box-shadow: {SHADOW};
            }}
            
            /* Text area: tech card */
            [data-testid="stTextArea"] textarea {{
                background: {BG_CARD} !important;
                border: 1px solid {BORDER_TECH} !important;
                border-radius: {RADIUS};
                color: {TEXT_PRIMARY} !important;
            }}
            
            [data-testid="stCaptionContainer"] {{ color: {TEXT_MUTED} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
