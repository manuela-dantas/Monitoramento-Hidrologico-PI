from datetime import datetime, timezone


def current_hour_utc():
    return datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)