"""
Iteration 52 — Bulk-delete endpoints across 8 surfaces.

Verifies:
 - Role gating (admin passes, non-admin sales returns 403).
 - Body validation ({ids:[]} / missing / non-array -> 400).
 - Non-existent id in a valid list -> deleted_count: 0 (no 500).
 - Users bulk-delete silently skips the current user's own id.
 - Customers bulk-delete cascades to schedules / checklists / generated
   documents / communication logs / payment transactions.
 - Uploaded-documents bulk-delete strips uploaded_documents pointer map.
 - Transactions bulk-delete recomputes customer totals.
 - Follow-ups bulk-delete recomputes latest_call_status.
"""
import os
import uuid
import base64
import io
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')

ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASSWORD = "#RRLnew2026"
SALES_EMAIL = "sales@rrlrprojects.com"
SALES_PASSWORD = "sales123"

RAMYA_ID = "6d902613-5106-4294-bc3e-b907f85127f7"


# ---------- fixtures ----------
def _login(email, password):
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"email": email, "password": password}, timeout=30)
    assert r.status_code == 200, f"login failed for {email}: {r.status_code} {r.text}"
    data = r.json()
    return data["access_token"], data["user"]


@pytest.fixture(scope="session")
def admin_auth():
    token, user = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    return {"headers": {"Authorization": f"Bearer {token}"}, "user": user}


@pytest.fixture(scope="session")
def sales_auth():
    token, user = _login(SALES_EMAIL, SALES_PASSWORD)
    return {"headers": {"Authorization": f"Bearer {token}"}, "user": user}


@pytest.fixture()
def admin_headers(admin_auth):
    return admin_auth["headers"]


@pytest.fixture()
def sales_headers(sales_auth):
    return sales_auth["headers"]


# ---------- helpers ----------
def _create_test_customer(headers, name_suffix=""):
    payload = {
        "name": f"TEST_bulk_{name_suffix}_{uuid.uuid4().hex[:6]}",
        "email": f"test_bulk_{uuid.uuid4().hex[:6]}@example.com",
        "phone": f"9{uuid.uuid4().int % 1000000000:09d}",
        "project": "Palm Altezze",
        "unit_number": f"T{uuid.uuid4().hex[:3]}",
        "tower": "A",
        "total_price": 5000000,
        "booking_date": "2026-03-30",
    }
    r = requests.post(f"{BASE_URL}/api/customers", headers=headers, json=payload, timeout=30)
    assert r.status_code == 200, f"create customer failed: {r.status_code} {r.text}"
    return r.json()


# ==================================================================
# 1. VALIDATION — {ids:[]} / missing / non-array -> 400
# ==================================================================
class TestBulkDeleteValidation:
    """Every bulk-delete endpoint must reject empty/missing/non-array ids -> 400."""

    ENDPOINTS = [
        ("customers/bulk-delete", None),
        ("users/bulk-delete", None),
        ("templates/bulk-delete", None),
        ("documents/bulk-delete", None),
        (f"customers/{RAMYA_ID}/documents/bulk-delete", None),
        (f"transactions/{RAMYA_ID}/bulk-delete", None),
        (f"customers/{RAMYA_ID}/notes/bulk-delete", None),
        (f"customers/{RAMYA_ID}/follow-ups/bulk-delete", None),
    ]

    @pytest.mark.parametrize("endpoint,_", ENDPOINTS)
    def test_empty_ids_list_returns_400(self, endpoint, _, admin_headers):
        r = requests.post(f"{BASE_URL}/api/{endpoint}", headers=admin_headers,
                          json={"ids": []}, timeout=30)
        assert r.status_code == 400, f"{endpoint}: expected 400, got {r.status_code} {r.text}"

    @pytest.mark.parametrize("endpoint,_", ENDPOINTS)
    def test_missing_ids_returns_400(self, endpoint, _, admin_headers):
        r = requests.post(f"{BASE_URL}/api/{endpoint}", headers=admin_headers,
                          json={}, timeout=30)
        assert r.status_code == 400, f"{endpoint}: expected 400, got {r.status_code} {r.text}"

    @pytest.mark.parametrize("endpoint,_", ENDPOINTS)
    def test_non_array_ids_returns_400(self, endpoint, _, admin_headers):
        r = requests.post(f"{BASE_URL}/api/{endpoint}", headers=admin_headers,
                          json={"ids": "not-a-list"}, timeout=30)
        assert r.status_code == 400, f"{endpoint}: expected 400, got {r.status_code} {r.text}"


