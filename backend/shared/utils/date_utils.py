"""
Date and time utility functions.
"""

from datetime import date, datetime, timedelta
from typing import Optional

import pytz

from core.config import settings


def get_current_utc_datetime() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(pytz.UTC)


def get_current_date() -> date:
    """Get current date."""
    return date.today()


def get_week_start_date(target_date: Optional[date] = None) -> date:
    """Get the start date of the week (Monday) for the given date."""
    if target_date is None:
        target_date = get_current_date()

    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    return week_start


def get_week_end_date(target_date: Optional[date] = None) -> date:
    """Get the end date of the week (Sunday) for the given date."""
    week_start = get_week_start_date(target_date)
    week_end = week_start + timedelta(days=settings.DATE_WEEK_DAYS)
    return week_end


def is_date_in_range(check_date: date, start_date: date, end_date: date) -> bool:
    """Check if a date is within a given range."""
    return start_date <= check_date <= end_date


def days_until_expiry(expiry_date: date) -> int:
    """Calculate days until expiry date."""
    today = get_current_date()
    delta = expiry_date - today
    return delta.days
