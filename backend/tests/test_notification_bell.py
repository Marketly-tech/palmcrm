"""Backend tests for the Notification Bell endpoints:
- GET  /api/follow-ups/pending  -> list non-completed follow-ups (all customers)
- PATCH /api/customers/{cid}/follow-ups/{fid} -> mark completed (or update status)
Built on iteration_37 (POST /follow-ups, DELETE /follow-ups) + iteration_38 work.
"""
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN = {"email": "crm@rrlbuildersanddevelopers.com", "password": "#RRLnew2026"}
SALES = {"email": "sales@rrlrprojects.com", "password": "sales123"}
ACCOUNTS = {"email": "accounts@rrlbuilders.com", "password": "accounts123"}
TEST_CUSTOMER = "6d902613-5106-4294-bc3e-b907f85127f7"


def _login(creds):
    r = requests.post(f"{API}/auth/login", json=creds, timeout=15)
    assert r.status_code == 200, f"Login failed for {creds['email']}: {r.text}"
    body = r.json()
    return body.get("access_token") or body.get("token")


def _hdr(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ---------- Session-scoped fixtures ----------
@pytest.fixture(scope="session")
def admin_token():
    return _login(ADMIN)


@pytest.fixture(scope="session")
def sales_token():
    return _login(SALES)


@pytest.fixture(scope="session")
def accounts_token():
    return _login(ACCOUNTS)


# ---------- Helpers ----------
def _create_follow_up(token, *, status="Follow-up", next_date=None, next_time=None, notes="TEST_bell"):
    payload = {
        "stage_key": "podium",
        "status": status,
        "notes": notes,
        "next_follow_up_date": next_date,
        "next_follow_up_time": next_time,
    }
    r = requests.post(
        f"{API}/customers/{TEST_CUSTOMER}/follow-ups",
        json=payload,
        headers=_hdr(token),
        timeout=15,
    )
    assert r.status_code == 200, f"Create follow-up failed: {r.status_code} {r.text}"
    return r.json()


def _delete_follow_up(token, fid):
    requests.delete(
        f"{API}/customers/{TEST_CUSTOMER}/follow-ups/{fid}",
        headers=_hdr(token),
        timeout=10,
    )


# ---------- Cleanup fixture: kills every TEST_ follow-up on Ramya before+after ----------
@pytest.fixture(autouse=True, scope="module")
def cleanup_test_followups(admin_token):
    def _purge():
        r = requests.get(
            f"{API}/customers/{TEST_CUSTOMER}/follow-ups",
            headers=_hdr(admin_token), timeout=10,
        )
        if r.status_code == 200:
            for fu in r.json().get("follow_ups", []):
                if (fu.get("notes") or "").startswith("TEST_"):
                    _delete_follow_up(admin_token, fu["id"])
    _purge()
    yield
    _purge()


# ============================================================
# GET /api/follow-ups/pending
# ============================================================
class TestPendingEndpoint:
    def test_requires_auth(self):
        r = requests.get(f"{API}/follow-ups/pending", timeout=10)
        assert r.status_code in (401, 403)

    def test_returns_list_and_excludes_completed(self, admin_token):
        # create two entries: one open Follow-up, one already Completed
        open_fu = _create_follow_up(admin_token, status="Follow-up", notes="TEST_open")
        done_fu = _create_follow_up(admin_token, status="Completed", notes="TEST_done")
        try:
            r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(admin_token), timeout=15)
            assert r.status_code == 200
            data = r.json()
            assert isinstance(data, list)
            ids = {x["follow_up_id"] for x in data}
            assert open_fu["id"] in ids, "Open follow-up should be returned"
            assert done_fu["id"] not in ids, "Completed follow-up must NOT appear"
            # validate enrichment shape on the open entry
            row = next(x for x in data if x["follow_up_id"] == open_fu["id"])
            for key in [
                "customer_id", "customer_name", "stage_name", "status",
                "notes", "is_today", "is_past_due", "next_follow_up_date",
            ]:
                assert key in row, f"missing key {key}"
            assert row["customer_id"] == TEST_CUSTOMER
            assert row["status"] == "Follow-up"
        finally:
            _delete_follow_up(admin_token, open_fu["id"])
            _delete_follow_up(admin_token, done_fu["id"])

    def test_sorting_past_due_then_today_then_upcoming_then_unscheduled(self, admin_token):
        today = datetime.now(timezone.utc).date()
        past_str = (today - timedelta(days=2)).isoformat()
        today_str = today.isoformat()
        future_str = (today + timedelta(days=5)).isoformat()

        past_fu = _create_follow_up(admin_token, next_date=past_str, notes="TEST_past")
        today_fu = _create_follow_up(admin_token, next_date=today_str, next_time="10:00", notes="TEST_today")
        future_fu = _create_follow_up(admin_token, next_date=future_str, notes="TEST_future")
        unsched_fu = _create_follow_up(admin_token, next_date=None, notes="TEST_unsched")
        created = [past_fu["id"], today_fu["id"], future_fu["id"], unsched_fu["id"]]
        try:
            r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(admin_token), timeout=15)
            assert r.status_code == 200
            data = r.json()
            # extract only the ones we created, preserving server order
            ours_ordered = [x["follow_up_id"] for x in data if x["follow_up_id"] in created]
            assert ours_ordered == [
                past_fu["id"], today_fu["id"], future_fu["id"], unsched_fu["id"]
            ], f"Sort order mismatch: {ours_ordered}"

            # flag correctness
            by_id = {x["follow_up_id"]: x for x in data if x["follow_up_id"] in created}
            assert by_id[past_fu["id"]]["is_past_due"] is True
            assert by_id[past_fu["id"]]["is_today"] is False
            assert by_id[today_fu["id"]]["is_today"] is True
            assert by_id[today_fu["id"]]["is_past_due"] is False
            assert by_id[future_fu["id"]]["is_today"] is False
            assert by_id[future_fu["id"]]["is_past_due"] is False
        finally:
            for fid in created:
                _delete_follow_up(admin_token, fid)

    def test_role_parity_sales(self, sales_token, admin_token):
        fu = _create_follow_up(admin_token, notes="TEST_role_sales")
        try:
            r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(sales_token), timeout=15)
            assert r.status_code == 200
            assert any(x["follow_up_id"] == fu["id"] for x in r.json())
        finally:
            _delete_follow_up(admin_token, fu["id"])

    def test_role_parity_accounts(self, accounts_token, admin_token):
        fu = _create_follow_up(admin_token, notes="TEST_role_acc")
        try:
            r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(accounts_token), timeout=15)
            assert r.status_code == 200
            assert any(x["follow_up_id"] == fu["id"] for x in r.json())
        finally:
            _delete_follow_up(admin_token, fu["id"])