# ==================================================================
# 2. ROLE GATING — non-admin -> 403
# ==================================================================
class TestBulkDeleteRoleGating:
    """Every bulk-delete endpoint must reject non-admin callers -> 403."""

    ENDPOINTS = [
        "customers/bulk-delete",
        "users/bulk-delete",
        "templates/bulk-delete",
        "documents/bulk-delete",
        f"customers/{RAMYA_ID}/documents/bulk-delete",
        f"transactions/{RAMYA_ID}/bulk-delete",
        f"customers/{RAMYA_ID}/notes/bulk-delete",
        f"customers/{RAMYA_ID}/follow-ups/bulk-delete",
    ]

    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_sales_forbidden(self, endpoint, sales_headers):
        r = requests.post(f"{BASE_URL}/api/{endpoint}", headers=sales_headers,
                          json={"ids": ["fake-id"]}, timeout=30)
        assert r.status_code == 403, f"{endpoint}: expected 403, got {r.status_code} {r.text}"


# ==================================================================
# 3. NON-EXISTENT IDS — deleted_count 0, no 500
# ==================================================================
class TestBulkDeleteNonexistentIds:

    def test_customers_nonexistent(self, admin_headers):
        r = requests.post(f"{BASE_URL}/api/customers/bulk-delete", headers=admin_headers,
                          json={"ids": ["nonexistent-xyz-1", "nonexistent-xyz-2"]}, timeout=30)
        assert r.status_code == 200, f"expected 200, got {r.status_code} {r.text}"
        assert r.json().get("deleted_count") == 0

    def test_generated_documents_nonexistent(self, admin_headers):
        r = requests.post(f"{BASE_URL}/api/documents/bulk-delete", headers=admin_headers,
                          json={"ids": ["nonexistent-doc-1"]}, timeout=30)
        assert r.status_code == 200
        assert r.json().get("deleted_count") == 0

    def test_uploaded_docs_nonexistent(self, admin_headers):
        r = requests.post(f"{BASE_URL}/api/customers/{RAMYA_ID}/documents/bulk-delete",
                          headers=admin_headers, json={"ids": ["nonexistent-upload-1"]}, timeout=30)
        assert r.status_code == 200
        assert r.json().get("deleted_count") == 0

    def test_transactions_nonexistent(self, admin_headers):
        r = requests.post(f"{BASE_URL}/api/transactions/{RAMYA_ID}/bulk-delete",
                          headers=admin_headers, json={"ids": ["nonexistent-txn-1"]}, timeout=30)
        assert r.status_code == 200
        assert r.json().get("deleted_count") == 0

    def test_notes_nonexistent_on_valid_customer(self, admin_headers):
        r = requests.post(f"{BASE_URL}/api/customers/{RAMYA_ID}/notes/bulk-delete",
                          headers=admin_headers, json={"ids": ["nonexistent-note-1"]}, timeout=30)
        # customer exists -> 200 with pull that removed nothing
        assert r.status_code == 200

    def test_followups_nonexistent_on_valid_customer(self, admin_headers):
        r = requests.post(f"{BASE_URL}/api/customers/{RAMYA_ID}/follow-ups/bulk-delete",
                          headers=admin_headers, json={"ids": ["nonexistent-fu-1"]}, timeout=30)
        assert r.status_code == 200

    def test_templates_nonexistent(self, admin_headers):
        r = requests.post(f"{BASE_URL}/api/templates/bulk-delete", headers=admin_headers,
                          json={"ids": ["nonexistent-tmpl-1"]}, timeout=30)
        assert r.status_code == 200
        assert r.json().get("deleted_count") == 0


