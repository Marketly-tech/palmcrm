"""
Backend Refactoring Test - Iteration 28
Tests all endpoints after server.py refactoring from ~4200 lines to ~232 lines.
Routes extracted to: auth/routes.py, customers/routes.py, payments/routes.py, 
dashboard/routes.py, documents/routes.py, email_service/routes.py, 
booking/__init__.py, settings/__init__.py
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://builder-crm-dev.preview.emergentagent.com').rstrip('/')

# Test credentials from environment variables (see /app/memory/test_credentials.md)
ADMIN_EMAIL = os.environ.get("TEST_ADMIN_EMAIL", "crm@rrlbuildersanddevelopers.com")
ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "#RRLnew2026")
ACCOUNTS_EMAIL = os.environ.get("TEST_ACCOUNTS_EMAIL", "accounts@rrlbuilders.com")
ACCOUNTS_PASSWORD = os.environ.get("TEST_ACCOUNTS_PASSWORD", "accounts123")
TEST_CUSTOMER_ID = os.environ.get("TEST_CUSTOMER_ID", "6d902613-5106-4294-bc3e-b907f85127f7")


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_api_health(self):
        """GET /api/health returns healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print(f"✓ Health check passed: {data}")


class TestAuthRoutes:
    """Test authentication routes from auth/routes.py"""
    
    def test_admin_login(self):
        """Login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful: {data['user']['name']}")
        return data["access_token"]
    
    def test_accounts_login(self):
        """Login with accounts credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ACCOUNTS_EMAIL,
            "password": ACCOUNTS_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == ACCOUNTS_EMAIL
        assert data["user"]["role"] == "accounts"
        print(f"✓ Accounts login successful: {data['user']['name']}")
        return data["access_token"]
    
    def test_invalid_login(self):
        """Login with invalid credentials should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")


class TestDashboardRoutes:
    """Test dashboard routes from dashboard/routes.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_dashboard_stats(self):
        """GET /api/dashboard/stats returns all stat fields"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        # Verify all expected fields
        assert "total_customers" in data
        assert "pending_agreements" in data
        assert "payments_due_this_week" in data
        assert "overdue_payments" in data
        assert "total_revenue" in data
        assert "total_pending" in data
        assert "total_flat_value" in data
        assert "total_balance" in data
        assert "pending_percentage" in data
        assert "monthly_revenue" in data
        assert "payment_status_breakdown" in data
        print(f"✓ Dashboard stats: {data['total_customers']} customers, {data['pending_agreements']} pending agreements")
    
    def test_recent_activities(self):
        """GET /api/dashboard/recent-activities returns list"""
        response = requests.get(f"{BASE_URL}/api/dashboard/recent-activities", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Recent activities: {len(data)} activities returned")
    
    def test_upcoming_due_dates(self):
        """GET /api/dashboard/upcoming-due-dates returns list"""
        response = requests.get(f"{BASE_URL}/api/dashboard/upcoming-due-dates", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Upcoming due dates: {len(data)} items returned")
    
    def test_overdue_by_stage(self):
        """GET /api/dashboard/overdue-by-stage returns overdue data"""
        response = requests.get(f"{BASE_URL}/api/dashboard/overdue-by-stage", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "current_stage" in data
        assert "overdue_count" in data
        assert "total_overdue_amount" in data
        assert "overdue_customers" in data
        print(f"✓ Overdue by stage: {data['overdue_count']} overdue customers")


class TestCustomerRoutes:
    """Test customer routes from customers/routes.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_customers_list(self):
        """GET /api/customers returns customer list with total count"""
        response = requests.get(f"{BASE_URL}/api/customers", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert "total" in data
        assert isinstance(data["customers"], list)
        assert data["total"] > 0
        print(f"✓ Customers list: {data['total']} total customers")
    
    def test_get_single_customer(self):
        """GET /api/customers/{id} returns single customer (Ramya test lead)"""
        response = requests.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == TEST_CUSTOMER_ID
        assert "name" in data
        assert "email" in data
        assert "phone" in data
        assert "project" in data
        print(f"✓ Single customer: {data['name']} - {data.get('project', 'N/A')}")
    
    def test_get_customer_notes(self):
        """GET /api/customers/{id}/notes returns notes list"""
        response = requests.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/notes", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Customer notes: {len(data)} notes")
    
    def test_get_customer_overdue(self):
        """GET /api/customers/{id}/overdue returns overdue info"""
        response = requests.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/overdue", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "customer_id" in data
        assert "overdue_amount" in data
        print(f"✓ Customer overdue: {data.get('overdue_amount', 0)} overdue amount")


