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
def _create_follow_up(token, *, status="Follow-up", next_date=None, next_time=None, notes="TEST_bell", stage_key="handover"):
    # Default stage is `handover` (100%) so by default the follow-up is NOT
    # auto-dropped by the new "paid-up stage" filter (Ramya is ~40% paid).
    payload = {
        "stage_key": stage_key,
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
        # Use distinct unpaid stages so dedup doesn't drop either.
        open_fu = _create_follow_up(admin_token, status="Follow-up", notes="TEST_open", stage_key="handover")
        done_fu = _create_follow_up(admin_token, status="Completed", notes="TEST_done", stage_key="flooring")
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

        past_fu = _create_follow_up(admin_token, next_date=past_str, notes="TEST_past", stage_key="2nd_floor")
        today_fu = _create_follow_up(admin_token, next_date=today_str, next_time="10:00", notes="TEST_today", stage_key="6th_floor")
        future_fu = _create_follow_up(admin_token, next_date=future_str, notes="TEST_future", stage_key="10th_floor")
        unsched_fu = _create_follow_up(admin_token, next_date=None, notes="TEST_unsched", stage_key="handover")
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



# ============================================================
# iteration_49: Dedup + stage-paid-drop logic
# ============================================================
# PAYMENT_STAGES cumulative %s (from /app/backend/utils/payment_helpers.py):
#   podium=40, 2nd_floor=45, 6th_floor=50, 10th_floor=55, 14th_floor=60,
#   18th_floor=65, 22nd_floor=70, top_roof=80, flooring=90, handover=100
# Ramya is ~40.4% paid → podium (40%) is fully cleared (paid-up), so any
# follow-up on `podium` MUST be dropped. 2nd_floor (45%) is the next unpaid
# stage and `handover` (100%) is the furthest unpaid stage.
import time


class TestDedupAndStageDropLogic:
    """iteration_49 — collapse historical log entries to one row per
    (customer × stage) and drop stages already paid-up by the customer."""

    def test_dedup_to_latest_status_per_stage(self, admin_token):
        """Seed 3 follow-ups on the SAME unpaid stage with different statuses
        and verify only the LATEST (by created_at) appears in /pending."""
        # Use 22nd_floor (70% cumulative) — well above Ramya's 40% paid
        f1 = _create_follow_up(admin_token, status="Dialed", notes="TEST_dedup_1", stage_key="22nd_floor")
        time.sleep(1.2)  # ensure created_at strictly increases (ISO sort)
        f2 = _create_follow_up(admin_token, status="Connected", notes="TEST_dedup_2", stage_key="22nd_floor")
        time.sleep(1.2)
        f3 = _create_follow_up(admin_token, status="Follow-up", notes="TEST_dedup_3", stage_key="22nd_floor")
        ids = {f1["id"], f2["id"], f3["id"]}
        try:
            r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(admin_token), timeout=15)
            assert r.status_code == 200, r.text
            data = r.json()
            mine = [x for x in data
                    if x["customer_id"] == TEST_CUSTOMER
                    and x.get("stage_key") == "22nd_floor"
                    and x["follow_up_id"] in ids]
            # Exactly ONE entry — the latest by created_at — for this stage
            assert len(mine) == 1, f"Expected 1 entry for 22nd_floor, got {len(mine)}: {mine}"
            assert mine[0]["follow_up_id"] == f3["id"], (
                f"Latest follow-up should be returned, got {mine[0]['follow_up_id']} (expected {f3['id']})"
            )
            assert mine[0]["status"] == "Follow-up"
            assert mine[0]["notes"] == "TEST_dedup_3"
        finally:
            for fid in ids:
                _delete_follow_up(admin_token, fid)

    def test_dedup_does_not_collapse_different_stages(self, admin_token):
        """Two follow-ups on DIFFERENT (unpaid) stages must both appear."""
        a = _create_follow_up(admin_token, status="Follow-up", notes="TEST_diff_a", stage_key="2nd_floor")
        b = _create_follow_up(admin_token, status="Follow-up", notes="TEST_diff_b", stage_key="handover")
        try:
            r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(admin_token), timeout=15)
            assert r.status_code == 200
            ids = {x["follow_up_id"] for x in r.json()}
            assert a["id"] in ids, "Follow-up on 2nd_floor (45%) should appear (unpaid)"
            assert b["id"] in ids, "Follow-up on handover (100%) should appear (unpaid)"
        finally:
            _delete_follow_up(admin_token, a["id"])
            _delete_follow_up(admin_token, b["id"])

    def test_drop_follow_up_on_paid_stage(self, admin_token):
        """A follow-up logged on a stage the customer has ALREADY PAID
        (podium @ 40% for Ramya who is at 40.4%) must NOT appear in /pending."""
        fu = _create_follow_up(admin_token, status="Follow-up", notes="TEST_paid_stage_drop", stage_key="podium")
        try:
            r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(admin_token), timeout=15)
            assert r.status_code == 200
            ids = {x["follow_up_id"] for x in r.json()}
            assert fu["id"] not in ids, (
                "Follow-up on already-paid stage 'podium' (40%) MUST be dropped "
                f"for Ramya (~40.4% paid). Got entry in response."
            )
            # Sanity: verify the follow-up DOES still exist on the customer
            # record (we only drop from /pending, not from history).
            g = requests.get(f"{API}/customers/{TEST_CUSTOMER}/follow-ups",
                             headers=_hdr(admin_token), timeout=10)
            assert g.status_code == 200
            assert any(x["id"] == fu["id"] for x in g.json().get("follow_ups", [])), \
                "Follow-up history should still contain the entry"
        finally:
            _delete_follow_up(admin_token, fu["id"])

    def test_keep_follow_up_on_unpaid_far_stage(self, admin_token):
        """A follow-up on a far-future unpaid stage (handover @ 100%) MUST
        appear in /pending for a partially-paid customer."""
        fu = _create_follow_up(admin_token, status="Follow-up", notes="TEST_unpaid_far", stage_key="handover")
        try:
            r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(admin_token), timeout=15)
            assert r.status_code == 200
            row = next((x for x in r.json() if x["follow_up_id"] == fu["id"]), None)
            assert row is not None, \
                "Follow-up on unpaid stage 'handover' (100%) should appear for ~40%-paid Ramya"
            assert row["stage_key"] == "handover"
            assert row["customer_id"] == TEST_CUSTOMER
        finally:
            _delete_follow_up(admin_token, fu["id"])

    def test_keep_follow_up_on_next_unpaid_stage(self, admin_token):
        """The immediately-next unpaid stage (2nd_floor @ 45% for Ramya
        ~40.4%) must still appear."""
        fu = _create_follow_up(admin_token, status="Follow-up", notes="TEST_next_unpaid", stage_key="2nd_floor")
        try:
            r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(admin_token), timeout=15)
            assert r.status_code == 200
            assert any(x["follow_up_id"] == fu["id"] for x in r.json()), \
                "Follow-up on 2nd_floor (45%) MUST appear — customer only at ~40.4%"
        finally:
            _delete_follow_up(admin_token, fu["id"])

    def test_endpoint_performance_under_2s(self, admin_token):
        """Endpoint should complete in <2s even at current preview-DB scale."""
        t0 = time.time()
        r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(admin_token), timeout=5)
        elapsed = time.time() - t0
        assert r.status_code == 200
        assert elapsed < 2.0, f"Endpoint took {elapsed:.2f}s — possible N+1 explosion"

    def test_no_duplicate_customer_stage_pairs_across_all_data(self, admin_token):
        """Global invariant: response must never contain two rows sharing the
        same (customer_id, stage_key). This is the user-reported screenshot
        bug."""
        r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(admin_token), timeout=15)
        assert r.status_code == 200
        seen = {}
        dupes = []
        for row in r.json():
            key = (row.get("customer_id"), row.get("stage_key"))
            if key in seen:
                dupes.append(key)
            seen[key] = row
        assert not dupes, f"Duplicate (customer × stage) rows found in /pending: {dupes}"
