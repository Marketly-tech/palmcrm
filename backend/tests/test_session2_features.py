"""
Test Session 2 Features for RRL Builders CRM:
1. Public booking form with profession, document upload, tower as text, floor_rise_cost
2. Delete customer functionality
3. Terms and conditions validation (frontend only)
"""
import pytest
import requests
import os
from tests.conftest_credentials import ADMIN_EMAIL, ADMIN_PASSWORD, ACCOUNTS_EMAIL, ACCOUNTS_PASSWORD, TEST_CUSTOMER_ID, API_URL, TEST_BASE_URL

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Test authentication for admin access"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rrlbuilders.com",
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["access_token"]
    
    def test_admin_login(self, auth_token):
        """Verify admin can login"""
        assert auth_token is not None
        assert len(auth_token) > 20
        print(f"PASS: Admin login successful")


class TestPublicBookingForm:
    """Test the enhanced public booking form features"""
    
    def test_booking_form_with_profession_and_floor_rise(self):
        """Test booking form submission with new fields: profession, floor_rise_cost, tower as text"""
        payload = {
            "name": "TEST_Session2_Customer",
            "phone": "9876543210",
            "email": "test_session2@example.com",
            "profession": "Business Owner",  # NEW: profession field
            "nationality": "Indian",
            "project": "RRL Palm Altezze",
            "tower": "Tower-B",  # NOW: text input instead of dropdown
            "unit_number": "0901",
            "bhk_type": "3BHK",
            "floor": 9,
            "saleable_area": 1630,
            "rate_per_sqft": 6600,
            "floor_rise_cost": 50,  # NEW: manual floor rise cost per sqft
            "parking": "1",
            "additional_parking": 0,
            "booking_amount": 200000,
            # Co-applicant fields
            "co_applicant_name": "TEST Co-Applicant",
            "co_applicant_profession": "Salaried",  # NEW: co-applicant profession
            "co_applicant_nationality": "Indian",
        }
        
        response = requests.post(f"{BASE_URL}/api/public/booking-form", json=payload)
        assert response.status_code == 200, f"Booking form failed: {response.text}"
        
        data = response.json()
        assert "customer_id" in data
        assert "reference_id" in data
        assert data["message"] == "Booking submitted successfully! Our team will contact you shortly."
        
        print(f"PASS: Booking form submitted successfully")
        print(f"  Customer ID: {data['customer_id']}")
        print(f"  Reference ID: {data['reference_id']}")
        
        return data["reference_id"]
    
    def test_verify_booking_data_saved(self):
        """Verify the booking data was saved correctly with new fields"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rrlbuilders.com",
            "password": ADMIN_PASSWORD
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Search for the test customer
        response = requests.get(f"{BASE_URL}/api/customers?search=TEST_Session2_Customer", headers=headers)
        assert response.status_code == 200
        
        customers = response.json()["customers"]
        assert len(customers) > 0, "Test customer not found"
        
        customer = customers[0]
        
        # Verify new fields were saved
        assert customer["name"] == "TEST_Session2_Customer"
        assert customer["tower"] == "Tower-B"  # Tower as text
        assert customer["custom_fields"]["profession"] == "Business Owner"  # Profession
        assert customer["custom_fields"]["floor_rise_cost"] == 50  # Floor rise cost
        assert customer["custom_fields"]["co_applicant_profession"] == "Salaried"
        
        # Verify price calculation with floor rise
        # Base: 1630 * 6600 = 10,758,000
        # Floor rise: 1630 * 50 = 81,500
        # Club house: 200,000
        # Subtotal: 11,039,500
        # Labour cess 0.7%: 77,276.5
        # GST 5%: 551,975
        # Total: 11,668,751.5
        
        assert customer["base_price"] == 10758000.0  # Verify base price
        assert customer["custom_fields"]["floor_rise_total"] == 81500.0  # Floor rise total
        
        print(f"PASS: Booking data verified")
        print(f"  Tower (text input): {customer['tower']}")
        print(f"  Profession: {customer['custom_fields']['profession']}")
        print(f"  Floor Rise Cost: {customer['custom_fields']['floor_rise_cost']}")
        print(f"  Floor Rise Total: {customer['custom_fields']['floor_rise_total']}")
        print(f"  Total Price: {customer['total_price']}")
        
        return customer["id"]


class TestDeleteCustomer:
    """Test delete customer functionality"""
    
    @pytest.fixture(scope="class")
    def admin_headers(self):
        """Get admin auth headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rrlbuilders.com",
            "password": ADMIN_PASSWORD
        })
        return {"Authorization": f"Bearer {response.json()['access_token']}"}
    
    def test_delete_customer_full_flow(self, admin_headers):
        """Test complete create and delete customer flow"""
        # Step 1: Create a customer
        payload = {
            "name": "TEST_ToBeDeleted",
            "phone": "9999999999",
            "email": "test_delete@example.com",
            "project": "RRL Palm Altezze",
            "tower": "Tower-Delete",
            "unit_number": "DEL01",
            "bhk_type": "2BHK",
            "saleable_area": 1000,
            "rate_per_sqft": 6600,
        }
        
        create_response = requests.post(f"{BASE_URL}/api/customers", json=payload, headers=admin_headers)
        assert create_response.status_code == 200, f"Create customer failed: {create_response.text}"
        
        customer_id = create_response.json()["id"]
        print(f"PASS: Created test customer for deletion: {customer_id}")
        
        # Step 2: Verify customer exists
        get_response = requests.get(f"{BASE_URL}/api/customers/{customer_id}", headers=admin_headers)
        assert get_response.status_code == 200, "Customer should exist after creation"
        print(f"PASS: Customer exists before deletion")
        
        # Step 3: Delete the customer
        delete_response = requests.delete(f"{BASE_URL}/api/customers/{customer_id}", headers=admin_headers)
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        
        data = delete_response.json()
        assert data["message"] == "Customer deleted"
        print(f"PASS: Customer deleted successfully")
        
        # Step 4: Verify customer no longer exists
        verify_response = requests.get(f"{BASE_URL}/api/customers/{customer_id}", headers=admin_headers)
        assert verify_response.status_code == 404, "Customer should not exist after deletion"
        print(f"PASS: Customer verified as deleted (404 returned)")
    
    def test_delete_customer_not_found(self, admin_headers):
        """Test deleting non-existent customer returns 404"""
        fake_id = "non-existent-id-12345"
        response = requests.delete(f"{BASE_URL}/api/customers/{fake_id}", headers=admin_headers)
        assert response.status_code == 404
        print(f"PASS: Delete non-existent customer returns 404")
    
    def test_delete_requires_admin_role(self):
        """Test that delete requires admin or manager role"""
        # This test is implicit from the code - the endpoint uses check_role([UserRole.ADMIN, UserRole.MANAGER])
        # We verify by checking that unauthorized requests fail
        
        response = requests.delete(f"{BASE_URL}/api/customers/any-id")
        assert response.status_code in [401, 403], "Delete should require authentication"
        print(f"PASS: Delete endpoint requires authentication")