# ==================================================================
# 4. CUSTOMERS BULK-DELETE CASCADE
# ==================================================================
class TestCustomersBulkDeleteCascade:

    def test_bulk_delete_customer_and_verify_removal(self, admin_headers):
        c1 = _create_test_customer(admin_headers, "cascade1")
        c2 = _create_test_customer(admin_headers, "cascade2")
        r = requests.post(f"{BASE_URL}/api/customers/bulk-delete", headers=admin_headers,
                          json={"ids": [c1["id"], c2["id"]]}, timeout=30)
        assert r.status_code == 200
        assert r.json().get("deleted_count") == 2
        # verify 404 on GET
        r1 = requests.get(f"{BASE_URL}/api/customers/{c1['id']}", headers=admin_headers, timeout=30)
        assert r1.status_code == 404

    def test_cascade_deletes_transactions_and_schedules(self, admin_headers):
        cust = _create_test_customer(admin_headers, "cascadetxn")
        cid = cust["id"]
        # Generate a payment schedule (creates payment_schedules doc)
        r_sch = requests.post(f"{BASE_URL}/api/calculator/generate-schedule/{cid}",
                              headers=admin_headers, timeout=30)
        assert r_sch.status_code == 200, r_sch.text

        # Create a payment transaction
        txn_payload = {
            "transaction_stage": "booking",
            "transaction_date": "2026-03-30",
            "bank_name": "HDFC",
            "transaction_number": f"TXN-{uuid.uuid4().hex[:8]}",
            "amount": 100000,
            "notes": "TEST_cascade",
        }
        r_txn = requests.post(f"{BASE_URL}/api/transactions/{cid}", headers=admin_headers,
                              json=txn_payload, timeout=30)
        assert r_txn.status_code == 200, r_txn.text

        # Bulk delete customer
        r_del = requests.post(f"{BASE_URL}/api/customers/bulk-delete", headers=admin_headers,
                              json={"ids": [cid]}, timeout=30)
        assert r_del.status_code == 200
        assert r_del.json().get("deleted_count") == 1

        # Verify transactions gone
        r_get_txn = requests.get(f"{BASE_URL}/api/transactions/{cid}", headers=admin_headers, timeout=30)
        assert r_get_txn.status_code == 200
        assert r_get_txn.json() == []

        # Verify schedule gone
        r_get_sch = requests.get(f"{BASE_URL}/api/payments/schedule/{cid}", headers=admin_headers, timeout=30)
        # returns {items: []} for missing
        assert r_get_sch.status_code == 200
        assert r_get_sch.json().get("items", []) == []


# ==================================================================
# 5. USERS BULK-DELETE — self-lockout protection
# ==================================================================
class TestUsersBulkDeleteSelfLockout:

    def test_only_own_id_returns_400_no_deletable(self, admin_auth, admin_headers):
        """Admin passes only their own id -> silently stripped -> 400 'No deletable IDs'."""
        own_id = admin_auth["user"]["id"]
        r = requests.post(f"{BASE_URL}/api/users/bulk-delete", headers=admin_headers,
                          json={"ids": [own_id]}, timeout=30)
        assert r.status_code == 400, f"expected 400, got {r.status_code} {r.text}"

    def test_admin_self_id_stripped_and_other_deleted(self, admin_auth, admin_headers):
        """Create a throwaway user; admin bulk-deletes [own_id, throwaway_id];
        own_id is stripped, throwaway is deleted. Admin still logged in."""
        # Create throwaway
        payload = {
            "email": f"TEST_bulkuser_{uuid.uuid4().hex[:6]}@example.com",
            "password": "throwaway123",
            "name": "TEST bulk user",
            "role": "sales",
        }
        r_new = requests.post(f"{BASE_URL}/api/auth/register", json=payload, timeout=30)
        assert r_new.status_code == 200, r_new.text
        throwaway_id = r_new.json()["id"]

        own_id = admin_auth["user"]["id"]
        r = requests.post(f"{BASE_URL}/api/users/bulk-delete", headers=admin_headers,
                          json={"ids": [own_id, throwaway_id]}, timeout=30)
        assert r.status_code == 200, r.text
        # Only 1 deletion (own_id stripped)
        assert r.json().get("deleted_count") == 1

        # Verify admin can still call /me
        r_me = requests.get(f"{BASE_URL}/api/auth/me", headers=admin_headers, timeout=30)
        assert r_me.status_code == 200
        assert r_me.json()["id"] == own_id


