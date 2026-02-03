"""DB layer: Snowflake (from secrets.toml [SNOWFLAKE]) or SQLite fallback."""
import streamlit as st


def _use_snowflake():
    """True if SNOWFLAKE is configured in secrets."""
    try:
        cfg = st.secrets.get("SNOWFLAKE")
        return bool(cfg and isinstance(cfg, dict) and (cfg.get("account") or cfg.get("ACCOUNT")))
    except Exception:
        return False


def get_conn():
    """Return Snowflake connection if configured, else SQLite."""
    if _use_snowflake():
        from .snowflake_schema import get_conn as sf_conn
        return sf_conn()
    from . import _sqlite_schema
    return _sqlite_schema.get_conn()


def init_db():
    """Create tables: Snowflake if configured, else SQLite."""
    if _use_snowflake():
        from .snowflake_schema import init_db as sf_init
        sf_init()
        return
    from . import _sqlite_schema
    _sqlite_schema.init_db()


def get_param_style():
    """Return placeholder for parameterized queries: %s for Snowflake, ? for SQLite."""
    return "%s" if _use_snowflake() else "?"
