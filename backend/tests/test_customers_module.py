"""
Pytest tests for modular customer routes.
Tests the customers routes module created during refactoring.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://builder-crm-dev.preview.emergentagent.com')
API_URL = f"{BASE_URL.rstrip('/')}/api"


class TestCustomersModule:
    """Test suite for customers module routes."""
    
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
    
    def test_get_customers_list(self, session, admin_token):
        """Test getting customer list."""
        response = session.get(f"{API_URL}/customers", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert "total" in data
        assert data["total"] >= 35  # Should have at least 35 imported customers
    
    def test_get_customers_with_search(self, session, admin_token):
        """Test customer search functionality."""
        response = session.get(f"{API_URL}/customers?search=JAYANTHI", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["customers"]) >= 1
        assert "JAYANTHI" in data["customers"][0]["name"]
    
    def test_get_customers_with_project_filter(self, session, admin_token):
        """Test customer project filter."""
        response = session.get(f"{API_URL}/customers?project=RRL%20Palm%20Altezze", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        for customer in data["customers"]:
            assert customer["project"] == "RRL Palm Altezze"
    
    def test_get_customer_detail(self, session, admin_token):
        """Test getting single customer detail."""
        # First get a customer ID
        list_response = session.get(f"{API_URL}/customers?limit=1", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        customer_id = list_response.json()["customers"][0]["id"]
        
        # Get customer detail
        response = session.get(f"{API_URL}/customers/{customer_id}", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "email" in data
        assert "project" in data
    
    def test_get_nonexistent_customer(self, session, admin_token):
        """Test 404 for non-existent customer."""
        response = session.get(f"{API_URL}/customers/nonexistent-id-123", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 404
    
    def test_update_customer(self, session, admin_token):
        """Test updating customer."""
        # First get a customer ID
        list_response = session.get(f"{API_URL}/customers?limit=1", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        customer_id = list_response.json()["customers"][0]["id"]
        
        # Update customer
        response = session.put(f"{API_URL}/customers/{customer_id}", 
            json={"remarks": "Test update from pytest"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Customer updated"
