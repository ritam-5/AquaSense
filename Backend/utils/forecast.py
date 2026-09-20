import calendar
from datetime import date as ddate


def _parse(d):
    return ddate.fromisoformat(d) if isinstance(d, str) else d


def same_month(d, ref):
    return d.year == ref.year and d.month == ref.month


def same_day(d, ref):
    return same_month(d, ref) and d.day == ref.day


def forecast_month_total(entries, now=None):
    """Projects the month-end total from the daily rate observed so far."""
    now = now or ddate.today()
    month_entries = [e for e in entries if same_month(_parse(e["date"]), now)]
    total = sum(e["litres"] for e in month_entries)
    day_of_month = now.day
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    if day_of_month == 0:
        return total
    daily_rate = total / day_of_month
    return round(daily_rate * days_in_month)


def month_total(entries, ref=None):
    ref = ref or ddate.today()
    return sum(e["litres"] for e in entries if same_month(_parse(e["date"]), ref))


def day_total(entries, ref=None):
    ref = ref or ddate.today()
    return sum(e["litres"] for e in entries if same_day(_parse(e["date"]), ref))
