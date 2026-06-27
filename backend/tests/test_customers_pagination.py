"""Tests for customer pagination (skip/limit) - iteration 41."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # Try frontend/.env via filesystem if not set in environment
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
                    break
    except Exception:
        pass

ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASSWORD = "#RRLnew2026"
PROTECTED_CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"  # Ramya


@pytest.fixture(scope="module")
def admin_session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    r = s.post(f"{BASE_URL}/api/auth/login",
               json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    token = r.json().get("token") or r.json().get("access_token")
    assert token, f"No token in login response: {r.json()}"
    s.headers.update({"Authorization": f"Bearer {token}"})
    return s


@pytest.fixture(scope="module")
def seeded_customers(admin_session):
    """Seed 55 TEST_pagination customers and cleanup at end."""
    created_ids = []
    for i in range(55):
        payload = {
            "name": f"TEST_pagination_{i}",
            "phone": f"90000{i:05d}",
            "email": f"TEST_pagination_{i}@example.com",
            "project": "Test Project Pagination",
            "tower": "T1",
            "unit_number": f"U{i}",
            "saleable_area": 1000,
            "total_price": 5000000,
            "booking_amount": 100000,
        }
        r = admin_session.post(f"{BASE_URL}/api/customers", json=payload)
        if r.status_code in (200, 201):
            data = r.json()
            cid = data.get("id") or data.get("customer", {}).get("id")
            if cid:
                created_ids.append(cid)
    yield created_ids
    # Cleanup
    for cid in created_ids:
        try:
            admin_session.delete(f"{BASE_URL}/api/customers/{cid}")
        except Exception:
            pass


class TestCustomerPagination:

    def test_default_limit_is_50(self, admin_session, seeded_customers):
        r = admin_session.get(f"{BASE_URL}/api/customers")
        assert r.status_code == 200
        data = r.json()
        assert "customers" in data and "total" in data
        assert len(data["customers"]) <= 50
        # Total must reflect UNPAGINATED count and should exceed 50 after seeding
        assert data["total"] >= 50, f"total={data['total']}"

    def test_explicit_limit_param(self, admin_session, seeded_customers):
        r = admin_session.get(f"{BASE_URL}/api/customers?skip=0&limit=25")
        assert r.status_code == 200
        data = r.json()
        assert len(data["customers"]) == 25
        # total still unpaginated
        assert data["total"] >= 50

    def test_skip_returns_next_page(self, admin_session, seeded_customers):
        r1 = admin_session.get(f"{BASE_URL}/api/customers?skip=0&limit=50")
        r2 = admin_session.get(f"{BASE_URL}/api/customers?skip=50&limit=50")
        assert r1.status_code == 200 and r2.status_code == 200
        page1 = r1.json()["customers"]
        page2 = r2.json()["customers"]
        assert len(page1) == 50
        assert len(page2) >= 1  # at least some rows beyond first 50
        # No overlap
        ids1 = {c["id"] for c in page1}
        ids2 = {c["id"] for c in page2}
        assert ids1.isdisjoint(ids2), "Pages should not overlap"
        # total identical
        assert r1.json()["total"] == r2.json()["total"]

    def test_total_unaffected_by_pagination(self, admin_session, seeded_customers):
        r_small = admin_session.get(f"{BASE_URL}/api/customers?skip=0&limit=5")
        r_big = admin_session.get(f"{BASE_URL}/api/customers?skip=0&limit=200")
        assert r_small.json()["total"] == r_big.json()["total"]

    def test_skip_beyond_total_returns_empty(self, admin_session, seeded_customers):
        r = admin_session.get(f"{BASE_URL}/api/customers?skip=10000&limit=50")
        assert r.status_code == 200
        assert r.json()["customers"] == []

    def test_protected_customer_still_present(self, admin_session, seeded_customers):
        # Ensure Ramya is in the unpaginated full result
        r = admin_session.get(f"{BASE_URL}/api/customers?skip=0&limit=500")
        assert r.status_code == 200
        ids = {c["id"] for c in r.json()["customers"]}
        assert PROTECTED_CUSTOMER_ID in ids, "Ramya must not be deleted"
