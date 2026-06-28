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

    def test_mobile_friendly_markers(self, headers):
        """Verify mobile-friendly markup: viewport meta, media query,
        big tel: link, WhatsApp button, and 3 stacked full-width CTAs."""
        r = requests.get(
            f"{BASE_URL}/api/communication/preview-interior-email/{TEST_CUSTOMER_ID}",
            headers=headers,
            timeout=20,
        )
        assert r.status_code == 200, r.text
        html = r.json().get("email_html") or ""

        # 1) viewport meta tag for mobile email clients
        assert 'name="viewport"' in html, "viewport meta tag missing"
        assert "width=device-width" in html, "viewport width missing"
        assert "initial-scale=1.0" in html, "viewport initial-scale missing"

        # 2) Mobile media query in base template
        assert "@media only screen and (max-width: 600px)" in html, \
            "mobile media query missing"

        # 3) Prominent tel: link to +91 96199 95516 with 26px font
        assert 'href="tel:+919619995516"' in html, "tel: link missing or wrong"
        assert "font-size: 26px" in html, "26px phone font missing"

        # 4) WhatsApp chat button text
        assert "Chat on WhatsApp" in html, "Chat on WhatsApp button text missing"

        # 5) wa.me link with the encoded prefilled message
        assert "I%27d%20like%20to%20schedule" in html, \
            "encoded prefilled WhatsApp message missing"

        # 6) Three stacked full-width CTAs — display: block appears at least
        #    3 times (phone tel anchor + 3 stacked CTA anchors = 4+).
        display_block_count = html.count("display: block")
        assert display_block_count >= 4, (
            f"expected >=4 'display: block' occurrences for stacked CTAs + tel anchor, "
            f"got {display_block_count}"
        )

        # 7) Confirm the three CTA labels still present (regression)
        assert "Book a Design Consultation" in html
        assert "View Design Catalog" in html
        assert "Follow on Instagram" in html

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
        # Welcome now has 4 attachments (added in iteration 45 — Total Registration Charges)
        assert len(d.get("attachments", [])) == 4

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

    def test_base_document_email_has_viewport_meta(self, headers):
        """Regression: generate_document_email_html now contains the
        viewport meta + mobile media query — verify it didn't break other
        email types' render."""
        # Sales agreement uses the base document template
        r = requests.get(
            f"{BASE_URL}/api/communication/preview-sales-agreement/{TEST_CUSTOMER_ID}",
            headers=headers,
            timeout=20,
        )
        assert r.status_code == 200
        html = r.json().get("email_html") or ""
        assert 'name="viewport"' in html, "viewport meta missing from sales email"
        assert "@media only screen and (max-width: 600px)" in html, \
            "mobile media query missing from sales email"

        # Allotment letter also uses the base document template
        r2 = requests.get(
            f"{BASE_URL}/api/communication/preview-allotment-letter/{TEST_CUSTOMER_ID}",
            headers=headers,
            timeout=20,
        )
        html2 = r2.json().get("email_html") or ""
        assert 'name="viewport"' in html2, "viewport meta missing from allotment email"
