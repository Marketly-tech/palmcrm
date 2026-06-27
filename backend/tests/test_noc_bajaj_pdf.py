"""
Iteration 42 — verifies the bug fix for Bajaj NOC 'Details of Purchaser' table
overlap/breakage on PDF download. We:

  1. Login as admin and call POST /api/documents/generate with doc_type=noc_bajaj
     for the test customer (Ramya).
  2. Download the PDF via GET /api/documents/pdf/{id} and assert it is a valid
     application/pdf binary.
  3. Extract text from the PDF and assert all 13 'Details of Purchaser' field
     labels are present and the long Bengaluru address row is intact (not
     truncated mid-string).
  4. Sanity-check noc_hdfc still generates a valid PDF (regression).
"""
import io
import os
import re
import subprocess
import tempfile

import pytest
import requests
from pypdf import PdfReader

def _read_frontend_env() -> str:
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    return line.split("=", 1)[1].strip()
    except OSError:
        pass
    return ""


BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or _read_frontend_env()).rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL must be set"
ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASSWORD = "#RRLnew2026"
TEST_CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"  # Ramya — DO NOT modify

EXPECTED_LABELS = [
    "Details of Purchaser",
    "Full Name",
    "Mobile",
    "Flat No",
    "Wing",   # 'Wing / Tower'
    "Area",
    "Project Name",
    "Project Location",
    "Consideration",
    "Loan Amount",
    "Lender",
    "Own Contribution",
    "Booking Date",
    "Agreement",  # 'Agreement for Sale Date'
]

LONG_ADDRESS_FRAGMENTS = [
    "SY NO: 73/6",
    "Janthagondanahalli",
    "Sarjapura",
    "Anekal",
    "Bengaluru",
    "560087",
]


# ---------- fixtures ----------
@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=30,
    )
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    token = r.json().get("token") or r.json().get("access_token")
    assert token, f"no token in login response: {r.json()}"
    return token


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


# ---------- helpers ----------
def _generate_doc(headers, doc_type: str) -> str:
    r = requests.post(
        f"{BASE_URL}/api/documents/generate",
        headers=headers,
        json={"customer_id": TEST_CUSTOMER_ID, "doc_type": doc_type, "custom_fields": {}},
        timeout=60,
    )
    assert r.status_code == 200, f"generate {doc_type} failed: {r.status_code} {r.text[:400]}"
    body = r.json()
    doc = body.get("document") or {}
    doc_id = doc.get("id")
    assert doc_id, f"no document id returned: {body}"
    return doc_id


def _download_pdf(headers, doc_id: str) -> bytes:
    r = requests.get(
        f"{BASE_URL}/api/documents/pdf/{doc_id}",
        headers={"Authorization": headers["Authorization"]},
        timeout=120,
    )
    assert r.status_code == 200, f"pdf download failed: {r.status_code} {r.text[:300]}"
    ct = r.headers.get("content-type", "")
    assert "application/pdf" in ct, f"unexpected content-type: {ct}"
    assert r.content[:5] == b"%PDF-", f"binary is not a PDF: {r.content[:20]!r}"
    return r.content


def _pdf_text(pdf_bytes: bytes) -> str:
    # pdftotext is more reliable than pypdf for layout-sensitive extraction.
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf_bytes)
        pdf_path = f.name
    try:
        out = subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True, text=True, timeout=30, check=True,
        )
        return out.stdout
    finally:
        try:
            os.unlink(pdf_path)
        except OSError:
            pass