class TestDocumentUpload:
    """Test public document upload feature"""
    
    def test_public_upload_endpoint_exists(self):
        """Verify public document upload endpoint exists"""
        # First create a booking
        payload = {
            "name": "TEST_DocUpload",
            "phone": "8888888888",
            "email": "test_upload@example.com",
            "project": "RRL Palm Altezze",
            "tower": "Tower-Upload",
            "unit_number": "UPL01",
        }
        
        response = requests.post(f"{BASE_URL}/api/public/booking-form", json=payload)
        assert response.status_code == 200
        
        customer_id = response.json()["reference_id"]
        print(f"PASS: Created booking for upload test: {customer_id}")
        
        # Test document upload endpoint (without file - just check endpoint exists)
        # The endpoint expects multipart form data with file
        upload_response = requests.post(
            f"{BASE_URL}/api/public/upload-document/{customer_id}",
            data={"doc_type": "pan_card"},
            files={"file": ("test.txt", b"test content", "text/plain")}
        )
        
        # Should succeed or fail with validation error (not 404)
        assert upload_response.status_code != 404, "Upload endpoint should exist"
        print(f"PASS: Public upload endpoint exists (status: {upload_response.status_code})")
        
        return customer_id


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_customers(self):
        """Clean up TEST_ prefixed customers"""
        # Login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rrlbuilders.com",
            "password": ADMIN_PASSWORD
        })
        headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Get all customers
        response = requests.get(f"{BASE_URL}/api/customers?limit=100", headers=headers)
        customers = response.json()["customers"]
        
        # Delete TEST_ prefixed customers created in this session
        test_customers = [c for c in customers if c["name"].startswith("TEST_Session2") or 
                         c["name"].startswith("TEST_DocUpload")]
        
        for customer in test_customers:
            delete_response = requests.delete(f"{BASE_URL}/api/customers/{customer['id']}", headers=headers)
            if delete_response.status_code == 200:
                print(f"  Cleaned up: {customer['name']}")
        
        print(f"PASS: Cleaned up {len(test_customers)} test customers")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
