"""Tests for Interior email — no attachments, CTA buttons embedded in HTML."""
import os
import urllib.parse

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")
ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASSWORD = "#RRLnew2026"
TEST_CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"


@pytest.fixture(scope="module")
def token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=20,
    )
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    body = r.json()
    return body.get("access_token") or body.get("token")


@pytest.fixture(scope="module")
def headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ===== Interior preview =====
class TestInteriorPreview:
    def test_preview_interior_email(self, headers):
        r = requests.get(
            f"{BASE_URL}/api/communication/preview-interior-email/{TEST_CUSTOMER_ID}",
            headers=headers,
            timeout=20,
        )
        assert r.status_code == 200, r.text
        d = r.json()

        # email_type
        assert d.get("email_type") == "interior"

        # No attachment_filename / attachment_static keys
        assert "attachment_filename" not in d, "attachment_filename leaked"
        assert "attachment_static" not in d, "attachment_static leaked"
        assert "attachment_html" not in d, "attachment_html leaked"

        # body must NOT mention 'brochure'
        body = d.get("body", "") or ""
        assert "brochure" not in body.lower(), "body still references brochure"
        assert "attached" not in body.lower() or "attached for your reference" not in body.lower()

        html = d.get("email_html", "") or ""
        # CTA buttons present (3 links + text labels)
        assert "Book a Design Consultation" in html
        assert "View Design Catalog" in html
        assert "Follow on Instagram" in html

        # Links — encoded variants also accepted
        assert "wa.me/919619995516" in html, "WhatsApp link missing"
        assert "designhive.in" in html, "Catalog link missing"
        assert "instagram.com/sunrise.designhive" in html, "Instagram link missing"

        # No cid: image refs
        assert "cid:" not in html, "cid: image ref present in interior email html"

    def test_preview_interior_subject(self, headers):
        r = requests.get(
            f"{BASE_URL}/api/communication/preview-interior-email/{TEST_CUSTOMER_ID}",
            headers=headers,
            timeout=20,
        )
        d = r.json()
        assert "Design Your New Home" in (d.get("subject") or "")


# ===== Send interior — verify no attachments path =====
class TestInteriorSend:
    def test_send_interior_email_no_attachments(self, headers):
        # Use admin email to avoid sending to real customer
        payload = {
            "email_type": "interior",
            "subject": "TEST_INTERIOR Subject",
            "body": "TEST body for interior — no PDF should be attached.",
            "recipient_email": "crm@rrlbuildersanddevelopers.com",
        }
        r = requests.post(
            f"{BASE_URL}/api/communication/send-document-email/{TEST_CUSTOMER_ID}",
            headers=headers,
            json=payload,
            timeout=60,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        # attachments must be empty for interior
        assert d.get("attachments") == [], f"expected no attachments, got {d.get('attachments')}"
        assert d.get("status") in ("sent", "simulated", "mocked (no API key)", "failed"), d


# ===== Regression on welcome / sales_agreement / allotment previews =====
class TestRegressionOtherEmails:
    def test_welcome_preview_still_has_3_attachments(self, headers):
        r = requests.get(
            f"{BASE_URL}/api/communication/preview-welcome-email/{TEST_CUSTOMER_ID}",
            headers=headers,
            timeout=20,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("email_type") == "welcome"
        assert d.get("attachment_filename")
        assert d.get("attachment_filename_2")
        assert d.get("attachment_filename_3")
        assert len(d.get("attachments", [])) == 3

    def test_sales_agreement_preview_has_2_attachments(self, headers):
        r = requests.get(
            f"{BASE_URL}/api/communication/preview-sales-agreement/{TEST_CUSTOMER_ID}",
            headers=headers,
            timeout=20,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("email_type") == "sales_agreement"
        assert d.get("attachment_filename")
        assert d.get("attachment_filename_2")

    def test_allotment_letter_preview_has_1_attachment(self, headers):
        r = requests.get(
            f"{BASE_URL}/api/communication/preview-allotment-letter/{TEST_CUSTOMER_ID}",
            headers=headers,
            timeout=20,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get("email_type") == "allotment_letter"
        assert d.get("attachment_filename")
