"""
Tests for Reconciliation Debug endpoints (admin-only).
Covers:
- GET /api/dashboard/reconciliation (admin OK / non-admin error / shape)
- POST /api/dashboard/reconciliation/delete-orphan/{txn_id}
  - refuses when customer exists
  - deletes one small orphan and confirms counts decrease
"""
import os
import pytest
import requests
from tests.conftest_credentials import (
    ADMIN_EMAIL, ADMIN_PASSWORD,
    ACCOUNTS_EMAIL, ACCOUNTS_PASSWORD,
)

SALES_EMAIL = os.environ.get("TEST_SALES_EMAIL", "sales@rrlrprojects.com")
SALES_PASSWORD = os.environ.get("TEST_SALES_PASSWORD", "sales123")

BASE_URL = (os.environ.get('REACT_APP_BACKEND_URL') or 'https://builder-crm-dev.preview.emergentagent.com').rstrip('/')
API = f"{BASE_URL}/api"


def _login(session, email, password):
    r = session.post(f"{API}/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, f"login failed for {email}: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def session():
    return requests.Session()


@pytest.fixture(scope="module")
def admin_headers(session):
    return {"Authorization": f"Bearer {_login(session, ADMIN_EMAIL, ADMIN_PASSWORD)}"}


@pytest.fixture(scope="module")
def sales_headers(session):
    return {"Authorization": f"Bearer {_login(session, SALES_EMAIL, SALES_PASSWORD)}"}


@pytest.fixture(scope="module")
def accounts_headers(session):
    return {"Authorization": f"Bearer {_login(session, ACCOUNTS_EMAIL, ACCOUNTS_PASSWORD)}"}


class TestReconciliationGet:
    def test_admin_get_shape(self, session, admin_headers):
        r = session.get(f"{API}/dashboard/reconciliation", headers=admin_headers)
        assert r.status_code == 200, r.text
        d = r.json()
        # Required fields
        for k in [
            "aggregation_total", "aggregation_count", "loop_total", "loop_count",
            "difference", "orphan_total", "orphan_count", "null_amount_count",
            "orphan_samples", "verdict", "message",
        ]:
            assert k in d, f"missing field {k}"
        assert d["verdict"] in {"ok", "orphans", "unknown"}
        assert isinstance(d["orphan_samples"], list)
        assert len(d["orphan_samples"]) <= 25, "orphan_samples must be capped at 25"
        # Math: difference == aggregation_total - loop_total
        assert abs(d["difference"] - (d["aggregation_total"] - d["loop_total"])) < 0.5
        # Sorted desc by amount
        amounts = [o.get("amount") or 0 for o in d["orphan_samples"]]
        assert amounts == sorted(amounts, reverse=True), "orphan_samples must be sorted desc by amount"

    def test_preview_db_state_has_orphans(self, session, admin_headers):
        """Preview DB has 142 orphan txns totalling ~9.22 Cr — sanity-check it."""
        r = session.get(f"{API}/dashboard/reconciliation", headers=admin_headers)
        d = r.json()
        # Conditional check — only enforce when verdict says orphans
        if d["verdict"] == "orphans":
            assert d["orphan_count"] > 0
            assert d["orphan_total"] > 0
            # The drift should be fully explained by orphans
            assert abs(d["difference"] - d["orphan_total"]) < 0.5

    def test_non_admin_sales_gets_error_not_500(self, session, sales_headers):
        r = session.get(f"{API}/dashboard/reconciliation", headers=sales_headers)
        # MUST not be a 500. Returns 200 with {error: ...}
        assert r.status_code == 200, r.text
        d = r.json()
        assert "error" in d
        assert "Admin" in d["error"]

    def test_non_admin_accounts_gets_error(self, session, accounts_headers):
        r = session.get(f"{API}/dashboard/reconciliation", headers=accounts_headers)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "error" in d


class TestDeleteOrphan:
    def test_refuse_when_customer_exists(self, session, admin_headers):
        """Pick a real payment_transaction whose customer still exists and ensure delete is refused."""
        customers = session.get(f"{API}/customers?limit=50", headers=admin_headers).json()
        items = customers if isinstance(customers, list) else customers.get("items") or customers.get("customers", [])
        target_txn_id = None
        for c in items[:30]:
            cid = c.get("id")
            if not cid:
                continue
            pays = session.get(f"{API}/transactions/{cid}", headers=admin_headers)
            if pays.status_code != 200:
                continue
            paylist = pays.json()
            if isinstance(paylist, dict):
                paylist = paylist.get("transactions") or paylist.get("payments") or []
            if paylist:
                target_txn_id = paylist[0].get("id") or paylist[0].get("transaction_id")
                if target_txn_id:
                    break
        if not target_txn_id:
            pytest.skip("Could not find a non-orphan transaction to test refuse-to-delete")

        r = session.post(
            f"{API}/dashboard/reconciliation/delete-orphan/{target_txn_id}",
            headers=admin_headers,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert "error" in d, f"Expected refusal, got: {d}"
        assert "Refusing" in d["error"]

    def test_delete_smallest_orphan_and_verify(self, session, admin_headers):
        """Pick the smallest orphan (≤ ₹100,000) and delete it; verify counts decrease."""
        rec_before = session.get(f"{API}/dashboard/reconciliation", headers=admin_headers).json()
        if rec_before["orphan_count"] == 0:
            pytest.skip("No orphan transactions — nothing to delete")
        # Pick smallest amount orphan with amount <= 100000
        candidates = [
            o for o in rec_before["orphan_samples"]
            if o.get("amount") is not None and o["amount"] <= 100000
        ]
        if not candidates:
            # Fall back: take the smallest in the sample
            candidates = sorted(
                [o for o in rec_before["orphan_samples"] if o.get("amount") is not None],
                key=lambda x: x["amount"]
            )
        if not candidates:
            pytest.skip("No suitable small orphan found")
        target = min(candidates, key=lambda x: x.get("amount", 0))
        txn_id = target["transaction_id"]
        amount = target["amount"] or 0

        r = session.post(
            f"{API}/dashboard/reconciliation/delete-orphan/{txn_id}",
            headers=admin_headers,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("deleted") is True, f"Delete failed: {d}"
        assert d.get("transaction_id") == txn_id
        assert abs((d.get("amount") or 0) - amount) < 0.5

        # Verify counts decreased
        rec_after = session.get(f"{API}/dashboard/reconciliation", headers=admin_headers).json()
        assert rec_after["orphan_count"] == rec_before["orphan_count"] - 1
        assert abs(rec_after["orphan_total"] - (rec_before["orphan_total"] - amount)) < 0.5

    def test_delete_orphan_non_admin_refused(self, session, sales_headers):
        r = session.post(
            f"{API}/dashboard/reconciliation/delete-orphan/some-fake-id",
            headers=sales_headers,
        )
        assert r.status_code == 200, r.text
        assert "error" in r.json()

    def test_delete_nonexistent_txn(self, session, admin_headers):
        r = session.post(
            f"{API}/dashboard/reconciliation/delete-orphan/nonexistent-txn-id-xyz-12345",
            headers=admin_headers,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert "error" in d
        assert "not found" in d["error"].lower()
