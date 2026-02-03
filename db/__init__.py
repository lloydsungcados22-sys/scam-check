# CheckMoYan DB layer
from .schema import init_db, get_conn
from .queries import (
    ensure_user,
    get_user_plan,
    set_user_plan,
    record_usage,
    get_usage_today,
    insert_scan,
    get_stats_today,
    get_trending_categories,
    insert_upgrade_request,
    list_upgrade_requests,
    update_upgrade_request,
    get_upgrade_request,
)

__all__ = [
    "init_db",
    "get_conn",
    "ensure_user",
    "get_user_plan",
    "set_user_plan",
    "record_usage",
    "get_usage_today",
    "insert_scan",
    "get_stats_today",
    "get_trending_categories",
    "insert_upgrade_request",
    "list_upgrade_requests",
    "update_upgrade_request",
    "get_upgrade_request",
]
