"""
Tests for the new Payment Receipt feature (iteration 32).
Covers:
  - POST /api/transactions/{customer_id} auto-assigns PAR-XXX receipt_number
  - POST /api/documents/payment-receipt/{cid}/{txid} returns id+content+receipt_number
  - HTML contains all required fragments
  - GET /api/documents/pdf/{doc_id} returns PDF bytes
  - PUT /api/documents/html/{doc_id} edit allowed for admin, blocked for accounts
  - /api/payments/overview still works (regression for re-linked PaymentsPage)
  - Existing receipt is reused for same transaction (no duplicates)
  - Backfill of receipt_number for legacy transactions
"""
import os
import pytest
import requests

# Read from frontend/.env since pytest runs from backend cwd
def _read_backend_url():
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if url:
        return url.rstrip("/")
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    return line.split("=", 1)[1].strip().rstrip("/")
    except Exception:
        pass
    raise RuntimeError("REACT_APP_BACKEND_URL not found")

BASE_URL = _read_backend_url()
ADMIN = {"email": "crm@rrlbuildersanddevelopers.com", "password": "#RRLnew2026"}
ACCOUNTS = {"email": "accounts@rrlbuilders.com", "password": "accounts123"}
CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"  # Ramya test lead


def _login(creds):
    r = requests.post(f"{BASE_URL}/api/auth/login", json=creds, timeout=15)
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    return r.json().get("access_token") or r.json()["token"]


@pytest.fixture(scope="module")
def admin_token():
    return _login(ADMIN)


@pytest.fixture(scope="module")
def accounts_token():
    return _login(ACCOUNTS)


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def accounts_headers(accounts_token):
    return {"Authorization": f"Bearer {accounts_token}", "Content-Type": "application/json"}


# --- created resources for cleanup ---
_created_txn_ids = []
_created_doc_ids = []


@pytest.fixture(scope="module", autouse=True)
def cleanup(admin_headers):
    yield
    for did in _created_doc_ids:
        try:
            requests.delete(f"{BASE_URL}/api/documents/{did}", headers=admin_headers, timeout=10)
        except Exception:
            pass
    for tid in _created_txn_ids:
        try:
            requests.delete(
                f"{BASE_URL}/api/transactions/{CUSTOMER_ID}/{tid}",
                headers=admin_headers, timeout=10
            )
        except Exception:
            pass


# ---- Tests ----

def test_create_transaction_assigns_receipt_number(admin_headers):
    payload = {
        "transaction_stage": "booking",
        "transaction_date": "2026-01-15",
        "bank_name": "TEST_BANK",
        "transaction_number": "TEST_TXN_001",
        "amount": 12345.0,
        "notes": "TEST_receipt_assign"
    }
    r = requests.post(
        f"{BASE_URL}/api/transactions/{CUSTOMER_ID}",
        json=payload, headers=admin_headers, timeout=15
    )
    assert r.status_code in (200, 201), r.text
    data = r.json()
    txn = data.get("transaction", {})
    assert "receipt_number" in txn and txn["receipt_number"], "receipt_number missing"
    assert txn["receipt_number"].startswith("PAR-"), f"unexpected format: {txn['receipt_number']}"
    assert len(txn["receipt_number"].split("-")[1]) >= 3
    _created_txn_ids.append(txn["id"])