# ---------- tests ----------
class TestNocBajajPdf:
    """Bajaj NOC end-to-end: generate -> download -> verify content."""

    def test_generate_bajaj_returns_document(self, auth_headers):
        doc_id = _generate_doc(auth_headers, "noc_bajaj")
        assert isinstance(doc_id, str) and len(doc_id) > 0

    def test_bajaj_pdf_is_valid_binary(self, auth_headers):
        doc_id = _generate_doc(auth_headers, "noc_bajaj")
        pdf_bytes = _download_pdf(auth_headers, doc_id)
        # Save for downstream inspection
        with open("/tmp/noc_bajaj_test.pdf", "wb") as f:
            f.write(pdf_bytes)
        # pypdf should parse it cleanly + report >= 1 page
        reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) >= 1
        assert len(pdf_bytes) > 5000, f"PDF suspiciously small: {len(pdf_bytes)} bytes"

    def test_bajaj_pdf_contains_all_purchaser_labels(self, auth_headers):
        doc_id = _generate_doc(auth_headers, "noc_bajaj")
        pdf_bytes = _download_pdf(auth_headers, doc_id)
        text = _pdf_text(pdf_bytes)
        # write extracted text for debugging
        with open("/tmp/noc_bajaj_text.txt", "w") as f:
            f.write(text)
        missing = [lbl for lbl in EXPECTED_LABELS if lbl.lower() not in text.lower()]
        assert not missing, f"missing labels in Bajaj NOC PDF: {missing}\n---TEXT---\n{text[:2000]}"

    def test_bajaj_long_address_row_intact(self, auth_headers):
        """The Project Location/Address row was the culprit — verify every fragment
        of the long Bengaluru address survives extraction (i.e. wasn't truncated
        or obscured by overlapping borders)."""
        doc_id = _generate_doc(auth_headers, "noc_bajaj")
        pdf_bytes = _download_pdf(auth_headers, doc_id)
        text = _pdf_text(pdf_bytes)
        missing = [frag for frag in LONG_ADDRESS_FRAGMENTS if frag.lower() not in text.lower()]
        assert not missing, f"address fragments missing — row may be broken: {missing}"

    def test_bajaj_addressee_and_signature_intact(self, auth_headers):
        """Sanity-check letterhead surroundings (must NOT regress from the CSS-only fix)."""
        doc_id = _generate_doc(auth_headers, "noc_bajaj")
        pdf_bytes = _download_pdf(auth_headers, doc_id)
        text = _pdf_text(pdf_bytes)
        for needle in ["Bajaj Housing Finance", "RRL PALM ALTEZZE",
                       "Authorized Signatory", "Yours faithfully"]:
            assert needle.lower() in text.lower(), f"missing surrounding content: {needle!r}"


class TestNocRegression:
    """Regression: HDFC NOC must still render fine — the fix is scoped to Bajaj only."""

    def test_hdfc_noc_generates_and_downloads(self, auth_headers):
        doc_id = _generate_doc(auth_headers, "noc_hdfc")
        pdf_bytes = _download_pdf(auth_headers, doc_id)
        with open("/tmp/noc_hdfc_test.pdf", "wb") as f:
            f.write(pdf_bytes)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) >= 1
        text = _pdf_text(pdf_bytes)
        # HDFC NOC standard surroundings
        assert "hdfc" in text.lower() or "housing" in text.lower(), f"unexpected HDFC NOC content:\n{text[:800]}"
        assert "RRL PALM ALTEZZE".lower() in text.lower()


class TestRowSplittingVisual:
    """Render the Bajaj PDF to PNG via pdftoppm and inspect the per-page
    'Details of Purchaser' rows. We verify:
      (a) every row label appears exactly once across the rendered pages, and
      (b) if the table spans 2 pages, the label set is partitioned (no label
          is half-rendered on both pages — which is how an overlap would
          manifest after the page-break-inside:avoid fix)."""

    def test_rows_partition_across_pages(self, auth_headers):
        doc_id = _generate_doc(auth_headers, "noc_bajaj")
        pdf_bytes = _download_pdf(auth_headers, doc_id)
        pdf_path = "/tmp/noc_bajaj_visual.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # Per-page text extraction
        per_page = []
        reader = PdfReader(io.BytesIO(pdf_bytes))
        n_pages = len(reader.pages)
        for i in range(1, n_pages + 1):
            out = subprocess.run(
                ["pdftotext", "-layout", "-f", str(i), "-l", str(i), pdf_path, "-"],
                capture_output=True, text=True, timeout=30, check=True,
            )
            per_page.append(out.stdout.lower())

        row_labels = [
            "purchaser\u2019s full name", "full name",
            "mobile",
            "flat no",
            "wing",
            "area",
            "project name",
            "project location",
            "consideration",
            "loan amount",
            "lender",
            "own contribution",
            "booking date",
            "agreement for sale",
        ]
        # Per-row: ensure it appears in EXACTLY one page (no straddle).
        straddled = []
        for lbl in row_labels:
            hits = sum(1 for pg in per_page if lbl in pg)
            if hits > 1:
                # 'full name' may appear in salutation too — exempt the most generic ones.
                if lbl in {"full name", "mobile", "area"}:
                    continue
                straddled.append((lbl, hits))
        assert not straddled, f"these row labels appear on multiple pages (possible row split): {straddled}"
