"""
    author: ffpereira
    date: 2025-11-21
"""

from flask import abort


def parse_bool(value):
    """Safely parse a boolean value from a string, returning False for any non-true values."""
    return str(value).lower() in ("true", "1", "yes")


def parse_int(value, field):
    """Safely parse an integer, aborting with a 400 error if parsing fails."""
    try:
        return int(value)
    except (TypeError, ValueError):
        abort(400, description=f"{field} must be an integer")


def safe_percentage(numerator, denominator, decimals=2):
    """Safely calculate average, returning None if denominator is 0."""
    return round(numerator / denominator * 100, decimals)

def safe_avg(total, count, decimals=2):
    """Safely calculate percentage, returning None if whole is 0."""
    return round(total / count, decimals)