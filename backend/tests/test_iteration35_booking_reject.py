"""
Iteration 35: Tests for booking form co-applicant gender and Lead Reject endpoint.
- Backend: BookingFormData accepts co_applicant_gender + co_applicant_date_of_birth
- Backend: PUT /api/leads/{id}/reject deletes lead, releases unit, deletes checklist
- Backend: Reject accepts optional reason query param
- 404 for nonexistent lead reject
"""
import os
import uuid
import pytest
import requests

def _load_backend_url():
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if not url:
        # Fallback: read from frontend/.env
        env_path = "/app/frontend/.env"
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("REACT_APP_BACKEND_URL="):
                        url = line.split("=", 1)[1].strip()
                        break
    if not url:
        raise RuntimeError("REACT_APP_BACKEND_URL not configured")
    return url.rstrip("/")


BASE_URL = _load_backend_url()
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASSWORD = "#RRLnew2026"


@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="module")
def available_unit(auth_headers):
    """Find an available unit; create a synthetic one if DB has none."""
    r = requests.get(f"{API}/units", headers=auth_headers)
    units = r.json() if r.status_code == 200 else []
    available = [u for u in units if u.get("is_available")]
    if available:
        return available[0]
    # Try to create a test unit via admin API
    test_unit = {
        "project": "RRL Palm Altezze",
        "tower": "T-TEST",
        "unit_number": f"TST-{str(uuid.uuid4())[:6]}",
        "bhk_type": "2BHK",
        "floor": 1,
        "saleable_area": 1000,
        "rate_per_sqft": 6600,
        "is_available": True,
    }
    cr = requests.post(f"{API}/units", json=test_unit, headers=auth_headers)
    if cr.status_code in [200, 201]:
        # return the unit; may need id back
        body = cr.json() if cr.text else test_unit
        if isinstance(body, dict):
            return {**test_unit, **body}
        return test_unit
    # Fall back: return synthetic dict; booking submit handles missing unit
    return test_unit


# --- BOOKING FORM TESTS ---

def _make_booking_payload(unit, suffix=""):
    return {
        "name": f"TEST_Reject_Lead_{suffix}",
        "phone": "9999999999",
        "email": f"test_reject_{suffix}@example.com",
        "father_name": "Test Father",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "pan_number": "ABCDE1234F",
        "aadhar_number": "123456789012",
        "address": "Test Address",
        "nationality": "Indian",
        # Co-applicant with NEW fields
        "co_applicant_name": "TEST_CoApp",
        "co_applicant_father_name": "Co Father",
        "co_applicant_gender": "spouse",
        "co_applicant_date_of_birth": "1992-05-15",
        "co_applicant_phone": "8888888888",
        "co_applicant_email": f"co_{suffix}@example.com",
        "co_applicant_pan": "FGHIJ5678K",
        "co_applicant_aadhar": "987654321098",
        "co_applicant_address": "Co Address",
        "co_applicant_nationality": "Indian",
        "project": unit["project"],
        "tower": unit["tower"],
        "unit_number": unit["unit_number"],
        "bhk_type": unit.get("bhk_type", "2BHK"),
        "floor": unit.get("floor", 1),
        "saleable_area": unit.get("saleable_area", 1000),
        "rate_per_sqft": unit.get("rate_per_sqft", 6600),
        "floor_rise_cost": 0,
        "parking": "1",
        "additional_parking": 0,
        "booking_amount": 100000,
        "transaction_date": "2026-01-15",
        "finance_type": "self",
    }


