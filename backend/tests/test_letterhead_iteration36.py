"""
Iteration 36 — Letterhead verification across ALL document types.

Validates the recent NOC letterhead fix did not regress any other doc_type:
  - All 10 doc_types must contain RRL logo base64 prefix + company name.
  - NOC docs (HDFC/BOB/TATA) must additionally contain `<div class="letterhead"`
    and the gold border marker `#D4AF37`.
  - Each doc must download as a valid PDF (>50KB, starts with %PDF-).
  - Customer.interest_amount is persisted via PUT /api/customers/{id}
    and reflected as "Interest Amount" row in price_breakup HTML.
"""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://builder-crm-dev.preview.emergentagent.com").rstrip("/")
ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASS = "#RRLnew2026"
TEST_CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"  # Ramya test lead

LOGO_PREFIX = "data:image/png;base64,iVBOR"
COMPANY_NAME = "RRL Builders and Developers"
LETTERHEAD_MARK = '<div class="letterhead"'
GOLD_MARK = "#D4AF37"

ALL_DOC_TYPES = [
    "sales_agreement",
    "allotment_letter",
    "price_breakup",
    "cost_breakup",
    "demand_letter",
    "payment_schedule",
    "noc_hdfc",
    "noc_bob",
    "noc_tata",
    "payment_receipt",  # needs transaction_id
]
NOC_TYPES = {"noc_hdfc", "noc_bob", "noc_tata"}

RESULTS = []  # collected for the final report row


# ---------- fixtures ----------
@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"email": ADMIN_EMAIL, "password": ADMIN_PASS},
                      timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text[:200]}"
    return r.json()["access_token"] if "access_token" in r.json() else r.json().get("token")


@pytest.fixture(scope="module")
def client(token):
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def transaction_id(client):
    """Fetch a transaction id for payment_receipt, or None if customer has none."""
    r = client.get(f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}", timeout=30)
    if r.status_code != 200:
        return None
    txns = r.json()
    if isinstance(txns, dict):
        txns = txns.get("transactions") or txns.get("data") or []
    if not txns:
        return None
    return txns[0].get("id")


# ---------- helpers ----------
def _generate(client, doc_type, custom_fields=None):
    body = {"customer_id": TEST_CUSTOMER_ID, "doc_type": doc_type,
            "custom_fields": custom_fields or {}}
    return client.post(f"{BASE_URL}/api/documents/generate", json=body, timeout=60)


def _pdf(client, doc_id):
    return client.get(f"{BASE_URL}/api/documents/pdf/{doc_id}", timeout=120)


# ---------- core letterhead test, parameterised over all doc types ----------
@pytest.mark.parametrize("doc_type", ALL_DOC_TYPES)
def test_doc_has_letterhead_and_valid_pdf(client, transaction_id, doc_type):
    custom_fields = {}
    if doc_type == "payment_receipt":
        if not transaction_id:
            pytest.skip("Customer has no transactions; cannot test payment_receipt")
        custom_fields = {"transaction_id": transaction_id}

    r = _generate(client, doc_type, custom_fields)
    assert r.status_code == 200, f"{doc_type} generate failed: {r.status_code} {r.text[:300]}"
    payload = r.json()
    doc = payload.get("document") or payload
    html = doc.get("content", "")
    doc_id = doc.get("id")
    assert doc_id, f"{doc_type}: no doc_id returned"
    assert html, f"{doc_type}: empty HTML"

    has_logo = LOGO_PREFIX in html
    # case-insensitive: some templates uppercase the company name (e.g. payment_receipt)
    has_company = COMPANY_NAME.lower() in html.lower()

    # PDF
    p = _pdf(client, doc_id)
    pdf_ok = p.status_code == 200 and p.content.startswith(b"%PDF-")
    pdf_size = len(p.content) if p.status_code == 200 else 0
    pdf_size_ok = pdf_size > 50_000

    row = {
        "doc_type": doc_type,
        "has_logo": "Y" if has_logo else "N",
        "has_company_name": "Y" if has_company else "N",
        "html_size": len(html),
        "pdf_size": pdf_size,
        "pdf_valid": "Y" if (pdf_ok and pdf_size_ok) else "N",
    }
    if doc_type in NOC_TYPES:
        row["has_letterhead_div"] = "Y" if LETTERHEAD_MARK in html else "N"
        row["has_gold_border"] = "Y" if GOLD_MARK in html else "N"
    RESULTS.append(row)

    # assertions
    assert has_logo, f"{doc_type}: RRL logo base64 missing"
    assert has_company, f"{doc_type}: company name '{COMPANY_NAME}' missing"
    assert pdf_ok, f"{doc_type}: PDF invalid (status={p.status_code}, head={p.content[:8]!r})"
    assert pdf_size_ok, f"{doc_type}: PDF too small ({pdf_size} bytes)"
    if doc_type in NOC_TYPES:
        assert LETTERHEAD_MARK in html, f"{doc_type}: missing <div class='letterhead'>"
        assert GOLD_MARK in html, f"{doc_type}: missing gold border #D4AF37"


# ---------- payment_schedule auto-generate fix ----------
def test_payment_schedule_autogenerate(client):
    """If schedule is missing, endpoint should auto-build the 13 default milestones."""
    r = _generate(client, "payment_schedule")
    assert r.status_code == 200, r.text[:300]
    html = (r.json().get("document") or r.json()).get("content", "")
    # The default schedule has 13 milestones; HTML should be non-trivial.
    assert len(html) > 3000, f"payment_schedule HTML suspiciously small: {len(html)}"


# ---------- interest_amount persistence + price_breakup ----------
def test_interest_amount_persists_and_renders(client):
    # Read current customer to restore later
    cur = client.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}", timeout=30)
    assert cur.status_code == 200, cur.text[:200]
    original = cur.json().get("interest_amount", 0)

    try:
        upd = client.put(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}",
                         json={"interest_amount": 75000}, timeout=30)
        assert upd.status_code in (200, 204), f"PUT failed: {upd.status_code} {upd.text[:200]}"

        get_after = client.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}", timeout=30)
        assert get_after.status_code == 200
        assert get_after.json().get("interest_amount") == 75000, \
            f"interest_amount not persisted, got {get_after.json().get('interest_amount')}"

        # Generate price_breakup and check Interest Amount row
        r = _generate(client, "price_breakup")
        assert r.status_code == 200, r.text[:300]
        html = (r.json().get("document") or r.json()).get("content", "")
        assert re.search(r"Interest\s+Amount", html, re.I), \
            "price_breakup HTML does not contain 'Interest Amount' row"
    finally:
        # restore
        client.put(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}",
                   json={"interest_amount": original or 0}, timeout=30)


# ---------- final summary table ----------
def test_zz_print_summary():
    print("\n\n=== LETTERHEAD VERIFICATION SUMMARY ===")
    if not RESULTS:
        print("(no rows collected)")
        return
    hdr = ["doc_type", "has_logo", "has_company_name", "html_size", "pdf_size", "pdf_valid",
           "has_letterhead_div", "has_gold_border"]
    print("| " + " | ".join(hdr) + " |")
    print("|" + "|".join(["---"] * len(hdr)) + "|")
    for row in RESULTS:
        line = [str(row.get(k, "-")) for k in hdr]
        flag = " <-- FAIL" if "N" in (row.get("has_logo"), row.get("has_company_name"),
                                       row.get("pdf_valid"),
                                       row.get("has_letterhead_div", "Y"),
                                       row.get("has_gold_border", "Y")) else ""
        print("| " + " | ".join(line) + " |" + flag)
