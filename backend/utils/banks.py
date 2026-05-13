"""
Canonical bank name registry.

Single source of truth used by the customer-filter `/banks` endpoint
and the customer-list query. Aliases are normalized to a canonical name
so the filter dropdown shows each bank exactly once.
"""
import re
from typing import Dict, List, Optional


# Canonical name → list of accepted aliases (case-insensitive, trimmed)
BANK_CANONICAL: Dict[str, List[str]] = {
    "HDFC Bank": ["HDFC", "HDFC Bank", "HDFC BANK"],
    "Bank of Baroda": ["BOB", "Bank of Baroda", "BANK OF BARODA"],
    "TATA Capital": ["TATA", "TATA Capital", "TATA CAPITAL"],
    "State Bank of India": ["SBI", "State Bank of India", "STATE BANK OF INDIA"],
    "ICICI Bank": ["ICICI", "ICICI Bank", "ICICI BANK"],
    "Axis Bank": ["AXIS", "Axis Bank", "AXIS BANK"],
    "Punjab National Bank": ["PNB", "Punjab National Bank"],
    "Kotak Mahindra Bank": ["KOTAK", "Kotak", "Kotak Mahindra Bank"],
    "Canara Bank": ["CANARA", "Canara", "Canara Bank", "CANARA BANK"],
    "Bajaj Housing Finance": ["BAJAJ", "Bajaj", "Bajaj Housing Finance"],
}


def _norm(value: str) -> str:
    """Lowercase + collapse whitespace for alias matching."""
    return re.sub(r"\s+", " ", value.strip().lower())


# Build reverse lookup: normalized alias → canonical
_ALIAS_TO_CANONICAL: Dict[str, str] = {
    _norm(alias): canonical
    for canonical, aliases in BANK_CANONICAL.items()
    for alias in aliases
}


def to_canonical(raw: Optional[str]) -> Optional[str]:
    """Resolve a raw bank value to its canonical name.

    Returns None for empty input. Unknown banks pass through unchanged
    (so user-typed banks not in the registry still appear in the filter).
    """
    if not raw or not raw.strip():
        return None
    return _ALIAS_TO_CANONICAL.get(_norm(raw), raw.strip())


def aliases_for(canonical: str) -> List[str]:
    """Return the list of accepted aliases for a canonical bank name.

    Used by list-filter queries to match all variants when filtering
    by the canonical name (e.g. user picks "HDFC Bank" → also matches
    rows where finance_bank == "HDFC" or "HDFC BANK").
    """
    if canonical in BANK_CANONICAL:
        return BANK_CANONICAL[canonical]
    return [canonical]


def list_canonical_names() -> List[str]:
    """Return canonical bank names in display order."""
    return list(BANK_CANONICAL.keys())
