import sys
from datetime import datetime


def format_date(date_str: str, precision: str) -> str:
    """Format a date string according to precision level.

    Args:
        date_str: ISO date string or year string.
        precision: One of 'year', 'month', or 'day'.

    Returns:
        Formatted date string in UK English.
    """
    if precision == "year":
        return date_str

    if precision == "month":
        dt = datetime.strptime(date_str, "%Y-%m")
        return dt.strftime("%B %Y")

    # precision == "day"
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    if sys.platform == "win32":
        return dt.strftime("%#d %B %Y")
    return dt.strftime("%-d %B %Y")


def truncate(text: str, max_chars: int) -> str:
    """Truncate text to max_chars, appending ellipsis if truncated.

    Args:
        text: The input string.
        max_chars: Maximum number of characters before truncation.

    Returns:
        Original text if within limit, or truncated text with '...' appended.
    """
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text
