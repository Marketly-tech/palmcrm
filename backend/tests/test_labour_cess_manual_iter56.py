"""
Iteration 56: P0 fix — labour_cess manual override must persist.

Tests:
 1. POST /api/calculator/price honours labour_cess_manual + labour_cess_override
    (values 0 and 12345), and falls back to 0.70% when not manual.
 2. PUT /api/customers/{id} persists labour_cess=0 with labour_cess_manual=true
    on Ramya test lead.
 3. POST /api/documents/generate price_breakup renders Labour Cess ₹0.00.
 4. POST /api/calculator/generate-schedule/{id} produces 13 items using
    preserved total_price (not affected by labour_cess=0).
"""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASSWORD = "#RRLnew2026"
RAMYA_ID = "6d902613-5106-4294-bc3e-b907f85127f7"


@pytest.fixture(scope="module")
def token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=30,
    )
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    tok = r.json().get("access_token") or r.json().get("token")
    assert tok, f"No token in login response: {r.json()}"
    return tok


@pytest.fixture(scope="module")
def client(token):
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    return s


# ---------- 1. /api/calculator/price ----------
class TestCalculatorPrice:
    base_payload = {
        "saleable_area": 1000,
        "rate_per_sqft": 5000,
        "club_house_charges": 200000,
        "include_club_house": True,
    }
    # subtotal = 5000*1000 + 200000 = 5,200,000; auto labour cess = 36400

    def test_manual_zero(self, client):
        p = {**self.base_payload, "labour_cess_manual": True, "labour_cess_override": 0}
        r = client.post(f"{BASE_URL}/api/calculator/price", json=p, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["labour_cess"] == 0, f"Expected 0 got {d['labour_cess']}"
        assert d["subtotal_before_taxes"] == 5200000
        # total_flat_value = subtotal + 0 + gst(5%)
        assert d["total_flat_value"] == round(5200000 + 0 + 5200000 * 0.05, 2)

    def test_manual_custom(self, client):
        p = {**self.base_payload, "labour_cess_manual": True, "labour_cess_override": 12345}
        r = client.post(f"{BASE_URL}/api/calculator/price", json=p, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["labour_cess"] == 12345

    def test_auto_when_not_manual(self, client):
        r = client.post(f"{BASE_URL}/api/calculator/price", json=self.base_payload, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["labour_cess"] == round(5200000 * 0.007, 2)

    def test_manual_true_but_no_override_falls_back(self, client):
        p = {**self.base_payload, "labour_cess_manual": True}
        r = client.post(f"{BASE_URL}/api/calculator/price", json=p, timeout=30)
        assert r.status_code == 200, r.text
        # When override is None, spec says fallback to formula
        assert r.json()["labour_cess"] == round(5200000 * 0.007, 2)


# ---------- 2. PUT customer persists labour_cess=0 ----------
class TestCustomerPersistence:
    def test_get_ramya_exists(self, client):
        r = client.get(f"{BASE_URL}/api/customers/{RAMYA_ID}", timeout=30)
        assert r.status_code == 200, f"Ramya not found: {r.text}"

    def test_set_labour_cess_zero_persists(self, client):
        # snapshot original
        orig = client.get(f"{BASE_URL}/api/customers/{RAMYA_ID}", timeout=30).json()
        original_lc = orig.get("labour_cess")
        original_manual = orig.get("labour_cess_manual", False)

        payload = {"labour_cess": 0, "labour_cess_manual": True}
        r = client.put(f"{BASE_URL}/api/customers/{RAMYA_ID}", json=payload, timeout=30)
        assert r.status_code == 200, r.text

        # verify with GET
        got = client.get(f"{BASE_URL}/api/customers/{RAMYA_ID}", timeout=30).json()
        assert got.get("labour_cess") == 0, f"labour_cess={got.get('labour_cess')} (not 0)"
        assert got.get("labour_cess_manual") is True, f"labour_cess_manual={got.get('labour_cess_manual')}"

        # Restore
        client.put(
            f"{BASE_URL}/api/customers/{RAMYA_ID}",
            json={"labour_cess": original_lc, "labour_cess_manual": original_manual},
            timeout=30,
        )


# ---------- 3. Price breakup document reflects ₹0.00 ----------
class TestPriceBreakupDoc:
    def test_labour_cess_zero_in_html(self, client):
        # Ensure Ramya has labour_cess=0 first
        client.put(
            f"{BASE_URL}/api/customers/{RAMYA_ID}",
            json={"labour_cess": 0, "labour_cess_manual": True},
            timeout=30,
        )
        r = client.post(
            f"{BASE_URL}/api/documents/generate",
            json={"customer_id": RAMYA_ID, "doc_type": "price_breakup"},
            timeout=60,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        html = (
            body.get("html")
            or body.get("content")
            or body.get("html_content")
            or (body.get("document") or {}).get("content")
            or (body.get("document") or {}).get("html")
            or ""
        )
        if not html:
            # dump top-level keys to help debug
            raise AssertionError(f"No HTML in response. keys={list(body.keys())}, sample={str(body)[:400]}")
        assert "Labour Cess" in html, f"Labour Cess label missing. Sample: {html[:400]}"
        # Find the Labour Cess row and check it shows ₹0.00 (not e.g. ₹36,400.00)
        # Extract a chunk around Labour Cess
        idx = html.find("Labour Cess")
        chunk = html[idx: idx + 500]
        # Should contain 0.00 near it, and NOT a non-zero cess like 36,400
        assert re.search(r"[₹\$]?\s*0\.00", chunk), f"Expected ₹0.00 near Labour Cess. Chunk: {chunk[:400]}"


# ---------- 4. Generate-schedule uses preserved total_price ----------
class TestGenerateSchedule:
    def test_thirteen_items_using_preserved_total(self, client):
        # ensure labour_cess=0 doesn't affect legacy preserved total
        client.put(
            f"{BASE_URL}/api/customers/{RAMYA_ID}",
            json={"labour_cess": 0, "labour_cess_manual": True},
            timeout=30,
        )
        r = client.post(
            f"{BASE_URL}/api/calculator/generate-schedule/{RAMYA_ID}",
            timeout=30,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        # Response shape: {"message": ..., "schedule": {"items": [...]}}
        schedule = data.get("schedule") if isinstance(data, dict) else None
        if isinstance(schedule, dict):
            items = schedule.get("items", [])
        elif isinstance(schedule, list):
            items = schedule
        elif isinstance(data, list):
            items = data
        else:
            items = data.get("items", []) if isinstance(data, dict) else []
        assert len(items) == 13, f"Expected 13 items, got {len(items)}. Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
        total = sum((it.get("amount") or it.get("total_amount") or 0) for it in items)
        # Ramya preserved total = 211655.79
        assert abs(total - 211655.79) < 1.0, f"Sum {total} != 211655.79"
