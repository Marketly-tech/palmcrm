"""
Common utility functions for RRL CRM backend.
"""
from datetime import datetime, timezone


def number_to_indian_words(num):
    """Convert a number to Indian words format (for legal documents)."""
    if num == 0:
        return "Zero"

    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def convert_less_than_thousand(n):
        if n == 0:
            return ""
        elif n < 20:
            return ones[n]
        elif n < 100:
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
        else:
            return ones[n // 100] + " Hundred" + (" " + convert_less_than_thousand(n % 100) if n % 100 != 0 else "")

    num = int(num)
    if num < 0:
        return "Minus " + number_to_indian_words(-num)

    crore = num // 10000000
    lakh = (num % 10000000) // 100000
    thousand = (num % 100000) // 1000
    remainder = num % 1000

    result = ""
    if crore > 0:
        result += convert_less_than_thousand(crore) + " Crore "
    if lakh > 0:
        result += convert_less_than_thousand(lakh) + " Lakh "
    if thousand > 0:
        result += convert_less_than_thousand(thousand) + " Thousand "
    if remainder > 0:
        result += convert_less_than_thousand(remainder)

    return result.strip() + " Rupees"


def format_indian_currency(amount, decimals=True):
    """Format amount in Indian currency style (e.g., 12,34,567.00)."""
    if amount is None:
        return "0"
    
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return "0"
    
    is_negative = amount < 0
    amount = abs(amount)
    
    if decimals:
        integer_part = int(amount)
        decimal_part = round((amount - integer_part) * 100)
        decimal_str = f".{decimal_part:02d}"
    else:
        integer_part = round(amount)
        decimal_str = ""
    
    s = str(integer_part)
    if len(s) <= 3:
        formatted = s
    else:
        formatted = s[-3:]
        s = s[:-3]
        while s:
            formatted = s[-2:] + "," + formatted
            s = s[:-2]
    
    result = formatted + decimal_str
    return f"-{result}" if is_negative else result


def get_ordinal_suffix(day):
    """Get ordinal suffix for a day number (1st, 2nd, 3rd, etc.)."""
    if 11 <= day <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')


def format_date_for_document(date_str):
    """Format a date string for document display."""
    if not date_str:
        return ""
    try:
        if isinstance(date_str, datetime):
            dt = date_str
        else:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        day = dt.day
        suffix = get_ordinal_suffix(day)
        return dt.strftime(f"{day}{suffix} %B, %Y")
    except Exception:
        return str(date_str)


def sanitize_for_json(obj):
    """Recursively convert ObjectId and datetime objects for JSON serialization."""
    from bson import ObjectId
    
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items() if k != '_id'}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def get_current_utc_time():
    """Get current UTC time."""
    return datetime.now(timezone.utc)
