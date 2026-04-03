"""Common utilities shared across document templates."""
from datetime import datetime
from utils import number_to_indian_words, format_indian_currency, get_ordinal_suffix


def format_inr(amount):
    """Format amount in Indian Rupee notation."""
    try:
        amount = float(amount or 0)
    except (ValueError, TypeError):
        amount = 0
    if amount == 0:
        return "0"
    is_negative = amount < 0
    amount = abs(amount)
    s = f"{amount:,.2f}"
    parts = s.split(".")
    whole = parts[0].replace(",", "")
    decimal = parts[1] if len(parts) > 1 else "00"
    if len(whole) <= 3:
        formatted = whole
    else:
        last3 = whole[-3:]
        rest = whole[:-3]
        groups = []
        while rest:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        formatted = ",".join(groups) + "," + last3
    result = f"{formatted}.{decimal}"
    return f"-{result}" if is_negative else result
