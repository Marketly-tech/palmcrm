"""
Backend tests for canonical bank filter (Iteration 33).
- /api/customers/banks returns deduped canonical names
- /api/customers/banks/registry returns full canonical list
- /api/customers?finance_bank=... matches all aliases
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASSWORD = "#RRLnew2026"

CANONICAL = [
    "HDFC Bank", "Bank of Baroda", "TATA Capital", "State Bank of India",
    "ICICI Bank", "Axis Bank", "Punjab National Bank",
    "Kotak Mahindra Bank", "Canara Bank", "Bajaj Housing Finance",
]


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def seeded_customers(headers):
    """Insert 3 TEST customers with HDFC alias variants. Cleaned up after module."""
    created = []
    variants = ["HDFC", "HDFC BANK", "hdfc bank"]
    for v in variants:
        payload = {
            "name": f"_TEST_BankFilter_{uuid.uuid4().hex[:6]}",
            "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
            "phone": f"9{uuid.uuid4().int % 10**9:09d}",
            "project": "Palm Altezze",
            "unit_number": f"T-{uuid.uuid4().hex[:3]}",
            "tower": "Tower A",
            "finance_type": "loan",
            "finance_bank": v,
        }
        r = requests.post(f"{API}/customers", json=payload, headers=headers)
        assert r.status_code in (200, 201), f"Create failed: {r.status_code} {r.text}"
        created.append(r.json())
    yield created
    for c in created:
        cid = c.get("id")
        if cid:
            requests.delete(f"{API}/customers/{cid}", headers=headers)


# ---------- /banks dedup ----------
def test_banks_returns_canonical_dedup(headers, seeded_customers):
    r = requests.get(f"{API}/customers/banks", headers=headers)
    assert r.status_code == 200
    banks = r.json()
    assert isinstance(banks, list)
    # All three aliases must collapse to one canonical "HDFC Bank"
    hdfc_like = [b for b in banks if "hdfc" in b.lower()]
    assert hdfc_like == ["HDFC Bank"], f"Expected only ['HDFC Bank'], got {hdfc_like}"
    # No duplicates overall
    assert len(banks) == len(set(banks))


# ---------- /banks/registry ----------
def test_banks_registry_full_canonical_list(headers):
    r = requests.get(f"{API}/customers/banks/registry", headers=headers)
    assert r.status_code == 200
    banks = r.json()
    assert isinstance(banks, list)
    assert set(CANONICAL).issubset(set(banks)), f"Missing: {set(CANONICAL) - set(banks)}"
    assert len(banks) >= 10


# ---------- filter matches all aliases ----------
def test_filter_hdfc_matches_all_aliases(headers, seeded_customers):
    r = requests.get(f"{API}/customers", headers=headers, params={"finance_bank": "HDFC Bank", "limit": 200})
    assert r.status_code == 200
    data = r.json()
    customers = data.get("customers", [])
    seeded_names = {c["name"] for c in seeded_customers}
    found = {c["name"] for c in customers if c["name"] in seeded_names}
    assert found == seeded_names, f"Filter missed aliases. Expected {seeded_names}, got {found}"
    # All matched customers should have an HDFC-ish bank value
    for c in customers:
        if c["name"] in seeded_names:
            assert "hdfc" in (c.get("finance_bank") or "").lower()


def test_filter_canonical_match_axis(headers):
    """Filter by 'Axis Bank' should not throw, even if DB has zero or alias rows."""
    r = requests.get(f"{API}/customers", headers=headers, params={"finance_bank": "Axis Bank", "limit": 200})
    assert r.status_code == 200
    body = r.json()
    assert "customers" in body and "total" in body


def test_filter_unknown_bank_passthrough(headers):
    """Unknown bank value should still build a valid query (no 500)."""
    r = requests.get(f"{API}/customers", headers=headers, params={"finance_bank": "Some Unknown Bank XYZ"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0 or all(
        (c.get("finance_bank") or "").strip().lower() == "some unknown bank xyz"
        for c in body["customers"]
    )


def test_ramya_not_mutated(headers):
    """Sanity: Ramya test lead remains untouched."""
    r = requests.get(f"{API}/customers/6d902613-5106-4294-bc3e-b907f85127f7", headers=headers)
    assert r.status_code == 200
    assert r.json().get("name", "").strip() == "Ramya test lead"
