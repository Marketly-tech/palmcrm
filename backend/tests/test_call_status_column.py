"""
Tests for the Customers list Call Status column (iteration 38).
- POST /api/customers/{id}/follow-ups/quick-status
- GET /api/customers now returns latest_call_status fields
- Roles parity: admin, sales, accounts
"""
import os
import pytest
import requests

def _read_frontend_env_url():
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None


BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or _read_frontend_env_url() or "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL not configured"
TEST_CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"

CREDS = {
    "admin": {"email": "crm@rrlbuildersanddevelopers.com", "password": "#RRLnew2026"},
    "sales": {"email": "sales@rrlrprojects.com", "password": "sales123"},
    "accounts": {"email": "accounts@rrlbuilders.com", "password": "accounts123"},
}

CREATED_FOLLOWUP_IDS = []


def _login(role):
    r = requests.post(f"{BASE_URL}/api/auth/login", json=CREDS[role], timeout=15)
    assert r.status_code == 200, f"Login {role} failed: {r.status_code} {r.text[:120]}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def admin_headers():
    return {"Authorization": f"Bearer {_login('admin')}"}


@pytest.fixture(scope="module")
def sales_headers():
    return {"Authorization": f"Bearer {_login('sales')}"}


@pytest.fixture(scope="module")
def accounts_headers():
    return {"Authorization": f"Bearer {_login('accounts')}"}


# ---------- POST quick-status validation ----------
class TestQuickStatusValidation:
    def test_invalid_status_returns_400(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/follow-ups/quick-status",
            json={"status": "BogusStatus"}, headers=admin_headers, timeout=15,
        )
        assert r.status_code == 400
        assert "Invalid status" in r.json().get("detail", "")

    def test_unknown_customer_returns_404(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/customers/non-existent-customer-id-xyz/follow-ups/quick-status",
            json={"status": "Dialed"}, headers=admin_headers, timeout=15,
        )
        assert r.status_code == 404


# ---------- POST quick-status happy path + persistence ----------
class TestQuickStatusHappyPath:
    def test_admin_can_set_call_status_and_persists(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/follow-ups/quick-status",
            json={"status": "Connected"}, headers=admin_headers, timeout=15,
        )
        assert r.status_code == 200, r.text
        entry = r.json()
        # Entry shape
        assert entry["status"] == "Connected"
        assert entry["notes"] == ""
        assert entry["next_follow_up_date"] is None
        assert entry["next_follow_up_time"] is None
        assert entry.get("stage_key"), "stage_key should be set"
        assert entry.get("stage_name"), "stage_name should be set"
        assert "id" in entry and "created_at" in entry
        CREATED_FOLLOWUP_IDS.append(entry["id"])

        # Verify persisted on the customer document
        list_r = requests.get(
            f"{BASE_URL}/api/customers", headers=admin_headers, timeout=15,
            params={"search": "Ramya"},
        )
        assert list_r.status_code == 200
        cust = next(
            (c for c in list_r.json()["customers"] if c["id"] == TEST_CUSTOMER_ID),
            None,
        )
        assert cust is not None, "Test customer missing in list response"
        assert cust.get("latest_call_status") == "Connected"
        assert cust.get("latest_call_status_at") is not None
        assert cust.get("latest_call_status_stage") is not None

    def test_setting_new_status_updates_latest(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/follow-ups/quick-status",
            json={"status": "Follow-up"}, headers=admin_headers, timeout=15,
        )
        assert r.status_code == 200
        CREATED_FOLLOWUP_IDS.append(r.json()["id"])

        list_r = requests.get(
            f"{BASE_URL}/api/customers", headers=admin_headers, timeout=15,
            params={"search": "Ramya"},
        )
        cust = next(
            c for c in list_r.json()["customers"] if c["id"] == TEST_CUSTOMER_ID
        )
        assert cust["latest_call_status"] == "Follow-up"


# ---------- Role parity ----------
class TestRoleParity:
    def test_sales_can_set_call_status(self, sales_headers):
        r = requests.post(
            f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/follow-ups/quick-status",
            json={"status": "Dialed"}, headers=sales_headers, timeout=15,
        )
        assert r.status_code == 200, r.text
        CREATED_FOLLOWUP_IDS.append(r.json()["id"])

    def test_accounts_can_set_call_status(self, accounts_headers):
        r = requests.post(
            f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/follow-ups/quick-status",
            json={"status": "Unanswered"}, headers=accounts_headers, timeout=15,
        )
        assert r.status_code == 200, r.text
        CREATED_FOLLOWUP_IDS.append(r.json()["id"])


# ---------- GET /customers schema for column ----------
class TestCustomersListSchema:
    def test_every_customer_has_latest_call_status_key(self, admin_headers):
        r = requests.get(
            f"{BASE_URL}/api/customers?limit=20", headers=admin_headers, timeout=20,
        )
        assert r.status_code == 200
        for c in r.json()["customers"]:
            assert "latest_call_status" in c, f"Missing key on {c.get('id')}"


# ---------- Tracker history integration ----------
class TestTrackerHistoryIntegration:
    def test_quick_status_entries_visible_in_tracker(self, admin_headers):
        r = requests.get(
            f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/follow-ups",
            headers=admin_headers, timeout=15,
        )
        assert r.status_code == 200
        data = r.json()
        ids = {fu["id"] for fu in data.get("follow_ups", [])}
        # At least one of the created quick-status entries should be in the tracker
        assert CREATED_FOLLOWUP_IDS, "No follow-ups created in previous tests"
        assert any(fid in ids for fid in CREATED_FOLLOWUP_IDS), (
            "Quick-status entries are not surfaced in tracker history"
        )


# ---------- Cleanup ----------
def teardown_module(module):
    """Remove TEST_ follow-ups created on Ramya during this run."""
    try:
        token = _login("admin")
        headers = {"Authorization": f"Bearer {token}"}
        for fid in CREATED_FOLLOWUP_IDS:
            requests.delete(
                f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/follow-ups/{fid}",
                headers=headers, timeout=10,
            )
    except Exception as e:
        print(f"Cleanup error: {e}")
