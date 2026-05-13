"""
Iteration 30: Document inline edit (PUT /documents/html/{id}) +
Admin Template Editor (POST /templates/snapshot/{doc_type}, DELETE /templates/{id}).
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')
API = f"{BASE_URL}/api"

ADMIN = {"email": "crm@rrlbuildersanddevelopers.com", "password": "#RRLnew2026"}
ACCOUNTS = {"email": "accounts@rrlbuilders.com", "password": "accounts123"}
CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"  # Ramya test lead


def _login(creds):
    r = requests.post(f"{API}/auth/login", json=creds, timeout=20)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    j = r.json()
    return j.get("access_token") or j.get("token")


@pytest.fixture(scope="module")
def admin_headers():
    return {"Authorization": f"Bearer {_login(ADMIN)}"}


@pytest.fixture(scope="module")
def accounts_headers():
    return {"Authorization": f"Bearer {_login(ACCOUNTS)}"}


# ---------------------------------------------------------------------
# Generate a doc once and reuse across tests
# ---------------------------------------------------------------------
@pytest.fixture(scope="module")
def generated_doc(admin_headers):
    r = requests.post(
        f"{API}/documents/generate",
        headers=admin_headers,
        json={"customer_id": CUSTOMER_ID, "doc_type": "allotment_letter", "custom_fields": {}},
        timeout=30,
    )
    assert r.status_code == 200, r.text
    data = r.json()["document"]
    yield data
    # cleanup
    requests.delete(f"{API}/documents/{data['id']}", headers=admin_headers, timeout=20)


# ---------------------------------------------------------------------
# PUT /documents/html/{doc_id}
# ---------------------------------------------------------------------
class TestEditDocumentHtml:
    def test_admin_can_update(self, admin_headers, generated_doc):
        new_content = "<html><body><h1>TEST_EDITED_BY_ADMIN</h1></body></html>"
        r = requests.put(
            f"{API}/documents/html/{generated_doc['id']}",
            headers=admin_headers,
            json={"content": new_content},
            timeout=20,
        )
        assert r.status_code == 200, r.text
        # verify persistence
        g = requests.get(
            f"{API}/documents/html/{generated_doc['id']}",
            headers=admin_headers,
            timeout=20,
        )
        assert g.status_code == 200
        assert "TEST_EDITED_BY_ADMIN" in g.json()["content"]

    def test_missing_content_returns_400(self, admin_headers, generated_doc):
        r = requests.put(
            f"{API}/documents/html/{generated_doc['id']}",
            headers=admin_headers,
            json={},
            timeout=20,
        )
        assert r.status_code == 400, r.text

    def test_empty_string_returns_400(self, admin_headers, generated_doc):
        r = requests.put(
            f"{API}/documents/html/{generated_doc['id']}",
            headers=admin_headers,
            json={"content": "   "},
            timeout=20,
        )
        assert r.status_code == 400

    def test_non_string_returns_400(self, admin_headers, generated_doc):
        r = requests.put(
            f"{API}/documents/html/{generated_doc['id']}",
            headers=admin_headers,
            json={"content": 12345},
            timeout=20,
        )
        assert r.status_code == 400

    def test_accounts_gets_403(self, accounts_headers, generated_doc):
        r = requests.put(
            f"{API}/documents/html/{generated_doc['id']}",
            headers=accounts_headers,
            json={"content": "<html>nope</html>"},
            timeout=20,
        )
        assert r.status_code == 403

    def test_unknown_doc_returns_404(self, admin_headers):
        r = requests.put(
            f"{API}/documents/html/nonexistent-doc-id-xyz",
            headers=admin_headers,
            json={"content": "<html></html>"},
            timeout=20,
        )
        assert r.status_code == 404


# ---------------------------------------------------------------------
# PDF download still works after edit
# ---------------------------------------------------------------------
class TestPdfDownload:
    def test_pdf_download_after_edit(self, admin_headers, generated_doc):
        r = requests.get(
            f"{API}/documents/pdf/{generated_doc['id']}",
            headers=admin_headers,
            timeout=60,
        )
        assert r.status_code == 200, r.text
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert r.content[:4] == b"%PDF"


# ---------------------------------------------------------------------
# Snapshot template flow
# ---------------------------------------------------------------------
class TestSnapshotTemplate:
    DOC_TYPE = "cost_breakup"  # safe choice (simple generator, no schedule needed)

    def test_full_snapshot_override_revert_cycle(self, admin_headers):
        # cleanup: remove any pre-existing override for this doc_type
        tmpls = requests.get(f"{API}/templates", headers=admin_headers, timeout=20).json()
        for t in tmpls:
            if t.get("doc_type") == self.DOC_TYPE:
                requests.delete(f"{API}/templates/{t['id']}", headers=admin_headers, timeout=20)

        # 1) snapshot creates template
        s = requests.post(
            f"{API}/templates/snapshot/{self.DOC_TYPE}",
            headers=admin_headers,
            json={"customer_id": CUSTOMER_ID},
            timeout=30,
        )
        assert s.status_code == 200, s.text
        tmpl = s.json()
        assert tmpl["doc_type"] == self.DOC_TYPE
        assert tmpl["is_active"] is True
        assert isinstance(tmpl["content"], str) and len(tmpl["content"]) > 50
        tmpl_id = tmpl["id"]

        try:
            # 2) modify the template content to a unique marker
            marker = "TEST_OVERRIDE_MARKER_X9Y2"
            new_content = (
                "<html><body><h1>" + marker + "</h1>"
                "<p>Customer: {customer_name}</p></body></html>"
            )
            u = requests.put(
                f"{API}/templates/{tmpl_id}",
                headers=admin_headers,
                json={"content": new_content, "is_active": True},
                timeout=20,
            )
            assert u.status_code == 200, u.text

            # 3) generate doc → must contain marker (override used)
            g = requests.post(
                f"{API}/documents/generate",
                headers=admin_headers,
                json={"customer_id": CUSTOMER_ID, "doc_type": self.DOC_TYPE, "custom_fields": {}},
                timeout=30,
            )
            assert g.status_code == 200, g.text
            gen = g.json()["document"]
            assert marker in gen["content"], "Override template content not used in generated doc"
            # placeholder substitution check
            assert "{customer_name}" not in gen["content"]
            # cleanup generated doc
            requests.delete(f"{API}/documents/{gen['id']}", headers=admin_headers, timeout=20)

            # 4) snapshot again should overwrite (same id) with rendered default
            s2 = requests.post(
                f"{API}/templates/snapshot/{self.DOC_TYPE}",
                headers=admin_headers,
                json={"customer_id": CUSTOMER_ID},
                timeout=30,
            )
            assert s2.status_code == 200, s2.text
            assert s2.json()["id"] == tmpl_id
            assert marker not in s2.json()["content"], "Snapshot should overwrite with default, not keep marker"
        finally:
            # 5) DELETE → revert to default
            d = requests.delete(f"{API}/templates/{tmpl_id}", headers=admin_headers, timeout=20)
            assert d.status_code == 200

        # 6) After delete, generation falls back to file-based generator
        g2 = requests.post(
            f"{API}/documents/generate",
            headers=admin_headers,
            json={"customer_id": CUSTOMER_ID, "doc_type": self.DOC_TYPE, "custom_fields": {}},
            timeout=30,
        )
        assert g2.status_code == 200
        gen2 = g2.json()["document"]
        assert "TEST_OVERRIDE_MARKER_X9Y2" not in gen2["content"]
        # cleanup
        requests.delete(f"{API}/documents/{gen2['id']}", headers=admin_headers, timeout=20)

    def test_snapshot_requires_customer_id(self, admin_headers):
        r = requests.post(
            f"{API}/templates/snapshot/cost_breakup",
            headers=admin_headers,
            json={},
            timeout=20,
        )
        assert r.status_code == 400

    def test_snapshot_accounts_forbidden(self, accounts_headers):
        r = requests.post(
            f"{API}/templates/snapshot/cost_breakup",
            headers=accounts_headers,
            json={"customer_id": CUSTOMER_ID},
            timeout=20,
        )
        assert r.status_code == 403


# ---------------------------------------------------------------------
# Regression: existing generators still work with no override
# ---------------------------------------------------------------------
class TestGeneratorsRegression:
    @pytest.mark.parametrize("doc_type", [
        "sales_agreement",
        "allotment_letter",
        "price_breakup",
        "cost_breakup",
        "demand_letter",
        "noc_hdfc",
        "noc_bob",
        "noc_tata",
    ])
    def test_generate(self, admin_headers, doc_type):
        # ensure no override exists for this type
        tmpls = requests.get(f"{API}/templates", headers=admin_headers, timeout=20).json()
        for t in tmpls:
            if t.get("doc_type") == doc_type:
                requests.delete(f"{API}/templates/{t['id']}", headers=admin_headers, timeout=20)

        r = requests.post(
            f"{API}/documents/generate",
            headers=admin_headers,
            json={"customer_id": CUSTOMER_ID, "doc_type": doc_type, "custom_fields": {}},
            timeout=60,
        )
        assert r.status_code == 200, f"{doc_type}: {r.status_code} {r.text}"
        gen = r.json()["document"]
        assert gen["doc_type"] == doc_type
        assert "<" in gen["content"]
        # cleanup
        requests.delete(f"{API}/documents/{gen['id']}", headers=admin_headers, timeout=20)