class TestBookingCoApplicantFields:
    """Booking form persists co_applicant_gender + co_applicant_date_of_birth."""

    def test_submit_booking_with_co_app_gender_and_dob(self, auth_headers, available_unit):
        payload = _make_booking_payload(available_unit, suffix=str(uuid.uuid4())[:8])
        r = requests.post(f"{API}/public/booking-form", json=payload)
        assert r.status_code == 200, f"Booking submit failed: {r.text}"
        data = r.json()
        assert "reference_id" in data
        ref_id = data["reference_id"]

        # GET customer to verify persistence
        cust_r = requests.get(f"{API}/customers/{ref_id}", headers=auth_headers)
        assert cust_r.status_code == 200, cust_r.text
        cust = cust_r.json()
        assert cust["co_applicant_gender"] == "spouse"
        assert cust["co_applicant_date_of_birth"] == "1992-05-15"
        assert cust["co_applicant_name"] == "TEST_CoApp"

        # Cleanup: reject this lead
        requests.put(f"{API}/leads/{ref_id}/reject", headers=auth_headers, params={"reason": "test cleanup"})

    def test_submit_booking_with_co_app_gender_female(self, auth_headers, available_unit):
        # re-fetch available units since prior test may have consumed one (but cleanup rejected it)
        payload = _make_booking_payload(available_unit, suffix=str(uuid.uuid4())[:8])
        payload["co_applicant_gender"] = "female"
        payload["co_applicant_date_of_birth"] = "1993-03-20"
        r = requests.post(f"{API}/public/booking-form", json=payload)
        assert r.status_code == 200, r.text
        ref_id = r.json()["reference_id"]
        cust = requests.get(f"{API}/customers/{ref_id}", headers=auth_headers).json()
        assert cust["co_applicant_gender"] == "female"
        assert cust["co_applicant_date_of_birth"] == "1993-03-20"
        # Cleanup
        requests.put(f"{API}/leads/{ref_id}/reject", headers=auth_headers)


# --- LEAD REJECT TESTS ---

class TestRejectLead:
    """PUT /api/leads/{id}/reject behavior."""

    def test_reject_nonexistent_lead_returns_404(self, auth_headers):
        fake_id = str(uuid.uuid4())
        r = requests.put(f"{API}/leads/{fake_id}/reject", headers=auth_headers)
        assert r.status_code == 404, r.text

    def test_reject_unauthorized_returns_401_or_403(self):
        fake_id = str(uuid.uuid4())
        r = requests.put(f"{API}/leads/{fake_id}/reject")
        assert r.status_code in [401, 403], r.status_code

    def test_reject_lead_full_flow(self, auth_headers, available_unit):
        # Step 1: create a booking
        payload = _make_booking_payload(available_unit, suffix=str(uuid.uuid4())[:8])
        booking_r = requests.post(f"{API}/public/booking-form", json=payload)
        assert booking_r.status_code == 200, booking_r.text
        ref_id = booking_r.json()["reference_id"]

        # Verify the lead exists, unit is unavailable
        cust_r = requests.get(f"{API}/customers/{ref_id}", headers=auth_headers)
        assert cust_r.status_code == 200

        units_r = requests.get(f"{API}/units", headers=auth_headers)
        unit_after_booking = next(
            (u for u in units_r.json()
             if u["project"] == payload["project"]
             and u["tower"] == payload["tower"]
             and u["unit_number"] == payload["unit_number"]),
            None
        )
        assert unit_after_booking is not None
        assert unit_after_booking["is_available"] is False, "Unit should be unavailable after booking"

        # Step 2: Reject with reason
        rej_r = requests.put(
            f"{API}/leads/{ref_id}/reject",
            headers=auth_headers,
            params={"reason": "Duplicate"}
        )
        assert rej_r.status_code == 200, rej_r.text
        body = rej_r.json()
        assert "message" in body

        # Step 3: Customer should no longer exist
        cust_after = requests.get(f"{API}/customers/{ref_id}", headers=auth_headers)
        assert cust_after.status_code == 404

        # Step 4: Unit should be available again
        units_r2 = requests.get(f"{API}/units", headers=auth_headers)
        unit_after_reject = next(
            (u for u in units_r2.json()
             if u["project"] == payload["project"]
             and u["tower"] == payload["tower"]
             and u["unit_number"] == payload["unit_number"]),
            None
        )
        assert unit_after_reject is not None
        assert unit_after_reject["is_available"] is True, "Unit should be available after reject"

    def test_reject_lead_without_reason(self, auth_headers, available_unit):
        payload = _make_booking_payload(available_unit, suffix=str(uuid.uuid4())[:8])
        booking_r = requests.post(f"{API}/public/booking-form", json=payload)
        assert booking_r.status_code == 200
        ref_id = booking_r.json()["reference_id"]

        # Reject without reason
        rej_r = requests.put(f"{API}/leads/{ref_id}/reject", headers=auth_headers)
        assert rej_r.status_code == 200, rej_r.text
