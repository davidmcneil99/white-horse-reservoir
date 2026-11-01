import logging
import sys
from datetime import datetime


def format_date(date_str: str, precision: str) -> str:
    """Format a date string according to precision level.

    Args:
        date_str: ISO date string or year string.
        precision: One of 'year', 'month', or 'day'.

    Returns:
        Formatted date string in UK English. Returns original string on parse failure.
    """
    if precision == "year":
        return date_str

    if precision == "month":
        # Try YYYY-MM-DD first (data stores month-precision dates as first-of-month),
        # then fall back to YYYY-MM.
        for fmt in ("%Y-%m-%d", "%Y-%m"):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%B %Y")
            except ValueError:
                continue
        logging.warning("format_date: could not parse %r with month precision", date_str)
        return date_str

    # precision == "day"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        logging.warning("format_date: could not parse %r with day precision", date_str)
        return date_str
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
