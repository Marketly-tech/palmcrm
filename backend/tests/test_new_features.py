"""
Test cases for new features:
1. Document Delete API
2. Dashboard Upcoming Due Dates API  
3. Customers Agreement Filter
"""
import pytest
import requests
import os
from datetime import datetime, timedelta
from tests.conftest_credentials import ADMIN_EMAIL, ADMIN_PASSWORD, ACCOUNTS_EMAIL, ACCOUNTS_PASSWORD, TEST_CUSTOMER_ID, API_URL, TEST_BASE_URL

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@rrlbuilders.com"
TEST_PASSWORD = ADMIN_PASSWORD


class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL


class TestDashboardUpcomingDueDates:
    """Test Dashboard Upcoming Due Dates API"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_upcoming_due_dates_endpoint_exists(self, auth_headers):
        """Test that upcoming due dates endpoint exists and returns data"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/upcoming-due-dates",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Found {len(data)} customers with upcoming due dates")
    
    def test_upcoming_due_dates_data_structure(self, auth_headers):
        """Test data structure of upcoming due dates"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/upcoming-due-dates",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data) > 0:
            item = data[0]
            # Verify required fields
            required_fields = ["customer_id", "customer_name", "project", "unit_number", 
                             "booking_date", "due_date", "days_until_due"]
            for field in required_fields:
                assert field in item, f"Missing required field: {field}"
            
            print(f"Sample item: {item['customer_name']} - Due: {item['due_date']} ({item['days_until_due']} days)")
    
    def test_upcoming_due_dates_filtering(self, auth_headers):
        """Test that only customers within 5-day window are returned"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/upcoming-due-dates",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        for item in data:
            days = item.get("days_until_due", 999)
            # Should be within -3 to +5 days window
            assert -3 <= days <= 5, f"Customer {item['customer_name']} has {days} days - outside expected range"
            print(f"Customer {item['customer_name']}: {days} days until due")


class TestCustomersAgreementFilter:
    """Test Customers Agreement Filter"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_customers_all_agreements_filter(self, auth_headers):
        """Test customers endpoint without filter returns all"""
        response = requests.get(
            f"{BASE_URL}/api/customers",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert "total" in data
        total_all = data["total"]
        print(f"Total customers (all): {total_all}")
    
    def test_customers_upcoming_due_filter(self, auth_headers):
        """Test customers with upcoming_due filter"""
        response = requests.get(
            f"{BASE_URL}/api/customers?agreement_filter=upcoming_due",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        print(f"Customers with upcoming due: {len(data['customers'])}")
        
        # Should return filtered list
        for customer in data["customers"]:
            print(f"  - {customer.get('name')} ({customer.get('customer_id')})")
    
    def test_customers_pending_agreement_filter(self, auth_headers):
        """Test customers with pending_agreement filter"""
        response = requests.get(
            f"{BASE_URL}/api/customers?agreement_filter=pending_agreement",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        print(f"Customers with pending agreement: {len(data['customers'])}")
        
        # Should only contain draft or sent agreement status
        for customer in data["customers"]:
            status = customer.get("agreement_status", "")
            assert status in ["draft", "sent"], f"Unexpected status: {status}"
    
    def test_customers_agreement_due_filter(self, auth_headers):
        """Test customers with agreement_due filter (sent but not signed)"""
        response = requests.get(
            f"{BASE_URL}/api/customers?agreement_filter=agreement_due",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        print(f"Customers with agreement signing due: {len(data['customers'])}")


class TestDocumentDelete:
    """Test Document Delete API"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture(scope="class")
    def test_customer_id(self, auth_headers):
        """Get a customer ID for testing"""
        response = requests.get(
            f"{BASE_URL}/api/customers?limit=1",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        if data["customers"]:
            return data["customers"][0]["id"]
        pytest.skip("No customers available for testing")
    
    def test_document_delete_endpoint_exists(self, auth_headers, test_customer_id):
        """Test that delete endpoint returns appropriate response"""
        # Try to delete a non-existent document - should return 404
        fake_doc_id = "non-existent-doc-12345"
        response = requests.delete(
            f"{BASE_URL}/api/documents/{fake_doc_id}",
            headers=auth_headers
        )
        # Should return 404 for non-existent document
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Document delete endpoint exists and returns 404 for non-existent docs")
    
    def test_document_generate_and_delete(self, auth_headers, test_customer_id):
        """Test generating a document and then deleting it"""
        # First generate a document
        generate_response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            headers=auth_headers,
            json={
                "customer_id": test_customer_id,
                "doc_type": "demand_letter",
                "custom_fields": {}
            }
        )
        
        if generate_response.status_code != 200:
            pytest.skip(f"Could not generate document: {generate_response.text}")
        
        doc_data = generate_response.json()
        doc_id = doc_data.get("document", {}).get("id")
        assert doc_id, "No document ID returned"
        print(f"Generated document with ID: {doc_id}")
        
        # Now verify document exists
        docs_response = requests.get(
            f"{BASE_URL}/api/documents/{test_customer_id}",
            headers=auth_headers
        )
        assert docs_response.status_code == 200
        docs = docs_response.json()
        doc_exists = any(d.get("id") == doc_id for d in docs)
        assert doc_exists, "Generated document not found in customer's documents"
        
        # Now delete the document
        delete_response = requests.delete(
            f"{BASE_URL}/api/documents/{doc_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        print(f"Document {doc_id} deleted successfully")
        
        # Verify document no longer exists
        docs_response = requests.get(
            f"{BASE_URL}/api/documents/{test_customer_id}",
            headers=auth_headers
        )
        assert docs_response.status_code == 200
        docs = docs_response.json()
        doc_still_exists = any(d.get("id") == doc_id for d in docs)
        assert not doc_still_exists, "Document still exists after deletion"
        print("Document verified as deleted")
    
    def test_uploaded_document_delete_endpoint(self, auth_headers, test_customer_id):
        """Test that uploaded document delete endpoint returns appropriate response"""
        fake_doc_id = "non-existent-upload-12345"
        response = requests.delete(
            f"{BASE_URL}/api/customers/{test_customer_id}/documents/{fake_doc_id}",
            headers=auth_headers
        )
        # Should return 404 for non-existent document
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Uploaded document delete endpoint exists and returns 404 for non-existent docs")


class TestDashboardStats:
    """Test dashboard stats endpoint for completeness"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_dashboard_stats(self, auth_headers):
        """Test dashboard stats endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["total_customers", "pending_agreements", 
                         "payments_due_this_week", "overdue_payments"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"Dashboard stats: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
