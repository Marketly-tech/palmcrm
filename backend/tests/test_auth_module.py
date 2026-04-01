"""
Pytest tests for modular authentication routes.
Tests the auth routes module created during refactoring.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://builder-crm-dev.preview.emergentagent.com')
API_URL = f"{BASE_URL.rstrip('/')}/api"


class TestAuthModule:
    """Test suite for auth module routes."""
    
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
    
    def test_login_valid_credentials(self, session):
        """Test login with valid admin credentials."""
        response = session.post(f"{API_URL}/auth/login", json={
            "email": "crm@rrlbuildersanddevelopers.com",
            "password": "#RRLnew2026"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
    
    def test_login_invalid_credentials(self, session):
        """Test login with invalid credentials."""
        response = session.post(f"{API_URL}/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_auth_me_endpoint(self, session, admin_token):
        """Test /auth/me endpoint returns current user."""
        response = session.get(f"{API_URL}/auth/me", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "crm@rrlbuildersanddevelopers.com"
        assert data["role"] == "admin"
    
    def test_verify_email_exists(self, session):
        """Test email verification for password reset."""
        response = session.post(f"{API_URL}/auth/verify-email", json={
            "email": "crm@rrlbuildersanddevelopers.com"
        })
        assert response.status_code == 200
        assert response.json()["exists"] == True
    
    def test_verify_email_not_exists(self, session):
        """Test email verification for non-existent email."""
        response = session.post(f"{API_URL}/auth/verify-email", json={
            "email": "nonexistent@test.com"
        })
        assert response.status_code == 404
    
    def test_get_users_admin_only(self, session, admin_token):
        """Test that admin can get list of users."""
        response = session.get(f"{API_URL}/users", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0
    
    def test_protected_route_without_token(self, session):
        """Test that protected routes require authentication."""
        response = session.get(f"{API_URL}/auth/me")
        assert response.status_code == 403  # No token provided
