"""iteration_50 — additional coverage for _valid_stage_keys helper and the
current-stage filter on /follow-ups/pending + /follow-ups/upcoming."""
import os
from datetime import datetime, timezone

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"
ADMIN = {"email": "crm@rrlbuildersanddevelopers.com", "password": "#RRLnew2026"}
TEST_CUSTOMER = "6d902613-5106-4294-bc3e-b907f85127f7"


def _login():
    r = requests.post(f"{API}/auth/login", json=ADMIN, timeout=15)
    body = r.json()
    return body.get("access_token") or body.get("token")


def _hdr(t):
    return {"Authorization": f"Bearer {t}", "Content-Type": "application/json"}


def _set_stage(t, key):
    return requests.post(f"{API}/settings/current-stage", json={"current_stage": key}, headers=_hdr(t), timeout=10)


def _create_fu(t, **kw):
    from datetime import datetime, timezone
    payload = {
        "stage_key": kw.get("stage_key", "handover"),
        "status": kw.get("status", "Follow-up"),
        "notes": kw.get("notes", "TEST_iter50"),
        "next_follow_up_date": kw.get("next_date"),
        "next_follow_up_time": kw.get("next_time"),
    }
    r = requests.post(f"{API}/customers/{TEST_CUSTOMER}/follow-ups",
                      json=payload, headers=_hdr(t), timeout=15)
    assert r.status_code == 200, r.text
    return r.json()


def _delete_fu(t, fid):
    requests.delete(f"{API}/customers/{TEST_CUSTOMER}/follow-ups/{fid}",
                    headers=_hdr(t), timeout=10)


@pytest.fixture(scope="module")
def token():
    return _login()


@pytest.fixture(scope="module", autouse=True)
def preserve_and_restore(token):
    """Save the current stage before the module runs, restore after."""
    r = requests.get(f"{API}/settings/current-stage", headers=_hdr(token), timeout=10)
    original = r.json().get("current_stage") if r.status_code == 200 else "podium"
    yield
    _set_stage(token, original or "podium")


def test_valid_stage_keys_helper_direct():
    """Unit-test the helper directly (module-private)."""
    from settings import _valid_stage_keys
    assert _valid_stage_keys(None) == set()
    assert _valid_stage_keys("") == set()
    assert _valid_stage_keys("podium") == {"podium"}
    assert _valid_stage_keys("2nd_floor") == {"podium", "2nd_floor"}
    # handover is the last stage → all keys
    hk = _valid_stage_keys("handover")
    assert "podium" in hk and "handover" in hk and "flooring" in hk
    assert _valid_stage_keys("not_a_stage") == set()


def test_upcoming_filters_far_future_stage(token):
    """Follow-up on 'handover' with next_date=today must NOT appear in /upcoming
    when current_stage is 'podium'."""
    _set_stage(token, "podium")
    today = datetime.now(timezone.utc).date().isoformat()
    fu = _create_fu(token, stage_key="handover", next_date=today, notes="TEST_iter50_upcoming")
    try:
        r = requests.get(f"{API}/follow-ups/upcoming", headers=_hdr(token), timeout=15)
        assert r.status_code == 200
        ids = {x["follow_up_id"] for x in r.json()}
        assert fu["id"] not in ids, "handover follow-up must be filtered out at current_stage=podium"

        # Now bump to handover — it should reappear
        _set_stage(token, "handover")
        r2 = requests.get(f"{API}/follow-ups/upcoming", headers=_hdr(token), timeout=15)
        assert r2.status_code == 200
        ids2 = {x["follow_up_id"] for x in r2.json()}
        assert fu["id"] in ids2, "handover follow-up should appear when current_stage=handover"
    finally:
        _delete_fu(token, fu["id"])


def test_pending_filter_matches_when_current_stage_advanced(token):
    """With current_stage=handover, a 'handover' follow-up should appear on /pending."""
    _set_stage(token, "handover")
    fu = _create_fu(token, stage_key="handover", notes="TEST_iter50_pending_handover")
    try:
        r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(token), timeout=15)
        assert r.status_code == 200
        ids = {x["follow_up_id"] for x in r.json()}
        assert fu["id"] in ids, "handover follow-up should appear when current_stage=handover"
    finally:
        _delete_fu(token, fu["id"])


def test_pending_fall_open_when_no_current_stage(token):
    """If settings.current_stage is missing/null, no filter should be applied —
    every follow-up (subject to other filters) is returned."""
    # Directly clear the current_stage in DB via a null-safe approach:
    # We can't POST null through the endpoint (validated), so we manipulate DB.
    from motor.motor_asyncio import AsyncIOMotorClient
    import asyncio
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")

    async def _clear():
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        # Save then unset
        prev = await db.settings.find_one({"type": "payment_stage"})
        await db.settings.update_one(
            {"type": "payment_stage"},
            {"$set": {"current_stage": None}}
        )
        client.close()
        return prev

    async def _restore(prev):
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        await db.settings.update_one(
            {"type": "payment_stage"},
            {"$set": {"current_stage": prev.get("current_stage") if prev else "podium"}}
        )
        client.close()

    prev = asyncio.get_event_loop().run_until_complete(_clear())
    fu = _create_fu(token, stage_key="handover", notes="TEST_iter50_fallopen")
    try:
        r = requests.get(f"{API}/follow-ups/pending", headers=_hdr(token), timeout=15)
        assert r.status_code == 200
        ids = {x["follow_up_id"] for x in r.json()}
        assert fu["id"] in ids, "fall-open must return follow-ups when current_stage is null"
    finally:
        _delete_fu(token, fu["id"])
        asyncio.get_event_loop().run_until_complete(_restore(prev))
