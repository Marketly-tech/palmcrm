"""
Tests for POST /api/calculator/generate-schedule/{customer_id} fix.

Covers:
- Ramya (booking_date=2026-03-30) → 13 items with correct due_dates.
- Percentages sum to 100; cumulative accumulates correctly.
- Fallback to today when booking_date is null/missing/malformed.
- Booking date parser accepts YYYY-MM-DD and YYYY-MM-DDTHH:MM:SS variants.
- GET /api/calculator/payment-schedule-template still exposes days_offset.

Author: T1 (iteration_51).
"""
import os
import pytest
import requests
from datetime import date, datetime, timedelta, timezone

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASSWORD = "#RRLnew2026"
RAMYA_UUID = "6d902613-5106-4294-bc3e-b907f85127f7"

EXPECTED_STAGES = [
    ("booking", 10, 10),
    ("agreement", 10, 30),
    ("foundation", 10, 90),
    ("podium", 10, 180),
    ("2nd_floor", 5, 240),
    ("6th_floor", 5, 360),
    ("10th_floor", 5, 480),
    ("14th_floor", 5, 600),
    ("18th_floor", 5, 720),
    ("22nd_floor", 5, 840),
    ("top_roof", 10, 960),
    ("flooring", 10, 1080),
    ("handover", 10, 1200),
]


# ---------- Fixtures ---------- #
@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
    })
    if r.status_code != 200:
        pytest.skip(f"Admin login failed: {r.status_code} - {r.text}")
    return r.json().get("access_token")


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="module")
def ramya_original_booking_date(auth_headers):
    """Snapshot Ramya's booking_date so we can restore it after fallback test."""
    r = requests.get(f"{BASE_URL}/api/customers/{RAMYA_UUID}", headers=auth_headers)
    assert r.status_code == 200, f"Could not fetch Ramya: {r.status_code} {r.text}"
    return r.json().get("booking_date")


# ---------- Feature: correct due_dates for Ramya ---------- #
class TestGenerateScheduleForRamya:
    def test_ensure_ramya_booking_date_matches(self, auth_headers, ramya_original_booking_date):
        """Ensure Ramya's booking_date is 2026-03-30 (or set it if not)."""
        if not ramya_original_booking_date or "2026-03-30" not in ramya_original_booking_date:
            # Try to update via customers PUT
            r = requests.put(
                f"{BASE_URL}/api/customers/{RAMYA_UUID}",
                headers=auth_headers,
                json={"booking_date": "2026-03-30"},
            )
            assert r.status_code == 200, f"Cannot set booking_date: {r.status_code} {r.text}"

    def test_generate_schedule_returns_13_items_with_due_dates(self, auth_headers):
        r = requests.post(
            f"{BASE_URL}/api/calculator/generate-schedule/{RAMYA_UUID}",
            headers=auth_headers,
        )
        assert r.status_code == 200, f"generate-schedule failed: {r.status_code} {r.text}"
        data = r.json()
        schedule = data.get("schedule", {})
        items = schedule.get("items", [])
        assert len(items) == 13, f"Expected 13 items, got {len(items)}"

        for it in items:
            assert it.get("due_date"), f"due_date is empty on {it.get('milestone')}"
            # must parse as ISO date
            datetime.strptime(it["due_date"], "%Y-%m-%d")

    def test_first_five_due_dates_match_offsets(self, auth_headers):
        r = requests.post(
            f"{BASE_URL}/api/calculator/generate-schedule/{RAMYA_UUID}",
            headers=auth_headers,
        )
        items = r.json()["schedule"]["items"]
        anchor = date(2026, 3, 30)
        expectations = {
            "booking": anchor + timedelta(days=10),      # 2026-04-09
            "agreement": anchor + timedelta(days=30),    # 2026-04-29
            "foundation": anchor + timedelta(days=90),   # 2026-06-28
            "podium": anchor + timedelta(days=180),      # 2026-09-26
            "2nd_floor": anchor + timedelta(days=240),   # 2026-11-25
        }
        for it in items:
            m = it.get("milestone")
            if m in expectations:
                assert it["due_date"] == expectations[m].isoformat(), (
                    f"{m}: expected {expectations[m].isoformat()}, got {it['due_date']}"
                )

    def test_percentages_sum_to_100_and_cumulative_correct(self, auth_headers):
        r = requests.post(
            f"{BASE_URL}/api/calculator/generate-schedule/{RAMYA_UUID}",
            headers=auth_headers,
        )
        items = r.json()["schedule"]["items"]
        percentages = [it.get("percentage", 0) for it in items]
        assert sum(percentages) == 100, f"percentages sum={sum(percentages)}"

        # cumulative check: sum of amounts up to i == item[i]['cumulative']
        running = 0.0
        for it in items:
            running += it.get("amount", 0)
            # rounding may cause tiny drift
            assert abs(running - it.get("cumulative", 0)) < 1.0, (
                f"cumulative mismatch at {it.get('milestone')}: running={running}, "
                f"got {it.get('cumulative')}"
            )