def test_generate_payment_receipt_returns_full_payload(admin_headers):
    assert _created_txn_ids, "previous test must have created a txn"
    tid = _created_txn_ids[-1]
    r = requests.post(
        f"{BASE_URL}/api/documents/payment-receipt/{CUSTOMER_ID}/{tid}",
        headers=admin_headers, timeout=20
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("id"), "doc id missing"
    assert body.get("doc_type") == "payment_receipt"
    assert body.get("receipt_number", "").startswith("PAR-")
    content = body.get("content", "")
    # Required fragments
    expected = [
        "RRL BUILDERS AND DEVELOPERS PVT. LTD.",
        "www.rrlbuildersanddevelopers.com",
        "PAR-",
        "Received with thanks from",
        "A sum of Rupees",
        "Palm Altezze",
        "AUTHORISED SIGNATURE",
        "Cheque",
        "subject to realisation",
    ]
    missing = [s for s in expected if s not in content]
    assert not missing, f"missing fragments: {missing}"
    _created_doc_ids.append(body["id"])


def test_generate_payment_receipt_reuses_existing(admin_headers):
    tid = _created_txn_ids[-1]
    first_id = _created_doc_ids[-1]
    r = requests.post(
        f"{BASE_URL}/api/documents/payment-receipt/{CUSTOMER_ID}/{tid}",
        headers=admin_headers, timeout=20
    )
    assert r.status_code == 200
    assert r.json().get("id") == first_id, "Should reuse existing receipt doc"


def test_pdf_download_works(admin_headers):
    did = _created_doc_ids[-1]
    r = requests.get(
        f"{BASE_URL}/api/documents/pdf/{did}",
        headers={"Authorization": admin_headers["Authorization"]},
        timeout=30
    )
    assert r.status_code == 200, r.text[:300]
    assert r.headers.get("content-type", "").startswith("application/pdf")
    assert r.content[:4] == b"%PDF", "not a valid PDF"
    assert len(r.content) > 5000


def test_admin_can_edit_receipt(admin_headers):
    did = _created_doc_ids[-1]
    # Get current
    g = requests.get(f"{BASE_URL}/api/documents/html/{did}", headers=admin_headers, timeout=10)
    assert g.status_code == 200
    original = g.json()["content"]
    new = original + "<!-- TEST_EDIT_MARKER -->"
    p = requests.put(
        f"{BASE_URL}/api/documents/html/{did}",
        json={"content": new}, headers=admin_headers, timeout=10
    )
    assert p.status_code == 200, p.text
    g2 = requests.get(f"{BASE_URL}/api/documents/html/{did}", headers=admin_headers, timeout=10)
    assert "TEST_EDIT_MARKER" in g2.json()["content"]


def test_accounts_cannot_edit_receipt_but_can_generate(accounts_headers):
    # Accounts SHOULD be able to generate (per spec)
    tid = _created_txn_ids[-1]
    rgen = requests.post(
        f"{BASE_URL}/api/documents/payment-receipt/{CUSTOMER_ID}/{tid}",
        headers=accounts_headers, timeout=20
    )
    assert rgen.status_code == 200, f"Accounts should be able to generate: {rgen.text}"
    did = rgen.json()["id"]
    # But editing should be forbidden
    p = requests.put(
        f"{BASE_URL}/api/documents/html/{did}",
        json={"content": "<html>blocked</html>"},
        headers=accounts_headers, timeout=10
    )
    assert p.status_code == 403, f"expected 403, got {p.status_code} {p.text}"


def test_payments_overview_endpoint(admin_headers):
    r = requests.get(f"{BASE_URL}/api/payments/overview", headers=admin_headers, timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    for k in ("pending", "overdue", "upcoming"):
        assert k in body and isinstance(body[k], list)


def test_transactions_list_includes_receipt_number(admin_headers):
    r = requests.get(f"{BASE_URL}/api/transactions/{CUSTOMER_ID}", headers=admin_headers, timeout=10)
    assert r.status_code == 200
    txns = r.json()
    assert isinstance(txns, list) and len(txns) > 0
    # At least the newly created should have receipt_number
    found = [t for t in txns if t.get("id") in _created_txn_ids]
    assert all(t.get("receipt_number", "").startswith("PAR-") for t in found)


def test_backfill_receipt_for_legacy_txn(admin_headers):
    """If any transaction without receipt_number exists, generating receipt should backfill."""
    r = requests.get(f"{BASE_URL}/api/transactions/{CUSTOMER_ID}", headers=admin_headers, timeout=10)
    assert r.status_code == 200
    txns = r.json()
    legacy = [t for t in txns if not t.get("receipt_number")]
    if not legacy:
        pytest.skip("No legacy txn without receipt_number to backfill (expected by spec context).")
    tid = legacy[0]["id"]
    gen = requests.post(
        f"{BASE_URL}/api/documents/payment-receipt/{CUSTOMER_ID}/{tid}",
        headers=admin_headers, timeout=20
    )
    assert gen.status_code == 200
    assert gen.json().get("receipt_number", "").startswith("PAR-")
    _created_doc_ids.append(gen.json()["id"])
