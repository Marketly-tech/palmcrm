"""
RRL Builders CRM API Test Suite
Tests authentication, customer management, leads, calculator, documents and communication endpoints.
"""

import pytest
import requests
import os
import uuid
from datetime import datetime
from tests.conftest_credentials import ADMIN_EMAIL, ADMIN_PASSWORD, ACCOUNTS_EMAIL, ACCOUNTS_PASSWORD, TEST_CUSTOMER_ID, API_URL, TEST_BASE_URL

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API = f"{BASE_URL}/api"

# Test credentials
TEST_EMAIL = "admin@rrlbuilders.com"
TEST_PASSWORD = ADMIN_PASSWORD

class TestAuthenticationEndpoints:
    """Test authentication and user management endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for tests"""
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{API}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_login_success(self):
        """Test successful login with valid credentials"""
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL
        assert data["user"]["role"] == "admin"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials returns 401"""
        response = requests.post(f"{API}/auth/login", json={
            "email": "wrong@email.com",
            "password": "wrongpass"
        })
        assert response.status_code == 401
    
    def test_get_current_user(self, auth_token):
        """Test GET /auth/me returns current user info"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_EMAIL
        assert "name" in data
        assert "role" in data


class TestDashboardEndpoints:
    """Test dashboard statistics and activity endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_dashboard_stats(self, auth_token):
        """Test dashboard statistics endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/dashboard/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Verify all expected stat fields exist
        assert "total_customers" in data
        assert "pending_agreements" in data
        assert "payments_due_this_week" in data
        assert "overdue_payments" in data
        assert "total_revenue" in data
    
    def test_recent_activities(self, auth_token):
        """Test recent activities endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/dashboard/recent-activities", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestPublicBookingForm:
    """Test public booking form submission (no auth required)"""
    
    def test_submit_booking_form_success(self):
        """Test booking form submission creates pending lead"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "name": "TEST_Booking Customer",
            "phone": "9876543210",
            "email": unique_email,
            "project": "RRL Palm Altezze",
            "tower": "Tower-1",
            "unit_number": f"TEST-{uuid.uuid4().hex[:4]}",
            "father_name": "Test Father",
            "pan_number": "ABCDE1234F",
            "booking_amount": 200000,
            "booking_date": datetime.now().strftime("%Y-%m-%d"),
            "finance_type": "self",
            "remarks": "Test booking from API test"
        }
        response = requests.post(f"{API}/public/booking-form", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "customer_id" in data
        assert data["customer_id"].startswith("RRL-")
        assert "message" in data
    
    def test_submit_booking_form_validation(self):
        """Test booking form validation - missing required fields"""
        # Missing required email
        payload = {
            "name": "Test",
            "phone": "123",
            "project": "Test",
            "tower": "T1",
            "unit_number": "001"
        }
        response = requests.post(f"{API}/public/booking-form", json=payload)
        assert response.status_code == 422  # Validation error


class TestLeadsManagement:
    """Test leads approval/rejection workflow"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def test_lead(self, auth_token):
        """Create a test lead via booking form"""
        unique_email = f"test_lead_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "name": "TEST_Lead for Approval",
            "phone": "9876543210",
            "email": unique_email,
            "project": "RRL Palm Altezze",
            "tower": "Tower-1",
            "unit_number": f"LT-{uuid.uuid4().hex[:4]}",
            "booking_amount": 100000
        }
        response = requests.post(f"{API}/public/booking-form", json=payload)
        return response.json()
    
    def test_get_pending_leads(self, auth_token):
        """Test fetching pending leads list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/leads/pending", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_approve_lead(self, auth_token, test_lead):
        """Test lead approval workflow"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        customer_id = test_lead["reference_id"]
        
        response = requests.put(f"{API}/leads/{customer_id}/approve", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify stage changed
        get_response = requests.get(f"{API}/customers/{customer_id}", headers=headers)
        if get_response.status_code == 200:
            customer = get_response.json()
            assert customer.get("stage") == "qualified"


class TestCustomerCRUD:
    """Test customer CRUD operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def created_customer(self, auth_token):
        """Create a customer for tests"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "name": "TEST_CRUD Customer",
            "phone": "9876543210",
            "email": f"test_crud_{uuid.uuid4().hex[:8]}@example.com",
            "project": "RRL Palm Altezze",
            "tower": "Tower-1",
            "unit_number": f"CRUD-{uuid.uuid4().hex[:4]}",
            "bhk_type": "3BHK",
            "saleable_area": 1630,
            "rate_per_sqft": 6600,
            "base_price": 10758000,
            "gst_amount": 537900,
            "total_price": 11295900,
            "stage": "qualified"
        }
        response = requests.post(f"{API}/customers", json=payload, headers=headers)
        return response.json()
    
    def test_create_customer(self, auth_token):
        """Test customer creation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "name": "TEST_New Customer",
            "phone": "8765432109",
            "email": f"test_new_{uuid.uuid4().hex[:8]}@example.com",
            "project": "RRL NC 216",
            "tower": "Tower-A",
            "unit_number": f"NC-{uuid.uuid4().hex[:4]}",
            "stage": "qualified"
        }
        response = requests.post(f"{API}/customers", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "customer_id" in data
        assert data["name"] == payload["name"]
    
    def test_get_customers_list(self, auth_token):
        """Test fetching customers list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/customers", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert "total" in data
        assert isinstance(data["customers"], list)
    
    def test_get_customer_by_id(self, auth_token, created_customer):
        """Test fetching single customer by ID"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        customer_id = created_customer["id"]
        response = requests.get(f"{API}/customers/{customer_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == customer_id
        assert data["name"] == "TEST_CRUD Customer"
    
    def test_update_customer(self, auth_token, created_customer):
        """Test customer update"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        customer_id = created_customer["id"]
        update_payload = {
            "remarks": "Updated from API test"
        }
        response = requests.put(f"{API}/customers/{customer_id}", json=update_payload, headers=headers)
        assert response.status_code == 200
        
        # Verify update
        get_response = requests.get(f"{API}/customers/{customer_id}", headers=headers)
        assert get_response.status_code == 200
        updated = get_response.json()
        assert updated["remarks"] == "Updated from API test"


class TestPriceCalculator:
    """Test price calculator endpoints"""
    
    def test_calculate_price_basic(self):
        """Test basic price calculation"""
        payload = {
            "saleable_area": 1630,
            "rate_per_sqft": 6600,
            "include_club_house": True,
            "club_house_charges": 200000,
            "additional_parking_count": 0,
            "gst_percentage": 5,
            "labour_cess_percentage": 0.70
        }
        response = requests.post(f"{API}/calculator/price", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify calculations
        assert data["base_price"] == 1630 * 6600  # 10,758,000
        assert data["club_house_charges"] == 200000
        assert data["subtotal_before_taxes"] == 10758000 + 200000  # 10,958,000
        assert "labour_cess" in data
        assert "gst_amount" in data
        assert "total_flat_value" in data
        assert "uds" in data
    
    def test_calculate_price_with_parking(self):
        """Test price calculation with additional parking"""
        payload = {
            "saleable_area": 1630,
            "rate_per_sqft": 6600,
            "include_club_house": True,
            "additional_parking_count": 2,
            "additional_parking_rate": 300000
        }
        response = requests.post(f"{API}/calculator/price", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["additional_parking_charges"] == 600000  # 2 * 300000
    
    def test_calculate_disbursement(self):
        """Test disbursement calculation"""
        payload = {
            "total_flat_value": 11295900,
            "disbursement_percentage": 30
        }
        response = requests.post(f"{API}/calculator/disbursement", json=payload)
        assert response.status_code == 200
        data = response.json()
        expected = 11295900 * 0.30
        assert abs(data["disbursement_amount"] - expected) < 1  # Allow rounding
    
    def test_calculate_payment_tracking(self):
        """Test payment tracking calculation"""
        response = requests.post(
            f"{API}/calculator/payment-tracking?total_flat_value=11295900&total_received=2000000"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_flat_value"] == 11295900
        assert data["total_received"] == 2000000
        assert data["balance_amount"] == 11295900 - 2000000
        assert "payment_received_percentage" in data
        assert "payment_pending_percentage" in data
    
    def test_payment_schedule_template(self):
        """Test payment schedule template generation"""
        response = requests.get(f"{API}/calculator/payment-schedule-template?total_amount=11295900")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 13  # 13 milestones
        
        # Verify structure of first item
        assert "installment_name" in data[0]
        assert "percentage" in data[0]
        assert "milestone" in data[0]
        assert "amount" in data[0]


class TestDocumentsAndCommunication:
    """Test document generation and communication endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def test_customer(self, auth_token):
        """Create test customer for document tests"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "name": "TEST_Doc Customer",
            "phone": "9876543210",
            "email": f"test_doc_{uuid.uuid4().hex[:8]}@example.com",
            "project": "RRL Palm Altezze",
            "tower": "Tower-1",
            "unit_number": f"DOC-{uuid.uuid4().hex[:4]}",
            "bhk_type": "3BHK",
            "saleable_area": 1630,
            "rate_per_sqft": 6600,
            "base_price": 10758000,
            "club_house_charges": 200000,
            "gst_amount": 537900,
            "total_price": 11295900,
            "stage": "qualified"
        }
        response = requests.post(f"{API}/customers", json=payload, headers=headers)
        return response.json()
    
    def test_send_welcome_email(self, auth_token, test_customer):
        """Test welcome email sending (MOCKED)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        customer_id = test_customer["id"]
        
        response = requests.post(
            f"{API}/communication/send-welcome-email/{customer_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "MOCKED" in data["message"]
        assert "welcome_html" in data
        assert "price_breakup_html" in data
    
    def test_generate_price_breakup_pdf(self, auth_token, test_customer):
        """Test price breakup PDF generation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        customer_id = test_customer["id"]
        
        response = requests.post(
            f"{API}/documents/generate-pdf/{customer_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "html_content" in data
        assert "filename" in data
        assert "RRL_PalmAltezze_PriceBreakup" in data["filename"]
    
    def test_get_customer_documents(self, auth_token, test_customer):
        """Test fetching customer documents"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        customer_id = test_customer["id"]
        
        response = requests.get(
            f"{API}/documents/{customer_id}",
            headers=headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_checklist(self, auth_token, test_customer):
        """Test document checklist retrieval"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        customer_id = test_customer["id"]
        
        response = requests.get(f"{API}/checklist/{customer_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
    
    def test_get_communication_history(self, auth_token, test_customer):
        """Test communication history retrieval"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        customer_id = test_customer["id"]
        
        response = requests.get(
            f"{API}/communication/{customer_id}",
            headers=headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestPaymentSchedule:
    """Test payment schedule management"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def test_customer_for_payment(self, auth_token):
        """Create customer with total price for payment schedule"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "name": "TEST_Payment Customer",
            "phone": "9876543210",
            "email": f"test_pay_{uuid.uuid4().hex[:8]}@example.com",
            "project": "RRL Palm Altezze",
            "tower": "Tower-1",
            "unit_number": f"PAY-{uuid.uuid4().hex[:4]}",
            "total_price": 11295900,
            "stage": "qualified"
        }
        response = requests.post(f"{API}/customers", json=payload, headers=headers)
        return response.json()
    
    def test_auto_generate_payment_schedule(self, auth_token, test_customer_for_payment):
        """Test auto-generating payment schedule from template"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        customer_id = test_customer_for_payment["id"]
        
        response = requests.post(
            f"{API}/calculator/generate-schedule/{customer_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "schedule" in data
        assert "items" in data["schedule"]
        assert len(data["schedule"]["items"]) == 13
    
    def test_get_payment_schedule(self, auth_token, test_customer_for_payment):
        """Test retrieving payment schedule"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        customer_id = test_customer_for_payment["id"]
        
        response = requests.get(
            f"{API}/payments/schedule/{customer_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestProjectsAndUnits:
    """Test project and unit pricing endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_get_projects(self, auth_token):
        """Test fetching projects list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/projects", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_units(self, auth_token):
        """Test fetching units list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{API}/units", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Returns list directly when no units exist
        assert isinstance(data, list) or "units" in data


# Run cleanup at the end
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Cleanup test data after all tests"""
    yield
    # Note: In production, add cleanup of TEST_ prefixed data
    print("Test suite completed")
