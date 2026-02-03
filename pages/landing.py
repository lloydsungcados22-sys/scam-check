"""Landing page: scam-checker theme, hero, CTAs, sample demos, live stats, how-it-works, trending, trust."""
import streamlit as st
from components.landing import (
    hero_section,
    cta_section,
    sample_scams_section,
    live_stats_section,
    three_step_section,
    trending_section,
    trust_section,
    sticky_bottom_cta,
)


def run():
    hero_section()
    cta_section()
    sample_scams_section()
    live_stats_section()
    three_step_section()
    trending_section()
    trust_section()
    sticky_bottom_cta()
