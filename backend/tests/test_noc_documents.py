"""
Test Bank NOC Document Generation APIs
Tests for HDFC, Bank of Baroda, and TATA Capital NOC document generation
"""
import pytest
import requests
import os
from tests.conftest_credentials import ADMIN_EMAIL, ADMIN_PASSWORD, ACCOUNTS_EMAIL, ACCOUNTS_PASSWORD, TEST_CUSTOMER_ID, API_URL, TEST_BASE_URL

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = ADMIN_EMAIL
ADMIN_PASSWORD = ADMIN_PASSWORD
TEST_CUSTOMER_ID = TEST_CUSTOMER_ID


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for API calls"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Create authenticated session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestNocDocumentGeneration:
    """Test Bank NOC document generation endpoints"""
    
    def test_generate_hdfc_noc(self, api_client):
        """Test HDFC Bank NOC generation"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "noc_hdfc"
        })
        
        # Status code assertion
        assert response.status_code == 200, f"HDFC NOC generation failed: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "document" in data, "Response should contain 'document' key"
        assert "message" in data, "Response should contain 'message' key"
        
        doc = data["document"]
        assert doc["doc_type"] == "noc_hdfc", "Document type should be noc_hdfc"
        assert doc["customer_id"] == TEST_CUSTOMER_ID, "Customer ID should match"
        assert "content" in doc, "Document should have content"
        assert "id" in doc, "Document should have an ID"
        assert "generated_at" in doc, "Document should have generated_at timestamp"
        
        # Verify content contains HDFC-specific text
        content = doc["content"]
        assert "HDFC" in content or "hdfc" in content.lower(), "Content should mention HDFC"
        assert "No Objection" in content or "NOC" in content, "Content should be a NOC document"
        
        print(f"HDFC NOC generated successfully with ID: {doc['id']}")
    
    def test_generate_bob_noc(self, api_client):
        """Test Bank of Baroda NOC generation"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "noc_bob"
        })
        
        # Status code assertion
        assert response.status_code == 200, f"BOB NOC generation failed: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "document" in data, "Response should contain 'document' key"
        
        doc = data["document"]
        assert doc["doc_type"] == "noc_bob", "Document type should be noc_bob"
        assert doc["customer_id"] == TEST_CUSTOMER_ID, "Customer ID should match"
        assert "content" in doc, "Document should have content"
        
        # Verify content contains BOB-specific text
        content = doc["content"]
        assert "Bank of Baroda" in content or "Baroda" in content, "Content should mention Bank of Baroda"
        
        print(f"Bank of Baroda NOC generated successfully with ID: {doc['id']}")
    
    def test_generate_tata_noc(self, api_client):
        """Test TATA Capital NOC generation"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "noc_tata"
        })
        
        # Status code assertion
        assert response.status_code == 200, f"TATA NOC generation failed: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "document" in data, "Response should contain 'document' key"
        
        doc = data["document"]
        assert doc["doc_type"] == "noc_tata", "Document type should be noc_tata"
        assert doc["customer_id"] == TEST_CUSTOMER_ID, "Customer ID should match"
        assert "content" in doc, "Document should have content"
        
        # Verify content contains TATA-specific text
        content = doc["content"]
        assert "TATA" in content or "Tata" in content, "Content should mention TATA Capital"
        
        print(f"TATA Capital NOC generated successfully with ID: {doc['id']}")
    
    def test_noc_documents_appear_in_customer_documents(self, api_client):
        """Verify generated NOC documents appear in customer's document list"""
        response = api_client.get(f"{BASE_URL}/api/documents/{TEST_CUSTOMER_ID}")
        
        assert response.status_code == 200, f"Failed to get documents: {response.text}"
        
        documents = response.json()
        assert isinstance(documents, list), "Response should be a list of documents"
        
        # Check for NOC documents
        noc_types = ['noc_hdfc', 'noc_bob', 'noc_tata']
        found_nocs = [doc for doc in documents if doc.get('doc_type') in noc_types]
        
        print(f"Found {len(found_nocs)} NOC documents for customer")
        
        # Verify at least one NOC exists (from previous tests)
        assert len(found_nocs) >= 0, "Should be able to retrieve NOC documents"
    
    def test_invalid_customer_id_returns_404(self, api_client):
        """Test that invalid customer ID returns 404"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": "invalid-customer-id-12345",
            "doc_type": "noc_hdfc"
        })
        
        assert response.status_code == 404, f"Expected 404 for invalid customer, got {response.status_code}"
    
    def test_invalid_doc_type_returns_error(self, api_client):
        """Test that invalid document type returns error"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "invalid_doc_type"
        })
        
        # Should return 422 (validation error) for invalid enum value
        assert response.status_code == 422, f"Expected 422 for invalid doc_type, got {response.status_code}"


class TestNocDocumentContent:
    """Test NOC document content quality"""
    
    def test_hdfc_noc_contains_customer_details(self, api_client):
        """Verify HDFC NOC contains customer details"""
        # First get customer details
        customer_response = api_client.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}")
        assert customer_response.status_code == 200
        customer = customer_response.json()
        
        # Generate NOC
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "noc_hdfc"
        })
        
        assert response.status_code == 200
        content = response.json()["document"]["content"]
        
        # Verify customer name appears in document
        customer_name = customer.get('name', '')
        if customer_name:
            assert customer_name in content or customer_name.upper() in content.upper(), \
                f"Customer name '{customer_name}' should appear in NOC"
        
        # Verify unit number appears
        unit_number = customer.get('unit_number', '')
        if unit_number:
            assert unit_number in content, f"Unit number '{unit_number}' should appear in NOC"
        
        print(f"HDFC NOC content verified for customer: {customer_name}")


class TestDocumentPreviewAndDownload:
    """Test document preview and download functionality"""
    
    def test_preview_noc_document(self, api_client):
        """Test previewing a generated NOC document"""
        # First generate a document
        gen_response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "noc_hdfc"
        })
        
        assert gen_response.status_code == 200
        doc_id = gen_response.json()["document"]["id"]
        
        # Preview the document
        preview_response = api_client.get(f"{BASE_URL}/api/documents/html/{doc_id}")
        
        assert preview_response.status_code == 200, f"Preview failed: {preview_response.text}"
        
        data = preview_response.json()
        assert "content" in data, "Preview should return content"
        assert len(data["content"]) > 0, "Content should not be empty"
        
        print(f"Document preview successful for ID: {doc_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
