"""
Tests for Multi-Level Calling / Follow-up Tracking endpoints.
Covers POST/GET/DELETE /api/customers/{id}/follow-ups and /api/follow-ups/upcoming
"""
import os
from datetime import datetime, timedelta

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://builder-crm-dev.preview.emergentagent.com").rstrip("/")
CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"

ADMIN_CREDS = {"email": "crm@rrlbuildersanddevelopers.com", "password": "#RRLnew2026"}
SALES_CREDS = {"email": "sales@rrlrprojects.com", "password": "sales123"}
ACCOUNTS_CREDS = {"email": "accounts@rrlbuilders.com", "password": "accounts123"}

FOLLOW_UP_STATUSES = {"Dialed", "Connected", "Unanswered", "Follow-up", "Completed"}


def _login(creds):
    r = requests.post(f"{BASE_URL}/api/auth/login", json=creds, timeout=20)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    token = r.json().get("token") or r.json().get("access_token")
    assert token, f"no token in {r.json()}"
    return token


@pytest.fixture(scope="module")
def admin_token():
    return _login(ADMIN_CREDS)


@pytest.fixture(scope="module")
def sales_token():
    return _login(SALES_CREDS)


@pytest.fixture(scope="module")
def accounts_token():
    return _login(ACCOUNTS_CREDS)


