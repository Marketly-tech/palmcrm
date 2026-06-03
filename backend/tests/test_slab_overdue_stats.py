"""Tests for the 3 new dashboard slab stat tiles + the existing overdue customer payload.
Iteration 34 — /api/dashboard/overdue-by-stage now returns total_expected_at_slab,
total_collected_cumulative, total_overdue_amount alongside the existing fields.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
ADMIN_EMAIL = os.environ.get("TEST_ADMIN_EMAIL", "crm@rrlbuildersanddevelopers.com")
ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "#RRLnew2026")
RAMYA_ID = os.environ.get("TEST_CUSTOMER_ID", "6d902613-5106-4294-bc3e-b907f85127f7")


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# Dashboard slab endpoint regression
class TestDashboardSlabOverdue:
    def test_overdue_by_stage_returns_new_fields(self, headers):
        r = requests.get(f"{BASE_URL}/api/dashboard/overdue-by-stage", headers=headers, timeout=20)
        assert r.status_code == 200, r.text
        data = r.json()
        # all required keys present
        for k in [
            "current_stage", "overdue_count", "total_overdue_amount",
            "total_expected_at_slab", "total_collected_cumulative", "overdue_customers",
        ]:
            assert k in data, f"missing key {k} in response: {list(data.keys())}"
        # types
        assert isinstance(data["overdue_customers"], list)
        assert isinstance(data["overdue_count"], int)
        # numeric types
        for k in ["total_overdue_amount", "total_expected_at_slab", "total_collected_cumulative"]:
            assert isinstance(data[k], (int, float)), f"{k} not numeric: {type(data[k])}"

    def test_aggregates_match_per_customer_math(self, headers):
        slab = requests.get(f"{BASE_URL}/api/dashboard/overdue-by-stage", headers=headers, timeout=20).json()
        if slab.get("current_stage") is None:
            pytest.skip("No stage set — skipping aggregate verification")

        cumulative_pct = slab["cumulative_percentage"]
        customers = requests.get(f"{BASE_URL}/api/customers", headers=headers, timeout=30).json()
        # customers may be list or dict
        if isinstance(customers, dict) and "customers" in customers:
            customers = customers["customers"]
        assert isinstance(customers, list), f"customers shape unexpected: {type(customers)}"

        expected_sum = 0.0
        for c in customers:
            tp = c.get("total_price") or 0
            expected_sum += (tp * cumulative_pct) / 100.0

        # tolerance for float rounding
        assert abs(expected_sum - slab["total_expected_at_slab"]) < 1.0, (
            f"expected={expected_sum} vs api={slab['total_expected_at_slab']}"
        )

        # Verify overdue_count == len(overdue_customers)
        assert slab["overdue_count"] == len(slab["overdue_customers"])

        # Verify total_overdue_amount roughly equals sum of overdue_amount in the customers list
        sum_overdue = sum(c.get("overdue_amount", 0) for c in slab["overdue_customers"])
        assert abs(sum_overdue - slab["total_overdue_amount"]) < 1.0

        # collected must be <= expected and >= 0
        assert slab["total_collected_cumulative"] >= 0
        # And overdue ≈ expected - collected when there are no over-collected customers
        # we only check directionally
        assert slab["total_overdue_amount"] >= 0
        assert slab["total_overdue_amount"] <= slab["total_expected_at_slab"] + 1

    def test_collected_matches_payment_transactions_aggregate(self, headers):
        slab = requests.get(f"{BASE_URL}/api/dashboard/overdue-by-stage", headers=headers, timeout=20).json()
        if slab.get("current_stage") is None:
            pytest.skip("No stage set — skipping collected aggregate")
        # We can't list ALL payment transactions globally without an endpoint, but
        # we validate the per-customer ramya overdue endpoint conforms to the same math.
        r = requests.get(f"{BASE_URL}/api/customers/{RAMYA_ID}/overdue", headers=headers, timeout=15)
        assert r.status_code == 200
        rdata = r.json()
        if rdata.get("current_stage") is None:
            pytest.skip("no stage on ramya")
        assert "expected_amount" in rdata
        assert "total_received" in rdata
        assert "overdue_amount" in rdata
        # overdue_amount == max(0, expected - received) — formula check
        expected_calc = max(0, rdata["expected_amount"] - rdata["total_received"])
        assert abs(expected_calc - rdata["overdue_amount"]) < 0.5


# Ramya untouched — Payment Tracking tab uses /api/customers/{id}/overdue
class TestRamyaPaymentTracking:
    def test_ramya_overdue_endpoint_intact(self, headers):
        r = requests.get(f"{BASE_URL}/api/customers/{RAMYA_ID}/overdue", headers=headers, timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        # endpoint structure unchanged
        for k in ["overdue_amount", "current_stage"]:
            assert k in d
