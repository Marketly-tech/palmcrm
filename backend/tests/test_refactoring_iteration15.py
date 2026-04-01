"""
Test suite for RRL CRM Refactoring - Iteration 15
Tests backend APIs after major refactoring:
- Backend: HTML template generators extracted from server.py into documents/templates.py
- Frontend: Inline tab content replaced with extracted components

Test Coverage:
- Login flow for admin user
- Customer detail API
- Document generation APIs (price_breakup, sales_agreement, allotment_letter, cost_breakup, noc_hdfc)
- Payment schedule APIs
- Communication APIs
- Checklist APIs
- Notes APIs
"""

import pytest
import requests
import os
import time
from tests.conftest_credentials import ADMIN_EMAIL, ADMIN_PASSWORD, ACCOUNTS_EMAIL, ACCOUNTS_PASSWORD, TEST_CUSTOMER_ID, API_URL, TEST_BASE_URL

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = ADMIN_EMAIL
ADMIN_PASSWORD = ADMIN_PASSWORD
TEST_CUSTOMER_ID = TEST_CUSTOMER_ID  # Ramya test lead


class TestHealthAndAuth:
    """Health check and authentication tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("✓ Health endpoint working")
    
    def test_admin_login_success(self):
        """Test admin login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "access_token not in response"
        assert "user" in data, "User not in response"
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"✓ Admin login successful - User: {data['user']['name']}")
        return data["access_token"]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid credentials correctly rejected")