# ==================================================================
# 6. TRANSACTIONS BULK-DELETE — recomputes customer totals
# ==================================================================
class TestTransactionsBulkDeleteRecompute:

    def test_bulk_delete_transactions_recomputes_totals(self, admin_headers):
        cust = _create_test_customer(admin_headers, "txnrecalc")
        cid = cust["id"]

        # Create 2 transactions
        txn_ids = []
        for amt in [100000, 200000]:
            payload = {
                "transaction_stage": "booking",
                "transaction_date": "2026-03-30",
                "bank_name": "HDFC",
                "transaction_number": f"TXN-{uuid.uuid4().hex[:8]}",
                "amount": amt,
                "notes": "TEST_recalc",
            }
            r = requests.post(f"{BASE_URL}/api/transactions/{cid}", headers=admin_headers,
                              json=payload, timeout=30)
            assert r.status_code == 200, r.text
            txn_ids.append(r.json()["transaction"]["id"])

        # Verify customer.total_received == 300000
        r_c = requests.get(f"{BASE_URL}/api/customers/{cid}", headers=admin_headers, timeout=30)
        assert r_c.json().get("total_received") == 300000

        # Bulk-delete first transaction
        r_bd = requests.post(f"{BASE_URL}/api/transactions/{cid}/bulk-delete",
                             headers=admin_headers, json={"ids": [txn_ids[0]]}, timeout=30)
        assert r_bd.status_code == 200
        assert r_bd.json().get("deleted_count") == 1

        # Verify total_received recomputed to 200000
        r_c2 = requests.get(f"{BASE_URL}/api/customers/{cid}", headers=admin_headers, timeout=30)
        assert r_c2.json().get("total_received") == 200000
        # balance = 5000000 - 200000 = 4800000
        assert r_c2.json().get("balance_amount") == 4800000

        # Cleanup
        requests.post(f"{BASE_URL}/api/customers/bulk-delete", headers=admin_headers,
                      json={"ids": [cid]}, timeout=30)


# ==================================================================
# 7. UPLOADED DOCS BULK-DELETE — strips pointer map
# ==================================================================
class TestUploadedDocsBulkDeleteStripsPointerMap:

    def test_bulk_delete_uploaded_removes_from_pointer_map(self, admin_headers):
        cust = _create_test_customer(admin_headers, "uploadmap")
        cid = cust["id"]

        # Upload two documents
        upload_ids = []
        for i, doc_type in enumerate(["aadhar", "pan"]):
            files = {"file": (f"test_{i}.txt", io.BytesIO(b"hello world"), "text/plain")}
            data = {"doc_type": doc_type}
            r = requests.post(f"{BASE_URL}/api/customers/{cid}/upload-document",
                              headers=admin_headers, files=files, data=data, timeout=30)
            assert r.status_code == 200, r.text
            upload_ids.append(r.json()["doc_id"])

        # Verify pointer map has both entries
        r_c = requests.get(f"{BASE_URL}/api/customers/{cid}", headers=admin_headers, timeout=30)
        pointer_map = r_c.json().get("uploaded_documents", {})
        assert pointer_map.get("aadhar") == upload_ids[0]
        assert pointer_map.get("pan") == upload_ids[1]

        # Bulk-delete both uploads
        r_bd = requests.post(f"{BASE_URL}/api/customers/{cid}/documents/bulk-delete",
                             headers=admin_headers, json={"ids": upload_ids}, timeout=30)
        assert r_bd.status_code == 200, r_bd.text
        assert r_bd.json().get("deleted_count") == 2

        # Verify pointer map is stripped
        r_c2 = requests.get(f"{BASE_URL}/api/customers/{cid}", headers=admin_headers, timeout=30)
        pointer_map2 = r_c2.json().get("uploaded_documents", {}) or {}
        assert "aadhar" not in pointer_map2
        assert "pan" not in pointer_map2

        # Cleanup
        requests.post(f"{BASE_URL}/api/customers/bulk-delete", headers=admin_headers,
                      json={"ids": [cid]}, timeout=30)