# ============================================================
# PATCH /api/customers/{id}/follow-ups/{fid}
# ============================================================
class TestPatchFollowUp:
    def test_mark_completed_stamps_metadata(self, admin_token):
        fu = _create_follow_up(admin_token, notes="TEST_patch_complete")
        try:
            r = requests.patch(
                f"{API}/customers/{TEST_CUSTOMER}/follow-ups/{fu['id']}",
                json={"status": "Completed"},
                headers=_hdr(admin_token), timeout=15,
            )
            assert r.status_code == 200, r.text
            body = r.json()
            assert body.get("status") == "Completed"

            # verify persistence on tracker
            g = requests.get(
                f"{API}/customers/{TEST_CUSTOMER}/follow-ups",
                headers=_hdr(admin_token), timeout=10,
            )
            assert g.status_code == 200
            match = next((x for x in g.json()["follow_ups"] if x["id"] == fu["id"]), None)
            assert match is not None, "Follow-up should still exist after PATCH (history)"
            assert match["status"] == "Completed"
            assert match.get("completed_at"), "completed_at should be stamped"
            assert match.get("completed_by"), "completed_by should be set"
            assert match.get("completed_by_name"), "completed_by_name should be set"

            # verify it disappears from /pending
            p = requests.get(f"{API}/follow-ups/pending", headers=_hdr(admin_token), timeout=10)
            assert p.status_code == 200
            assert not any(x["follow_up_id"] == fu["id"] for x in p.json())
        finally:
            _delete_follow_up(admin_token, fu["id"])

    def test_invalid_status_returns_400(self, admin_token):
        fu = _create_follow_up(admin_token, notes="TEST_patch_bad_status")
        try:
            r = requests.patch(
                f"{API}/customers/{TEST_CUSTOMER}/follow-ups/{fu['id']}",
                json={"status": "NotARealStatus"},
                headers=_hdr(admin_token), timeout=10,
            )
            assert r.status_code == 400
        finally:
            _delete_follow_up(admin_token, fu["id"])

    def test_no_fields_returns_400(self, admin_token):
        fu = _create_follow_up(admin_token, notes="TEST_patch_empty")
        try:
            r = requests.patch(
                f"{API}/customers/{TEST_CUSTOMER}/follow-ups/{fu['id']}",
                json={},
                headers=_hdr(admin_token), timeout=10,
            )
            assert r.status_code == 400
        finally:
            _delete_follow_up(admin_token, fu["id"])

    def test_unknown_follow_up_returns_404(self, admin_token):
        r = requests.patch(
            f"{API}/customers/{TEST_CUSTOMER}/follow-ups/{uuid.uuid4()}",
            json={"status": "Completed"},
            headers=_hdr(admin_token), timeout=10,
        )
        assert r.status_code == 404

    def test_sales_can_mark_completed(self, sales_token, admin_token):
        fu = _create_follow_up(admin_token, notes="TEST_patch_sales")
        try:
            r = requests.patch(
                f"{API}/customers/{TEST_CUSTOMER}/follow-ups/{fu['id']}",
                json={"status": "Completed"},
                headers=_hdr(sales_token), timeout=10,
            )
            assert r.status_code == 200
        finally:
            _delete_follow_up(admin_token, fu["id"])

    def test_accounts_can_mark_completed(self, accounts_token, admin_token):
        fu = _create_follow_up(admin_token, notes="TEST_patch_acc")
        try:
            r = requests.patch(
                f"{API}/customers/{TEST_CUSTOMER}/follow-ups/{fu['id']}",
                json={"status": "Completed"},
                headers=_hdr(accounts_token), timeout=10,
            )
            assert r.status_code == 200
        finally:
            _delete_follow_up(admin_token, fu["id"])
