"""
Test suite for Booking ID Import feature
Tests the booking_number field imported from Excel spreadsheet
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://builder-crm-dev.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASSWORD = "#RRLnew2026"

# Test customer IDs
SOVARAJ_PRUSTY_ID = "c514f446-bb16-43b2-bd37-faf767006024"
RAMYA_TEST_ID = "6d902613-5106-4294-bc3e-b907f85127f7"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for API calls"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Create authenticated API client"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    })
    return session


class TestBookingIdImport:
    """Tests for booking_number field imported from Excel"""
    
    def test_sovaraj_prusty_booking_number(self, api_client):
        """Test SOVARAJ PRUSTY has correct booking_number RRL PAB035"""
        response = api_client.get(f"{BASE_URL}/api/customers/{SOVARAJ_PRUSTY_ID}")
        assert response.status_code == 200
        
        customer = response.json()
        assert customer["booking_number"] == "RRL PAB035", f"Expected RRL PAB035, got {customer.get('booking_number')}"
    
    def test_sovaraj_prusty_booking_amount(self, api_client):
        """Test SOVARAJ PRUSTY has booking_amount=200000"""
        response = api_client.get(f"{BASE_URL}/api/customers/{SOVARAJ_PRUSTY_ID}")
        assert response.status_code == 200
        
        customer = response.json()
        assert customer["booking_amount"] == 200000, f"Expected 200000, got {customer.get('booking_amount')}"
    
    def test_sovaraj_prusty_booking_date(self, api_client):
        """Test SOVARAJ PRUSTY has booking_date=2026-02-28"""
        response = api_client.get(f"{BASE_URL}/api/customers/{SOVARAJ_PRUSTY_ID}")
        assert response.status_code == 200
        
        customer = response.json()
        assert customer["booking_date"] == "2026-02-28", f"Expected 2026-02-28, got {customer.get('booking_date')}"
    
    def test_sovaraj_prusty_agreement_date(self, api_client):
        """Test SOVARAJ PRUSTY has agreement_date=2026-02-24"""
        response = api_client.get(f"{BASE_URL}/api/customers/{SOVARAJ_PRUSTY_ID}")
        assert response.status_code == 200
        
        customer = response.json()
        assert customer["agreement_date"] == "2026-02-24", f"Expected 2026-02-24, got {customer.get('agreement_date')}"
    
    def test_sovaraj_prusty_remarks(self, api_client):
        """Test SOVARAJ PRUSTY has imported remarks from Excel"""
        response = api_client.get(f"{BASE_URL}/api/customers/{SOVARAJ_PRUSTY_ID}")
        assert response.status_code == 200
        
        customer = response.json()
        assert customer["remarks"] is not None, "Remarks should not be None"
        assert "EXCLUDING" in customer["remarks"], f"Expected remarks to contain 'EXCLUDING', got {customer.get('remarks')}"


class TestSearchByBookingNumber:
    """Tests for search functionality with booking_number"""
    
    def test_search_by_booking_number_pab035(self, api_client):
        """Test search by booking number PAB035 returns SOVARAJ PRUSTY"""
        response = api_client.get(f"{BASE_URL}/api/customers?search=PAB035")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 1, "Should find at least 1 customer"
        
        # Check that SOVARAJ PRUSTY is in results
        customer_names = [c["name"] for c in data["customers"]]
        assert any("SOVARAJ" in name for name in customer_names), f"SOVARAJ PRUSTY not found in search results: {customer_names}"
    
    def test_search_by_booking_number_pab001(self, api_client):
        """Test search by booking number PAB001"""
        response = api_client.get(f"{BASE_URL}/api/customers?search=PAB001")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 1, "Should find at least 1 customer"
        
        # Check booking_number in results
        booking_numbers = [c.get("booking_number") for c in data["customers"]]
        assert any("PAB001" in bn for bn in booking_numbers if bn), f"PAB001 not found in results: {booking_numbers}"


class TestAllCustomersHaveBookingNumber:
    """Tests to verify all customers have booking_number assigned"""
    
    def test_all_customers_have_booking_number(self, api_client):
        """Test all 37 customers have a booking_number assigned"""
        response = api_client.get(f"{BASE_URL}/api/customers?limit=100")
        assert response.status_code == 200
        
        data = response.json()
        customers = data["customers"]
        
        # Check total count
        assert data["total"] == 37, f"Expected 37 customers, got {data['total']}"
        
        # Check all have booking_number
        missing_booking_number = [c["name"] for c in customers if not c.get("booking_number")]
        assert len(missing_booking_number) == 0, f"Customers without booking_number: {missing_booking_number}"
    
    def test_booking_numbers_follow_pattern(self, api_client):
        """Test booking numbers follow RRL PAB pattern"""
        response = api_client.get(f"{BASE_URL}/api/customers?limit=100")
        assert response.status_code == 200
        
        data = response.json()
        customers = data["customers"]
        
        # Check pattern
        for customer in customers:
            booking_number = customer.get("booking_number", "")
            assert booking_number.startswith("RRL PAB"), f"Invalid booking number format for {customer['name']}: {booking_number}"


class TestRamyaTestLead:
    """Tests for Ramya test lead customer"""
    
    def test_ramya_has_booking_number(self, api_client):
        """Test Ramya test lead has booking_number assigned"""
        response = api_client.get(f"{BASE_URL}/api/customers/{RAMYA_TEST_ID}")
        assert response.status_code == 200
        
        customer = response.json()
        assert customer["booking_number"] == "RRL PAB-TEST", f"Expected RRL PAB-TEST, got {customer.get('booking_number')}"
    
    def test_ramya_customer_id_still_exists(self, api_client):
        """Test Ramya still has customer_id (internal ID)"""
        response = api_client.get(f"{BASE_URL}/api/customers/{RAMYA_TEST_ID}")
        assert response.status_code == 200
        
        customer = response.json()
        assert customer["customer_id"] is not None, "customer_id should still exist"
        assert customer["customer_id"].startswith("RRL-"), f"customer_id should start with RRL-, got {customer.get('customer_id')}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
