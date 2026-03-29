"""
Pytest tests for modular dashboard routes.
Tests the dashboard routes module created during refactoring.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://modular-crm-build-1.preview.emergentagent.com')
API_URL = f"{BASE_URL.rstrip('/')}/api"


class TestDashboardModule:
    """Test suite for dashboard module routes."""
    
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
    def accounts_token(self, session):
        """Get accounts role JWT token."""
        response = session.post(f"{API_URL}/auth/login", json={
            "email": "accounts@rrlbuilders.com",
            "password": "accounts123"
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    
    def test_dashboard_stats_admin(self, session, admin_token):
        """Test dashboard stats for admin user."""
        response = session.get(f"{API_URL}/dashboard/stats", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected fields are present
        assert "total_customers" in data
        assert "pending_agreements" in data
        assert "payments_due_this_week" in data
        assert "overdue_payments" in data
        assert "total_revenue" in data
        assert "total_pending" in data
        assert "total_flat_value" in data
        assert "total_balance" in data
        assert "payment_status_breakdown" in data
        
        # Admin should see revenue data
        assert data["total_customers"] >= 35  # At least 35 customers
    
    def test_dashboard_stats_non_admin(self, session, accounts_token):
        """Test dashboard stats for non-admin user (should hide revenue)."""
        if accounts_token is None:
            pytest.skip("Accounts user not available")
        
        response = session.get(f"{API_URL}/dashboard/stats", 
            headers={"Authorization": f"Bearer {accounts_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Non-admin should see 0 for revenue fields
        assert data["total_revenue"] == 0
        assert data["total_pending"] == 0
    
    def test_dashboard_recent_activities(self, session, admin_token):
        """Test recent activities endpoint."""
        response = session.get(f"{API_URL}/dashboard/recent-activities?limit=10", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_dashboard_upcoming_due_dates(self, session, admin_token):
        """Test upcoming due dates endpoint."""
        response = session.get(f"{API_URL}/dashboard/upcoming-due-dates", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_dashboard_stats_requires_auth(self, session):
        """Test that dashboard stats requires authentication."""
        response = session.get(f"{API_URL}/dashboard/stats")
        assert response.status_code == 403  # No token provided
    
    def test_dashboard_customer_count_accuracy(self, session, admin_token):
        """Test that dashboard customer count matches actual customers."""
        # Get dashboard stats
        stats_response = session.get(f"{API_URL}/dashboard/stats", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        stats_count = stats_response.json()["total_customers"]
        
        # Get customers list
        customers_response = session.get(f"{API_URL}/customers", 
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        actual_count = customers_response.json()["total"]
        
        assert stats_count == actual_count