def _h(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ----------------- GET shape -----------------
class TestGetFollowUps:
    def test_get_returns_expected_shape(self, admin_token):
        r = requests.get(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
            headers=_h(admin_token), timeout=20,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        for key in ("follow_ups", "overdue_stages", "current_stage", "all_stages", "statuses"):
            assert key in data, f"missing key {key} in {list(data.keys())}"
        assert isinstance(data["follow_ups"], list)
        assert isinstance(data["overdue_stages"], list)
        assert isinstance(data["all_stages"], list) and len(data["all_stages"]) > 0
        assert set(data["statuses"]) == FOLLOW_UP_STATUSES

    def test_get_404_unknown_customer(self, admin_token):
        r = requests.get(
            f"{BASE_URL}/api/customers/does-not-exist-xyz/follow-ups",
            headers=_h(admin_token), timeout=20,
        )
        assert r.status_code == 404


# ----------------- POST validation -----------------
class TestFollowUpValidation:
    def test_invalid_status_returns_400(self, admin_token):
        # Get a valid stage_key first
        meta = requests.get(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
            headers=_h(admin_token), timeout=20,
        ).json()
        valid_stage = meta["all_stages"][0]["key"]
        r = requests.post(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
            headers=_h(admin_token),
            json={"stage_key": valid_stage, "status": "BOGUS", "notes": "x"},
            timeout=20,
        )
        assert r.status_code == 400, r.text

    def test_invalid_stage_returns_400(self, admin_token):
        r = requests.post(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
            headers=_h(admin_token),
            json={"stage_key": "not-a-stage", "status": "Dialed", "notes": "x"},
            timeout=20,
        )
        assert r.status_code == 400, r.text


# ----------------- Create/Delete + persistence -----------------
def _create_followup(token, status="Dialed", next_date=None, next_time=None, note_text="TEST_followup"):
    meta = requests.get(
        f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
        headers=_h(token), timeout=20,
    ).json()
    stage_key = meta["all_stages"][0]["key"]
    body = {
        "stage_key": stage_key,
        "status": status,
        "notes": note_text,
        "next_follow_up_date": next_date,
        "next_follow_up_time": next_time,
    }
    r = requests.post(
        f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
        headers=_h(token), json=body, timeout=20,
    )
    return r, stage_key


class TestFollowUpCRUD:
    def test_create_get_delete_admin(self, admin_token):
        today = datetime.utcnow().date().isoformat()
        r, stage_key = _create_followup(admin_token, status="Connected",
                                        next_date=today, next_time="09:00",
                                        note_text="TEST_admin_create")
        assert r.status_code == 200, r.text
        entry = r.json()
        for k in ("id", "stage_key", "stage_name", "status", "notes",
                  "next_follow_up_date", "next_follow_up_time",
                  "created_at", "created_by", "created_by_name"):
            assert k in entry, f"missing {k}"
        assert entry["status"] == "Connected"
        assert entry["stage_key"] == stage_key

        fu_id = entry["id"]

        # Verify persisted via GET
        g = requests.get(f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
                         headers=_h(admin_token), timeout=20).json()
        ids = [f["id"] for f in g["follow_ups"]]
        assert fu_id in ids
        # sorted desc by created_at -- the most recent should be index 0 if newest
        timestamps = [f.get("created_at", "") for f in g["follow_ups"]]
        assert timestamps == sorted(timestamps, reverse=True)

        # Delete
        d = requests.delete(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups/{fu_id}",
            headers=_h(admin_token), timeout=20,
        )
        assert d.status_code == 200, d.text

        # Verify removed
        g2 = requests.get(f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
                          headers=_h(admin_token), timeout=20).json()
        assert fu_id not in [f["id"] for f in g2["follow_ups"]]

    def test_delete_unknown_followup_returns_404(self, admin_token):
        r = requests.delete(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups/non-existent-id",
            headers=_h(admin_token), timeout=20,
        )
        assert r.status_code == 404

    def test_sales_role_can_create_and_delete(self, sales_token):
        r, _ = _create_followup(sales_token, status="Dialed", note_text="TEST_sales_create")
        assert r.status_code == 200, r.text
        fid = r.json()["id"]
        d = requests.delete(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups/{fid}",
            headers=_h(sales_token), timeout=20,
        )
        assert d.status_code == 200, d.text

    def test_accounts_role_can_create_and_delete(self, accounts_token):
        r, _ = _create_followup(accounts_token, status="Unanswered",
                                note_text="TEST_accounts_create")
        assert r.status_code == 200, r.text
        fid = r.json()["id"]
        d = requests.delete(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups/{fid}",
            headers=_h(accounts_token), timeout=20,
        )
        assert d.status_code == 200, d.text


# ----------------- Upcoming -----------------
class TestUpcoming:
    def test_upcoming_returns_only_today_or_pastdue(self, admin_token):
        today = datetime.utcnow().date().isoformat()
        future = (datetime.utcnow().date() + timedelta(days=10)).isoformat()
        past = (datetime.utcnow().date() - timedelta(days=2)).isoformat()

        r_today, _ = _create_followup(admin_token, status="Follow-up",
                                      next_date=today, next_time="08:00",
                                      note_text="TEST_today")
        r_future, _ = _create_followup(admin_token, status="Follow-up",
                                       next_date=future, next_time="08:00",
                                       note_text="TEST_future")
        r_past, _ = _create_followup(admin_token, status="Follow-up",
                                     next_date=past, next_time="08:00",
                                     note_text="TEST_past")
        assert r_today.status_code == 200
        assert r_future.status_code == 200
        assert r_past.status_code == 200
        today_id = r_today.json()["id"]
        future_id = r_future.json()["id"]
        past_id = r_past.json()["id"]

        try:
            r = requests.get(f"{BASE_URL}/api/follow-ups/upcoming",
                             headers=_h(admin_token), timeout=20)
            assert r.status_code == 200, r.text
            items = r.json()
            assert isinstance(items, list)

            ids = {it["follow_up_id"] for it in items}
            assert today_id in ids, "today's entry should be in upcoming"
            assert past_id in ids, "past-due entry should be in upcoming"
            assert future_id not in ids, "future entry should NOT be in upcoming"

            # Check flags + sort + required fields
            today_entry = next(it for it in items if it["follow_up_id"] == today_id)
            past_entry = next(it for it in items if it["follow_up_id"] == past_id)
            assert today_entry["is_today"] is True
            assert today_entry["is_past_due"] is False
            assert past_entry["is_past_due"] is True
            for k in ("customer_id", "customer_name", "stage_name", "status",
                      "next_follow_up_date"):
                assert k in today_entry

            # Sorted ascending by (date, time)
            keys = [(it["next_follow_up_date"], it.get("next_follow_up_time") or "23:59")
                    for it in items]
            assert keys == sorted(keys)
        finally:
            for fid in (today_id, future_id, past_id):
                requests.delete(
                    f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups/{fid}",
                    headers=_h(admin_token), timeout=20,
                )

    def test_upcoming_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/follow-ups/upcoming", timeout=20)
        assert r.status_code in (401, 403)
