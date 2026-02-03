"""Reusable UI: cards, badges, CTAs, toasts, mobile sticky CTA."""
import streamlit as st


def primary_cta(label: str, key: str = None, use_container_width: bool = True):
    """Strong primary CTA button."""
    return st.button(
        label,
        key=key or f"cta_{label[:20]}",
        type="primary",
        use_container_width=use_container_width,
    )


def secondary_cta(label: str, key: str = None, use_container_width: bool = True):
    """Secondary CTA button."""
    return st.button(
        label,
        key=key or f"sec_{label[:20]}",
        type="secondary",
        use_container_width=use_container_width,
    )


def card_section(title: str, content: str = None, children=None):
    """Render a card-style section with optional title and content."""
    st.markdown(
        f"""
        <div style="
            border-radius: 12px;
            padding: 1.25rem;
            margin: 0.5rem 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        ">
            <h4 style="margin:0 0 0.5rem 0; color: #e94560;">{title}</h4>
            {f'<p style="margin:0; color: #a0a0a0;">{content}</p>' if content else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if children is not None:
        st.markdown("---")
        children()


def badge(text: str, color: str = "#e94560"):
    """Inline badge."""
    st.markdown(
        f'<span style="background:{color}; color:white; padding:0.2rem 0.5rem; border-radius:6px; font-size:0.85rem;">{text}</span>',
        unsafe_allow_html=True,
    )


def toast_success(message: str):
    st.success(message)


def toast_error(message: str):
    st.error(message)


def sticky_bottom_cta(label: str, url_anchor: str = "#check"):
    """Mobile-first sticky bottom CTA (Streamlit-friendly: use anchor or query param)."""
    st.markdown(
        f"""
        <div style="
            position: fixed; bottom: 0; left: 0; right: 0;
            padding: 12px 16px; background: linear-gradient(90deg, #e94560, #0f3460);
            text-align: center; z-index: 999;
            border-radius: 12px 12px 0 0; margin: 0 -1rem;
            box-shadow: 0 -4px 12px rgba(0,0,0,0.2);
        ">
            <a href="{url_anchor}" style="color: white; text-decoration: none; font-weight: bold; font-size: 1rem;">
                {label}
            </a>
        </div>
        <div style="height: 60px;"></div>
        """,
        unsafe_allow_html=True,
    )