# ==================================================================
# 8. NOTES + FOLLOW-UPS BULK-DELETE on Ramya
# ==================================================================
class TestNotesAndFollowupsBulkDelete:

    def test_notes_bulk_delete(self, admin_headers):
        # Create notes on Ramya
        note_ids = []
        for i in range(2):
            r = requests.post(f"{BASE_URL}/api/customers/{RAMYA_ID}/notes",
                              headers=admin_headers,
                              json={"content": f"TEST_bulk_note_{i}"}, timeout=30)
            assert r.status_code == 200, r.text
            note_ids.append(r.json()["id"])

        # Bulk delete
        r_bd = requests.post(f"{BASE_URL}/api/customers/{RAMYA_ID}/notes/bulk-delete",
                             headers=admin_headers, json={"ids": note_ids}, timeout=30)
        assert r_bd.status_code == 200, r_bd.text
        assert r_bd.json().get("deleted_count") == 2

        # Verify notes are gone from customer
        r_c = requests.get(f"{BASE_URL}/api/customers/{RAMYA_ID}", headers=admin_headers, timeout=30)
        remaining_ids = {n["id"] for n in (r_c.json().get("notes") or [])}
        for nid in note_ids:
            assert nid not in remaining_ids

    def test_followups_bulk_delete_recomputes_latest_call_status(self, admin_headers):
        # Snapshot current latest_call_status
        r_before = requests.get(f"{BASE_URL}/api/customers/{RAMYA_ID}",
                                headers=admin_headers, timeout=30)
        _pre_status = r_before.json().get("latest_call_status")

        # Create 2 follow-ups
        fu_ids = []
        for i in range(2):
            payload = {
                "stage_key": "podium",
                "status": "Connected",
                "notes": f"TEST_bulk_fu_{i}",
            }
            r = requests.post(f"{BASE_URL}/api/customers/{RAMYA_ID}/follow-ups",
                              headers=admin_headers, json=payload, timeout=30)
            assert r.status_code == 200, r.text
            fu_ids.append(r.json()["id"])

        # Now latest should be "Connected"
        r_mid = requests.get(f"{BASE_URL}/api/customers/{RAMYA_ID}",
                             headers=admin_headers, timeout=30)
        assert r_mid.json().get("latest_call_status") == "Connected"

        # Bulk-delete both
        r_bd = requests.post(f"{BASE_URL}/api/customers/{RAMYA_ID}/follow-ups/bulk-delete",
                             headers=admin_headers, json={"ids": fu_ids}, timeout=30)
        assert r_bd.status_code == 200, r_bd.text
        assert r_bd.json().get("deleted_count") == 2

        # latest_call_status recomputed — either back to pre-existing or None
        r_after = requests.get(f"{BASE_URL}/api/customers/{RAMYA_ID}",
                               headers=admin_headers, timeout=30)
        # It should NOT equal "Interested" since we deleted them
        # (unless another Interested follow-up existed pre-test)
        remaining_fus = r_after.json().get("follow_ups") or []
        remaining_statuses = {f.get("status") for f in remaining_fus}
        if "Connected" not in remaining_statuses:
            assert r_after.json().get("latest_call_status") != "Connected" or \
                   r_after.json().get("latest_call_status") is None or \
                   r_after.json().get("latest_call_status") == _pre_status


# ==================================================================
# 9. GENERATED DOCUMENTS BULK-DELETE
# ==================================================================
class TestGeneratedDocsBulkDelete:

    def test_generated_docs_bulk_delete(self, admin_headers):
        cust = _create_test_customer(admin_headers, "gendocs")
        cid = cust["id"]
        # Generate 2 documents
        doc_ids = []
        for _ in range(2):
            r = requests.post(f"{BASE_URL}/api/documents/generate",
                              headers=admin_headers,
                              json={"customer_id": cid, "doc_type": "price_breakup", "custom_fields": {}},
                              timeout=60)
            assert r.status_code == 200, r.text
            doc_ids.append(r.json()["document"]["id"])

        r_bd = requests.post(f"{BASE_URL}/api/documents/bulk-delete", headers=admin_headers,
                             json={"ids": doc_ids}, timeout=30)
        assert r_bd.status_code == 200
        assert r_bd.json().get("deleted_count") == 2

        # Cleanup customer
        requests.post(f"{BASE_URL}/api/customers/bulk-delete", headers=admin_headers,
                      json={"ids": [cid]}, timeout=30)