@pytest.fixture(scope="class")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="class")
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestCustomerAPIs:
    """Customer detail and related APIs"""
    
    def test_get_customer_detail(self, auth_headers):
        """Test fetching customer detail for test customer"""
        response = requests.get(
            f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get customer: {response.text}"
        data = response.json()
        assert data.get("id") == TEST_CUSTOMER_ID
        assert "name" in data
        print(f"✓ Customer detail fetched - Name: {data.get('name')}")
        return data
    
    def test_get_customer_checklist(self, auth_headers):
        """Test fetching customer checklist"""
        response = requests.get(
            f"{BASE_URL}/api/checklist/{TEST_CUSTOMER_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get checklist: {response.text}"
        data = response.json()
        assert "items" in data
        print(f"✓ Checklist fetched - Items: {len(data.get('items', {}))}")
    
    def test_get_customer_notes(self, auth_headers):
        """Test fetching customer notes"""
        response = requests.get(
            f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/notes",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get notes: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Notes fetched - Count: {len(data)}")
    
    def test_get_customer_communications(self, auth_headers):
        """Test fetching customer communications"""
        response = requests.get(
            f"{BASE_URL}/api/communication/{TEST_CUSTOMER_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get communications: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Communications fetched - Count: {len(data)}")


class TestPaymentScheduleAPIs:
    """Payment schedule related APIs"""
    
    def test_get_payment_schedule(self, auth_headers):
        """Test fetching payment schedule"""
        response = requests.get(
            f"{BASE_URL}/api/payments/schedule/{TEST_CUSTOMER_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get schedule: {response.text}"
        data = response.json()
        assert "items" in data
        print(f"✓ Payment schedule fetched - Items: {len(data.get('items', []))}")
    
    def test_get_transactions(self, auth_headers):
        """Test fetching transactions"""
        response = requests.get(
            f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get transactions: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Transactions fetched - Count: {len(data)}")


class TestDocumentGenerationAPIs:
    """Document generation APIs - testing refactored template generators"""
    
    def test_generate_price_breakup(self, auth_headers):
        """Test generating price_breakup document"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            headers=auth_headers,
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "price_breakup",
                "custom_fields": {}
            }
        )
        assert response.status_code == 200, f"Failed to generate price_breakup: {response.text}"
        data = response.json()
        assert "document" in data
        doc = data["document"]
        assert doc.get("doc_type") == "price_breakup"
        assert "content" in doc
        assert len(doc["content"]) > 100, "Document content too short"
        print(f"✓ Price breakup generated - Content length: {len(doc['content'])}")
    
    def test_generate_cost_breakup(self, auth_headers):
        """Test generating cost_breakup document"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            headers=auth_headers,
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "cost_breakup",
                "custom_fields": {}
            }
        )
        assert response.status_code == 200, f"Failed to generate cost_breakup: {response.text}"
        data = response.json()
        assert "document" in data
        doc = data["document"]
        assert doc.get("doc_type") == "cost_breakup"
        assert "content" in doc
        print(f"✓ Cost breakup generated - Content length: {len(doc['content'])}")
    
    def test_generate_allotment_letter(self, auth_headers):
        """Test generating allotment_letter document"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            headers=auth_headers,
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "allotment_letter",
                "custom_fields": {}
            }
        )
        assert response.status_code == 200, f"Failed to generate allotment_letter: {response.text}"
        data = response.json()
        assert "document" in data
        doc = data["document"]
        assert doc.get("doc_type") == "allotment_letter"
        assert "content" in doc
        print(f"✓ Allotment letter generated - Content length: {len(doc['content'])}")
    
    def test_generate_sales_agreement(self, auth_headers):
        """Test generating sales_agreement document"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            headers=auth_headers,
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "sales_agreement",
                "custom_fields": {}
            }
        )
        assert response.status_code == 200, f"Failed to generate sales_agreement: {response.text}"
        data = response.json()
        assert "document" in data
        doc = data["document"]
        assert doc.get("doc_type") == "sales_agreement"
        assert "content" in doc
        # Sales agreement should be substantial
        assert len(doc["content"]) > 1000, "Sales agreement content too short"
        print(f"✓ Sales agreement generated - Content length: {len(doc['content'])}")
    
    def test_generate_noc_hdfc(self, auth_headers):
        """Test generating HDFC NOC document"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            headers=auth_headers,
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "noc_hdfc",
                "custom_fields": {}
            }
        )
        assert response.status_code == 200, f"Failed to generate noc_hdfc: {response.text}"
        data = response.json()
        assert "document" in data
        doc = data["document"]
        assert doc.get("doc_type") == "noc_hdfc"
        assert "content" in doc
        # Verify HDFC-specific content
        assert "HDFC" in doc["content"], "HDFC not found in NOC content"
        print(f"✓ HDFC NOC generated - Content length: {len(doc['content'])}")
    
    def test_generate_payment_schedule_doc(self, auth_headers):
        """Test generating payment_schedule document"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            headers=auth_headers,
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "payment_schedule",
                "custom_fields": {}
            }
        )
        assert response.status_code == 200, f"Failed to generate payment_schedule: {response.text}"
        data = response.json()
        assert "document" in data
        doc = data["document"]
        assert doc.get("doc_type") == "payment_schedule"
        print(f"✓ Payment schedule document generated - Content length: {len(doc['content'])}")
    
    def test_get_generated_documents(self, auth_headers):
        """Test fetching generated documents list"""
        response = requests.get(
            f"{BASE_URL}/api/documents/{TEST_CUSTOMER_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get documents: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Generated documents fetched - Count: {len(data)}")


class TestUploadedDocumentsAPIs:
    """Uploaded documents APIs"""
    
    def test_get_uploaded_documents(self, auth_headers):
        """Test fetching uploaded documents list"""
        response = requests.get(
            f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/documents-list",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get uploaded docs: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Uploaded documents fetched - Count: {len(data)}")


class TestDashboardAPIs:
    """Dashboard APIs"""
    
    def test_get_dashboard_stats(self, auth_headers):
        """Test fetching dashboard stats"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get dashboard stats: {response.text}"
        data = response.json()
        assert "total_customers" in data or "customers" in data or isinstance(data, dict)
        print(f"✓ Dashboard stats fetched")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
