"""
Tests for Call-Status filter on GET /api/customers and the denormalised
`latest_call_status` field maintenance via follow-up mutations.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get(
    "REACT_APP_BACKEND_URL",
    "https://builder-crm-dev.preview.emergentagent.com",
).rstrip("/")
CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"  # Ramya

ADMIN_CREDS = {"email": "crm@rrlbuildersanddevelopers.com", "password": "#RRLnew2026"}


def _login(creds):
    r = requests.post(f"{BASE_URL}/api/auth/login", json=creds, timeout=20)
    assert r.status_code == 200, r.text
    return r.json().get("token") or r.json().get("access_token")


@pytest.fixture(scope="module")
def token():
    return _login(ADMIN_CREDS)


def _h(t):
    return {"Authorization": f"Bearer {t}", "Content-Type": "application/json"}


def _get_customers(token, **params):
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    r = requests.get(f"{BASE_URL}/api/customers?{qs}", headers=_h(token), timeout=20)
    assert r.status_code == 200, r.text
    return r.json()


# ---------------- Filter behaviour ----------------
class TestCallStatusFilter:
    def test_no_filter_returns_all(self, token):
        data = _get_customers(token, limit=500)
        assert "customers" in data
        assert "total" in data
        assert isinstance(data["total"], int)
        # Every customer should have latest_call_status key (in-memory derived)
        for c in data["customers"]:
            assert "latest_call_status" in c

    def test_filter_connected(self, token):
        data = _get_customers(token, call_status="Connected", limit=500)
        for c in data["customers"]:
            assert c.get("latest_call_status") == "Connected", c.get("name")
        # total must equal returned count when limit > total
        assert data["total"] == len(data["customers"])

    def test_filter_unanswered_includes_ramya(self, token):
        data = _get_customers(token, call_status="Unanswered", limit=500)
        names = [c.get("name") for c in data["customers"]]
        assert data["total"] >= 1
        # Ramya should be among Unanswered (per request context)
        assert any("Ramya" in (n or "") for n in names), names

    def test_filter_completed(self, token):
        data = _get_customers(token, call_status="Completed", limit=500)
        for c in data["customers"]:
            assert c.get("latest_call_status") == "Completed"

    def test_filter_no_status(self, token):
        data = _get_customers(token, call_status="no_status", limit=500)
        # All returned must have None / missing latest_call_status
        for c in data["customers"]:
            assert c.get("latest_call_status") in (None, ""), c.get("name")
        assert data["total"] == len(data["customers"])

    def test_total_reflects_full_match_count_not_page(self, token):
        # Get full count
        full = _get_customers(token, call_status="no_status", limit=500)
        # Now request with limit=1 — total must be the same
        sliced = _get_customers(token, call_status="no_status", limit=1)
        assert sliced["total"] == full["total"]
        assert len(sliced["customers"]) <= 1

    def test_combinable_with_agreement_filter(self, token):
        # Issue chained filter — should not error
        data = _get_customers(token, agreement_filter="overdue",
                              call_status="Unanswered", limit=500)
        for c in data["customers"]:
            assert c.get("latest_call_status") == "Unanswered"


# ---------------- Denormalised field maintenance ----------------
def _create_followup(token, status, note="TEST_call_status_filter"):
    meta = requests.get(
        f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
        headers=_h(token), timeout=20,
    ).json()
    stage_key = meta["all_stages"][0]["key"]
    r = requests.post(
        f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
        headers=_h(token),
        json={"stage_key": stage_key, "status": status, "notes": note},
        timeout=20,
    )
    assert r.status_code == 200, r.text
    return r.json()["id"]


def _get_customer_call_status(token, cid):
    """Find the customer in a paged list and return latest_call_status."""
    # iterate pages — DB is small
    for skip in range(0, 1000, 200):
        data = _get_customers(token, skip=skip, limit=200)
        for c in data["customers"]:
            if c.get("id") == cid:
                return c.get("latest_call_status")
        if len(data["customers"]) < 200:
            break
    return None


def _is_in_filter(token, status, cid):
    data = _get_customers(token, call_status=status, limit=500)
    return any(c.get("id") == cid for c in data["customers"])


class TestRecomputeLatestCallStatus:
    """End-to-end sequence: add → patch → delete and verify filter sees changes."""

    @pytest.fixture(autouse=True)
    def _restore_state(self, token):
        # Snapshot follow_ups before
        meta = requests.get(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
            headers=_h(token), timeout=20,
        ).json()
        original_ids = [f["id"] for f in meta["follow_ups"]]
        created_ids = []
        yield created_ids
        # Cleanup any test-created ones (don't touch pre-existing)
        for fid in created_ids:
            if fid not in original_ids:
                requests.delete(
                    f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups/{fid}",
                    headers=_h(token), timeout=20,
                )

    def test_add_followup_updates_denormalised_status(self, token, _restore_state):
        fid = _create_followup(token, "Dialed", note="TEST_seq_add")
        _restore_state.append(fid)
        # The most recent follow-up dictates latest_call_status — it should be "Dialed"
        assert _is_in_filter(token, "Dialed", CUSTOMER_ID), \
            "Customer not in ?call_status=Dialed after creating Dialed follow-up"
        status_now = _get_customer_call_status(token, CUSTOMER_ID)
        assert status_now == "Dialed", f"got {status_now!r}"

    def test_patch_followup_updates_denormalised_status(self, token, _restore_state):
        fid = _create_followup(token, "Dialed", note="TEST_seq_patch")
        _restore_state.append(fid)
        # PATCH to Completed
        r = requests.patch(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups/{fid}",
            headers=_h(token),
            json={"status": "Completed"},
            timeout=20,
        )
        assert r.status_code == 200, r.text
        assert not _is_in_filter(token, "Dialed", CUSTOMER_ID) or \
               _get_customer_call_status(token, CUSTOMER_ID) != "Dialed"
        assert _get_customer_call_status(token, CUSTOMER_ID) == "Completed"

    def test_delete_followup_restores_no_status_when_last(self, token):
        """If we delete ALL follow-ups, customer should appear in ?call_status=no_status."""
        # Snapshot existing follow-ups
        meta = requests.get(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
            headers=_h(token), timeout=20,
        ).json()
        existing = list(meta["follow_ups"])
        if not existing:
            pytest.skip("No existing follow-ups to delete-restore test against")

        # Delete each existing follow-up
        for f in existing:
            requests.delete(
                f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups/{f['id']}",
                headers=_h(token), timeout=20,
            )

        try:
            # Now customer must show as no_status
            assert _is_in_filter(token, "no_status", CUSTOMER_ID), \
                "Customer should appear in no_status after deleting all follow-ups"
            assert _get_customer_call_status(token, CUSTOMER_ID) is None
        finally:
            # Restore the prior follow-ups so we don't permanently nuke Ramya's data.
            # We re-POST each one (note: id will change, but content is preserved).
            for f in existing:
                requests.post(
                    f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups",
                    headers=_h(token),
                    json={
                        "stage_key": f.get("stage_key"),
                        "status": f.get("status"),
                        "notes": f.get("notes") or "",
                        "next_follow_up_date": f.get("next_follow_up_date"),
                        "next_follow_up_time": f.get("next_follow_up_time"),
                    },
                    timeout=20,
                )

    def test_quick_status_endpoint_updates_denormalised(self, token):
        """POST /follow-ups/quick-status should also update latest_call_status."""
        r = requests.post(
            f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups/quick-status",
            headers=_h(token),
            json={"status": "Connected"},
            timeout=20,
        )
        assert r.status_code == 200, r.text
        try:
            assert _get_customer_call_status(token, CUSTOMER_ID) == "Connected"
            assert _is_in_filter(token, "Connected", CUSTOMER_ID)
        finally:
            # Restore back to Unanswered via the same endpoint to honour the
            # context-note "leave Ramya at Unanswered"
            requests.post(
                f"{BASE_URL}/api/customers/{CUSTOMER_ID}/follow-ups/quick-status",
                headers=_h(token),
                json={"status": "Unanswered"},
                timeout=20,
            )
