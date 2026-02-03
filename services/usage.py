"""Rate limits: free vs premium daily check limits (from Admin → Payment config, stored in DB)."""
from services.payments import get_payment_config
from db.queries import (
    ensure_user,
    get_user_plan,
    get_usage_today,
    record_usage,
    insert_scan,
)


def _get_limits():
    """Daily limits from DB (Admin → Payment config)."""
    try:
        pay = get_payment_config()
        free = int(pay.get("free_daily_limit", 2))
        premium = int(pay.get("premium_daily_limit", 9999))
        return free, premium
    except Exception:
        return 2, 9999


def get_daily_limit(email: str) -> int:
    """Return max checks per day for this user (free vs premium/pro)."""
    if not email:
        free, _ = _get_limits()
        return free
    ensure_user(email)
    plan_info = get_user_plan(email)
    plan = (plan_info.get("plan") or "free").lower()
    premium_until = plan_info.get("premium_until")
    # If premium/pro but expired, treat as free
    if plan in ("premium", "pro") and premium_until:
        from datetime import datetime
        try:
            until = datetime.strptime(premium_until, "%Y-%m-%d").date()
            if until >= datetime.utcnow().date():
                _, premium = _get_limits()
                return premium
        except Exception:
            pass
    free, _ = _get_limits()
    return free


def can_user_check(email: str) -> tuple[bool, str]:
    """
    Return (True, "") if user can run a check; else (False, "reason").
    """
    limit = get_daily_limit(email)
    used = get_usage_today(email or "anonymous")
    if used >= limit:
        return False, f"You've used {used} of {limit} free checks today. Upgrade to Premium for unlimited checks."
    return True, ""


def record_check(
    email: str,
    verdict: str,
    confidence: int,
    category: str,
    signals_json: str,
    msg_hash: str,
) -> None:
    """Record usage and insert scan row (no raw message)."""
    record_usage(email or "anonymous")
    insert_scan(
        email=(email or "anonymous"),
        verdict=verdict,
        confidence=confidence,
        category=category or "",
        signals_json=signals_json or "[]",
        msg_hash=msg_hash or "",
    )
