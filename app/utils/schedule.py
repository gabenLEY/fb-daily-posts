from datetime import datetime, timedelta

def unix_for_today_or_tomorrow(time_hhmm: str) -> int:
    h, m = [int(x) for x in time_hhmm.split(":")]
    now = datetime.now()
    when = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if when <= now:
        when += timedelta(days=1)
    return int(when.timestamp())