class TestPaymentRoutes:
    """Test payment routes from payments/routes.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_transactions(self):
        """GET /api/transactions/{customer_id} returns transaction list"""
        response = requests.get(f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Transactions: {len(data)} transactions for customer")
    
    def test_get_payment_schedule(self):
        """GET /api/payments/schedule/{customer_id} returns schedule"""
        response = requests.get(f"{BASE_URL}/api/payments/schedule/{TEST_CUSTOMER_ID}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "customer_id" in data
        assert "items" in data
        print(f"✓ Payment schedule: {len(data.get('items', []))} schedule items")
    
    def test_get_payments_overview(self):
        """GET /api/payments/overview returns payment overview"""
        response = requests.get(f"{BASE_URL}/api/payments/overview", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "pending" in data
        assert "overdue" in data
        assert "upcoming" in data
        print(f"✓ Payments overview: {len(data['pending'])} pending, {len(data['overdue'])} overdue, {len(data['upcoming'])} upcoming")


class TestSettingsRoutes:
    """Test settings routes from settings/__init__.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_payment_stages(self):
        """GET /api/settings/payment-stages returns 10 stages"""
        response = requests.get(f"{BASE_URL}/api/settings/payment-stages", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10
        print(f"✓ Payment stages: {len(data)} stages returned")
    
    def test_get_current_stage(self):
        """GET /api/settings/current-stage returns current stage info"""
        response = requests.get(f"{BASE_URL}/api/settings/current-stage", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "current_stage" in data
        assert "cumulative_percentage" in data
        print(f"✓ Current stage: {data.get('current_stage_name', 'Not set')}")
    
    def test_get_projects(self):
        """GET /api/projects returns 6 projects"""
        response = requests.get(f"{BASE_URL}/api/projects", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 6
        print(f"✓ Projects: {len(data)} projects returned")
    
    def test_get_units(self):
        """GET /api/units returns units list"""
        response = requests.get(f"{BASE_URL}/api/units", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Units: {len(data)} units returned")
    
    def test_get_activity_logs(self):
        """GET /api/activity-logs returns activity logs"""
        response = requests.get(f"{BASE_URL}/api/activity-logs", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Activity logs: {len(data)} logs returned")


class TestBookingRoutes:
    """Test booking routes from booking/__init__.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_pending_leads(self):
        """GET /api/leads/pending returns pending leads"""
        response = requests.get(f"{BASE_URL}/api/leads/pending", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Pending leads: {len(data)} leads")


class TestEmailRoutes:
    """Test email routes from email_service/routes.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_email_logs(self):
        """GET /api/email-logs returns email logs with pagination"""
        response = requests.get(f"{BASE_URL}/api/email-logs", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        print(f"✓ Email logs: {data['total']} total logs")
    
    def test_get_communication_history(self):
        """GET /api/communication/{customer_id} returns communication history"""
        response = requests.get(f"{BASE_URL}/api/communication/{TEST_CUSTOMER_ID}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Communication history: {len(data)} records")
    
    def test_preview_welcome_email(self):
        """GET /api/communication/preview-welcome-email/{customer_id} returns email preview"""
        response = requests.get(f"{BASE_URL}/api/communication/preview-welcome-email/{TEST_CUSTOMER_ID}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "email_type" in data
        assert "customer_name" in data
        assert "recipient_email" in data
        assert "subject" in data
        assert "body" in data
        print(f"✓ Welcome email preview: {data['email_type']} for {data['customer_name']}")


class TestDocumentRoutes:
    """Test document routes from documents/routes.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_customer_documents(self):
        """GET /api/documents/{customer_id} returns generated documents list"""
        response = requests.get(f"{BASE_URL}/api/documents/{TEST_CUSTOMER_ID}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Generated documents: {len(data)} documents")
    
    def test_get_uploaded_documents(self):
        """GET /api/customers/{id}/documents-list returns uploaded docs"""
        response = requests.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/documents-list", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Uploaded documents: {len(data)} documents")
    
    def test_get_document_checklist(self):
        """GET /api/checklist/{customer_id} returns document checklist"""
        response = requests.get(f"{BASE_URL}/api/checklist/{TEST_CUSTOMER_ID}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "customer_id" in data
        print(f"✓ Document checklist retrieved")
    
    def test_get_templates(self):
        """GET /api/templates returns document templates"""
        response = requests.get(f"{BASE_URL}/api/templates", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Document templates: {len(data)} templates")
    
    def test_generate_document(self):
        """POST /api/documents/generate creates a document (price_breakup type)"""
        response = requests.post(f"{BASE_URL}/api/documents/generate", 
            headers=self.headers,
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "price_breakup",
                "custom_fields": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "document" in data
        print(f"✓ Document generated: {data['message']}")


class TestExportRoutes:
    """Test export routes from settings/__init__.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_export_customers_csv(self):
        """GET /api/export/customers/csv returns CSV 200"""
        response = requests.get(f"{BASE_URL}/api/export/customers/csv", headers=self.headers)
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        print(f"✓ Customers CSV export: {len(response.content)} bytes")
    
    def test_export_customers_excel(self):
        """GET /api/export/customers/excel returns Excel 200"""
        response = requests.get(f"{BASE_URL}/api/export/customers/excel", headers=self.headers)
        assert response.status_code == 200
        assert "spreadsheet" in response.headers.get("content-type", "")
        print(f"✓ Customers Excel export: {len(response.content)} bytes")
    
    def test_export_payments_csv(self):
        """GET /api/export/payments/csv returns CSV 200"""
        response = requests.get(f"{BASE_URL}/api/export/payments/csv", headers=self.headers)
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        print(f"✓ Payments CSV export: {len(response.content)} bytes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
