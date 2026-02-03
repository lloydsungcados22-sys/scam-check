"""Payment config and plan pricing from Admin panel (stored in DB). No secrets.toml for payment."""
from db.queries import get_payment_config_from_db


def _default_config() -> dict:
    """Default payment config when none set in DB."""
    return {
        "gcash_number": "",
        "gcash_name": "",
        "maya_number": "",
        "maya_name": "",
        "premium_price_php": 199,
        "premium_billing": "Month",
        "pro_price_php": 999,
        "pro_billing": "monthly",
        "free_daily_limit": 2,
        "premium_daily_limit": 9999,
    }


def get_payment_config() -> dict:
    """
    Return payment config from DB (set in Admin → Payment config).
    If not set, returns defaults with empty GCash/Maya details.
    """
    db_config = get_payment_config_from_db()
    if not db_config or not isinstance(db_config, dict):
        return _default_config()
    default = _default_config()
    out = {}
    for k in default:
        v = db_config.get(k)
        if v is None:
            out[k] = default[k]
        elif k in ("premium_price_php", "pro_price_php", "free_daily_limit", "premium_daily_limit"):
            try:
                out[k] = int(v)
            except (TypeError, ValueError):
                out[k] = default[k]
        else:
            out[k] = str(v).strip() if v else default[k]
    return out


def get_plans_config() -> list:
    """Return list of plan dicts for Pricing page. Values from DB (Admin → Payment config)."""
    pay = get_payment_config()
    return [
        {
            "key": "free",
            "name": "Free",
            "price_php": 0,
            "billing": "",
            "features": [
                f"{pay['free_daily_limit']} checks per day",
                "Basic verdict & reasons",
                "Shareable warning text",
                "No screenshot upload",
            ],
        },
        {
            "key": "premium",
            "name": "Premium",
            "price_php": pay["premium_price_php"],
            "billing": pay["premium_billing"],
            "features": [
                "Unlimited checks",
                "Advanced explainers",
                "Priority support",
            ],
        },
        {
            "key": "pro",
            "name": "Pro",
            "price_php": pay["pro_price_php"],
            "billing": pay["pro_billing"],
            "features": [
                "Everything in Premium",
                "Priority verification",
                "Bulk check (coming soon)",
                "Dedicated support",
            ],
        },
    ]