# ---------- Feature: fallback to today when booking_date is missing ---------- #
class TestGenerateScheduleFallback:
    """Use a scratch customer without a booking_date to verify today-fallback."""

    scratch_uuid = None

    def test_create_scratch_customer_and_generate(self, auth_headers):
        payload = {
            "name": "TEST_scratch_no_booking",
            "phone": "9000000001",
            "email": "test_scratch@example.com",
            "total_price": 1000000,
            "project": "TEST_PROJECT",
            "tower": "T1",
            "unit_number": "TEST-NB-01",
        }
        r = requests.post(
            f"{BASE_URL}/api/customers", headers=auth_headers, json=payload
        )
        assert r.status_code in (200, 201), f"create customer failed: {r.status_code} {r.text}"
        body = r.json()
        # Some backends return {'customer': {...}} or the customer directly
        cust = body.get("customer", body)
        uuid_ = cust.get("id") or cust.get("_id")
        assert uuid_, f"no id in create response: {body}"
        TestGenerateScheduleFallback.scratch_uuid = uuid_

        # Explicitly null out booking_date (in case default was applied)
        upd = requests.put(
            f"{BASE_URL}/api/customers/{uuid_}",
            headers=auth_headers,
            json={"booking_date": None},
        )
        # If PUT sends booking_date=None; some backends may reject → try empty string
        if upd.status_code != 200:
            requests.put(
                f"{BASE_URL}/api/customers/{uuid_}",
                headers=auth_headers,
                json={"booking_date": ""},
            )

        # Generate schedule
        r2 = requests.post(
            f"{BASE_URL}/api/calculator/generate-schedule/{uuid_}",
            headers=auth_headers,
        )
        assert r2.status_code == 200, f"gen failed: {r2.status_code} {r2.text}"
        items = r2.json()["schedule"]["items"]
        assert len(items) == 13

        # First item (booking): due_date should be today + 10 days
        booking_item = next(i for i in items if i["milestone"] == "booking")
        assert booking_item["due_date"], "due_date empty on booking (fallback failed)"

        today = datetime.now(timezone.utc).date()
        expected = today + timedelta(days=10)
        got = datetime.strptime(booking_item["due_date"], "%Y-%m-%d").date()
        # Allow 1-day drift due to timezone at day boundary
        assert abs((got - expected).days) <= 1, (
            f"fallback expected ~{expected}, got {got}"
        )

        # Assert NO empty due_date anywhere
        for it in items:
            assert it["due_date"], f"empty due_date for {it.get('milestone')}"

    def test_cleanup_scratch_customer(self, auth_headers):
        uuid_ = TestGenerateScheduleFallback.scratch_uuid
        if not uuid_:
            pytest.skip("no scratch to delete")
        r = requests.delete(
            f"{BASE_URL}/api/customers/{uuid_}", headers=auth_headers
        )
        # Not fatal if soft delete or 204
        assert r.status_code in (200, 204, 404), f"cleanup failed: {r.status_code}"


# ---------- Feature: booking_date parser variants ---------- #
class TestBookingDateParserVariants:
    """Verify the generator handles YYYY-MM-DD and ISO datetime formats."""

    scratch_uuid = None

    @pytest.fixture(autouse=True, scope="class")
    def create_scratch(self, auth_headers):
        payload = {
            "name": "TEST_scratch_iso_parser",
            "phone": "9000000002",
            "email": "test_iso_parser@example.com",
            "total_price": 500000,
            "project": "TEST_PROJECT",
            "tower": "T1",
            "unit_number": "TEST-IP-01",
        }
        r = requests.post(f"{BASE_URL}/api/customers", headers=auth_headers, json=payload)
        assert r.status_code in (200, 201)
        cust = r.json().get("customer", r.json())
        TestBookingDateParserVariants.scratch_uuid = cust.get("id") or cust.get("_id")
        yield
        # teardown
        requests.delete(
            f"{BASE_URL}/api/customers/{TestBookingDateParserVariants.scratch_uuid}",
            headers=auth_headers,
        )

    @pytest.mark.parametrize("bd_value,expected_anchor", [
        ("2025-06-15", date(2025, 6, 15)),
        ("2025-06-15T10:30:00", date(2025, 6, 15)),
    ])
    def test_parser_variant(self, auth_headers, bd_value, expected_anchor):
        uuid_ = TestBookingDateParserVariants.scratch_uuid
        r = requests.put(
            f"{BASE_URL}/api/customers/{uuid_}",
            headers=auth_headers,
            json={"booking_date": bd_value},
        )
        assert r.status_code == 200, f"cannot set booking_date={bd_value}: {r.text}"

        g = requests.post(
            f"{BASE_URL}/api/calculator/generate-schedule/{uuid_}",
            headers=auth_headers,
        )
        assert g.status_code == 200
        items = g.json()["schedule"]["items"]
        booking = next(i for i in items if i["milestone"] == "booking")
        expected = (expected_anchor + timedelta(days=10)).isoformat()
        assert booking["due_date"] == expected, (
            f"variant {bd_value}: expected {expected}, got {booking['due_date']}"
        )


# ---------- Feature: template endpoint exposes days_offset ---------- #
class TestPaymentScheduleTemplate:
    def test_template_returns_13_items_with_days_offset(self, auth_headers):
        r = requests.get(
            f"{BASE_URL}/api/calculator/payment-schedule-template",
            headers=auth_headers,
            params={"total_amount": 1000000},
        )
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert len(items) == 13
        for expected_ms, expected_pct, expected_offset in EXPECTED_STAGES:
            found = next((i for i in items if i.get("milestone") == expected_ms), None)
            assert found, f"missing milestone {expected_ms}"
            assert found.get("days_offset") == expected_offset, (
                f"{expected_ms}: expected offset {expected_offset}, got {found.get('days_offset')}"
            )
            assert found.get("percentage") == expected_pct


# ---------- Restore Ramya's booking_date at end ---------- #
@pytest.fixture(scope="module", autouse=True)
def _restore_ramya_booking_date(auth_headers, ramya_original_booking_date):
    yield
    if ramya_original_booking_date:
        requests.put(
            f"{BASE_URL}/api/customers/{RAMYA_UUID}",
            headers=auth_headers,
            json={"booking_date": ramya_original_booking_date},
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
