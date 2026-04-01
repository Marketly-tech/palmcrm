"""
Pytest tests for modular payment routes.
Tests the payments routes module created during refactoring.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://builder-crm-dev.preview.emergentagent.com')
API_URL = f"{BASE_URL.rstrip('/')}/api"


class TestPaymentsModule:
    """Test suite for payments module routes."""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create requests session."""
        return requests.Session()
    
    @pytest.fixture(scope="class")
    def admin_token(self, session):
        """Get admin JWT token."""
        response = session.post(f"{API_URL}/auth/login", json={
            "email": "crm@rrlbuildersanddevelopers.com",
            "password": "#RRLnew2026"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sample_customer_id(self, session, admin_token):
        """Get a sample customer ID for testing."""
        response = session.get(f"{API_URL}/customers?limit=1", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        return response.json()["customers"][0]["id"]
    
    # ==================== Price Calculator Tests ====================
    def test_price_calculator_basic(self, session, admin_token):
        """Test basic price calculation."""
        response = session.post(f"{API_URL}/calculator/price", 
            json={
                "saleable_area": 1200,
                "rate_per_sqft": 6500,
                "include_club_house": True
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "base_price" in data
        assert "total_flat_value" in data
        assert "club_house_charges" in data
        assert data["base_price"] == 7800000  # 1200 * 6500
    
    def test_price_calculator_with_additional_charges(self, session, admin_token):
        """Test price calculation with additional charges."""
        response = session.post(f"{API_URL}/calculator/price", 
            json={
                "saleable_area": 1000,
                "rate_per_sqft": 5000,
                "include_club_house": True,
                "club_house_charges": 250000,
                "additional_charges": 100000
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["club_house_charges"] == 250000
        assert data["additional_charges"] == 100000
    
    def test_disbursement_calculator(self, session, admin_token):
        """Test disbursement calculation."""
        response = session.post(f"{API_URL}/calculator/disbursement", 
            json={
                "total_flat_value": 10000000,
                "disbursement_percentage": 30
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["disbursement_amount"] == 3000000  # 30% of 10M
    
    # ==================== Payment Schedule Tests ====================
    def test_get_payment_schedule_template(self, session, admin_token):
        """Test getting payment schedule template."""
        response = session.get(f"{API_URL}/calculator/payment-schedule-template?total_amount=10000000", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # First installment should be 10% (booking)
        assert data[0]["percentage"] == 10
    
    def test_get_payment_schedule(self, session, admin_token, sample_customer_id):
        """Test getting payment schedule for a customer."""
        response = session.get(f"{API_URL}/payments/schedule/{sample_customer_id}", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
    
    def test_payments_overview(self, session, admin_token):
        """Test payments overview endpoint."""
        response = session.get(f"{API_URL}/payments/overview", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "pending" in data
        assert "overdue" in data
        assert "upcoming" in data
    
    # ==================== Transaction Tests ====================
    def test_get_transactions(self, session, admin_token, sample_customer_id):
        """Test getting transactions for a customer."""
        response = session.get(f"{API_URL}/transactions/{sample_customer_id}", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_transaction(self, session, admin_token, sample_customer_id):
        """Test creating a transaction."""
        response = session.post(f"{API_URL}/transactions/{sample_customer_id}", 
            json={
                "transaction_stage": "booking",
                "transaction_date": "2026-03-29",
                "bank_name": "Test Bank",
                "transaction_number": "TEST123456",
                "amount": 100000,
                "notes": "Test transaction from pytest"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "transaction" in data
        assert data["transaction"]["amount"] == 100000
