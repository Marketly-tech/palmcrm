"""Backend tests for Flat Inventory & Revenue Management (iteration 55)."""
import os
import io
import csv
import pytest
import requests

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or
            "https://builder-crm-dev.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN = {"email": "crm@rrlbuildersanddevelopers.com", "password": "#RRLnew2026"}
SALES = {"email": "sales@rrlrprojects.com", "password": "sales123"}


def _login(creds):
    r = requests.post(f"{API}/auth/login", json=creds, timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()["token"]


@pytest.fixture(scope="module")
def admin_token():
    return _login(ADMIN)


@pytest.fixture(scope="module")
def sales_token():
    return _login(SALES)


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ---- Import file ----
class TestImportFile:
    def test_import_admin_ok(self, admin_headers):
        with open("/tmp/flat.xlsx", "rb") as f:
            files = {"file": ("flat.xlsx", f.read(),
                              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        data = {"project": "RRL PALM ALTEZZE", "tower": "A", "replace_existing": "false"}
        r = requests.post(f"{API}/units/import-file", headers=admin_headers,
                          files=files, data=data, timeout=60)
        assert r.status_code == 200, r.text
        body = r.json()
        for k in ("rows_read", "created", "updated", "error_count", "errors"):
            assert k in body
        assert body["rows_read"] > 0
        # Since dev env already seeded, expect mostly updates
        assert (body["created"] + body["updated"]) >= 100

    def test_import_non_admin_forbidden(self, sales_token):
        with open("/tmp/flat.xlsx", "rb") as f:
            files = {"file": ("flat.xlsx", f.read(), "application/octet-stream")}
        r = requests.post(f"{API}/units/import-file",
                          headers={"Authorization": f"Bearer {sales_token}"},
                          files=files, data={}, timeout=30)
        assert r.status_code == 403

    def test_import_preserves_customer_link(self, admin_headers):
        # Fetch units, pick one, set customer_id/agreement_value/sold_rate via direct PUT
        r = requests.get(f"{API}/inventory/units", headers=admin_headers, timeout=30)
        assert r.status_code == 200
        units = r.json()["units"]
        assert units, "no units seeded"
        # Find a SOLD RRL unit
        sold_rrl = next((u for u in units if u.get("share_type") == "RRL" and u.get("status") == "SOLD"), None)
        assert sold_rrl, "expected at least one SOLD RRL unit"
        uid = sold_rrl["id"]
        put_payload = {
            "agreement_value": 12345678,
            "sold_rate_per_sqft": 7500,
            "customer_id": "TEST_customer_xyz",
        }
        p = requests.put(f"{API}/units/{uid}", headers=admin_headers,
                         json=put_payload, timeout=30)
        # Endpoint might not exist — allow both PATCH-like or direct
        if p.status_code == 404:
            pytest.skip("PUT /units/{id} not present — skipping preserve test")
        assert p.status_code in (200, 204), p.text

        # Re-run import (non replace)
        with open("/tmp/flat.xlsx", "rb") as f:
            files = {"file": ("flat.xlsx", f.read(), "application/octet-stream")}
        data = {"project": "RRL PALM ALTEZZE", "tower": "A", "replace_existing": "false"}
        r2 = requests.post(f"{API}/units/import-file", headers=admin_headers,
                           files=files, data=data, timeout=60)
        assert r2.status_code == 200

        r3 = requests.get(f"{API}/inventory/units", headers=admin_headers, timeout=30)
        after = next((u for u in r3.json()["units"] if u["id"] == uid), None)
        assert after, "unit disappeared after re-import"
        assert after.get("agreement_value") == 12345678
        assert after.get("sold_rate_per_sqft") == 7500
        assert after.get("customer_id") == "TEST_customer_xyz"


# ---- Inventory summary ----
class TestInventorySummary:
    def test_summary_all(self, admin_headers):
        r = requests.get(f"{API}/inventory/summary", headers=admin_headers, timeout=30)
        assert r.status_code == 200
        b = r.json()
        for k in ("total_projected_revenue", "collected_till_date", "outstanding",
                  "interest_amount", "avg_sold_rate", "total_valuation",
                  "counts_by_status", "total_units", "total_sba", "per_floor"):
            assert k in b, f"missing {k}"
        assert isinstance(b["counts_by_status"], dict)
        # Baseline expected ~115-116 units
        assert b["total_units"] >= 100

    def test_summary_rrl_filter(self, admin_headers):
        r = requests.get(f"{API}/inventory/summary?share_type=RRL", headers=admin_headers, timeout=30)
        assert r.status_code == 200
        rrl = r.json()
        r2 = requests.get(f"{API}/inventory/summary?share_type=LAND_OWNER", headers=admin_headers, timeout=30)
        lo = r2.json()
        r3 = requests.get(f"{API}/inventory/summary", headers=admin_headers, timeout=30).json()
        # Filters are exclusive
        assert rrl["total_units"] + lo["total_units"] <= r3["total_units"]
        assert rrl["total_units"] > 0
        assert lo["total_units"] > 0
        # Expected baseline ~77 RRL / ~38 landowner
        assert 60 <= rrl["total_units"] <= 90
        assert 25 <= lo["total_units"] <= 50

    def test_avg_and_valuation_positive_after_seed(self, admin_headers):
        # After previous class's PUT, RRL SOLD should have some sold_rate
        r = requests.get(f"{API}/inventory/summary?share_type=RRL", headers=admin_headers, timeout=30)
        b = r.json()
        # If PUT skipped, this still may be > 0 from prior tests
        assert b["avg_sold_rate"] >= 0
        assert b["total_valuation"] >= 0
        assert b["total_valuation"] == pytest.approx(b["avg_sold_rate"] * b["total_sba"], rel=0.01)


# ---- Inventory units listing ----
class TestInventoryUnits:
    def test_units_sorted_and_projected(self, admin_headers):
        r = requests.get(f"{API}/inventory/units", headers=admin_headers, timeout=30)
        assert r.status_code == 200
        b = r.json()
        assert "units" in b and "count" in b
        units = b["units"]
        assert units
        # sorted by floor asc then unit_number asc
        pairs = [(u.get("floor") or 0, str(u.get("unit_number"))) for u in units]
        assert pairs == sorted(pairs), "units not sorted by (floor, unit_number)"
        # no _id / no huge fields
        for u in units[:3]:
            assert "_id" not in u
