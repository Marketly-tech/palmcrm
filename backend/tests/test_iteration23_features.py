"""
Iteration 23 - Testing New Features:
1. Co-applicant details in Price Breakup document
2. Co-applicant details in Payment Schedule PDF (generate_payment_schedule_pdf_html)
3. Co-applicant name in Payment Schedule HTML (generate_payment_schedule_html)
4. Terms & Conditions uses format_customer_names - NOTE: terms_conditions NOT in DocumentType enum
5. Dashboard Payment Stage dropdown for admins
6. Transaction Export PDF endpoint
"""
import pytest
import requests
import os

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://builder-crm-dev.preview.emergentagent.com').rstrip('/')
API = f"{BASE_URL}/api"

# Test credentials
ADMIN_EMAIL = "crm@rrlbuildersanddevelopers.com"
ADMIN_PASSWORD = "#RRLnew2026"
TEST_CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"  # Ramya test lead with co-applicant


class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    def test_login_success(self, auth_token):
        """Test admin login works"""
        assert auth_token is not None
        assert len(auth_token) > 0
        print(f"✓ Admin login successful, token length: {len(auth_token)}")


class TestCustomerWithCoApplicant:
    """Test that test customer has co-applicant data"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_customer_has_co_applicant(self, headers):
        """Verify test customer has co-applicant details"""
        response = requests.get(f"{API}/customers/{TEST_CUSTOMER_ID}", headers=headers)
        assert response.status_code == 200, f"Failed to get customer: {response.text}"
        
        customer = response.json()
        # Use strip() to handle trailing spaces
        assert customer.get("name", "").strip() == "Ramya test lead", f"Wrong customer: {customer.get('name')}"
        assert customer.get("co_applicant_name") == "Marketly", f"Co-applicant name missing or wrong: {customer.get('co_applicant_name')}"
        assert customer.get("co_applicant_email") == "marketlytech@gmail.com", f"Co-applicant email wrong: {customer.get('co_applicant_email')}"
        
        print(f"✓ Customer '{customer.get('name').strip()}' has co-applicant: {customer.get('co_applicant_name')}")
        print(f"  Co-applicant email: {customer.get('co_applicant_email')}")
        print(f"  Co-applicant phone: {customer.get('co_applicant_phone', 'N/A')}")


class TestDocumentTemplatesWithCoApplicant:
    """Test document templates include co-applicant details"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_price_breakup_has_co_applicant(self, headers):
        """Test Price Breakup document shows co-applicant Name, Phone, Email"""
        response = requests.post(f"{API}/documents/generate", 
            headers=headers,
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "price_breakup"}
        )
        assert response.status_code == 200, f"Failed to generate price_breakup: {response.text}"
        
        data = response.json()
        # Response structure is {"document": {..., "content": "..."}, "message": "..."}
        html_content = data.get("document", {}).get("content", "")
        
        # Check for co-applicant section
        assert "Co-Applicant Details" in html_content, "Co-Applicant Details section missing in price_breakup"
        assert "Marketly" in html_content, "Co-applicant name 'Marketly' not found in price_breakup"
        assert "marketlytech@gmail.com" in html_content, "Co-applicant email not found in price_breakup"
        
        print("✓ Price Breakup document contains co-applicant details")
        print("  - Co-Applicant Details section: FOUND")
        print("  - Co-applicant name 'Marketly': FOUND")
        print("  - Co-applicant email: FOUND")
    
    def test_payment_schedule_pdf_has_co_applicant(self, headers):
        """Test Payment Schedule PDF shows co-applicant Name, Phone, Email"""
        response = requests.post(f"{API}/documents/generate", 
            headers=headers,
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "payment_schedule"}
        )
        assert response.status_code == 200, f"Failed to generate payment_schedule: {response.text}"
        
        data = response.json()
        html_content = data.get("document", {}).get("content", "")
        
        # Check for co-applicant section
        assert "Co-Applicant" in html_content, "Co-Applicant section missing in payment_schedule"
        assert "Marketly" in html_content, "Co-applicant name 'Marketly' not found in payment_schedule"
        
        print("✓ Payment Schedule PDF contains co-applicant details")
    
    def test_terms_conditions_not_in_api(self, headers):
        """
        NOTE: terms_conditions is NOT in DocumentType enum.
        The template exists but is not exposed via the API.
        This test documents the missing feature.
        """
        response = requests.post(f"{API}/documents/generate", 
            headers=headers,
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "terms_conditions"}
        )
        # Expected to fail with 422 because terms_conditions is not a valid doc_type
        assert response.status_code == 422, f"Expected 422 for invalid doc_type, got {response.status_code}"
        
        print("⚠ ISSUE: terms_conditions document type NOT in API DocumentType enum")
        print("  The template file exists at /app/backend/documents/templates/terms_conditions.py")
        print("  But it's not exposed via POST /api/documents/generate")
        print("  Main agent needs to add 'terms_conditions' to DocumentType enum and handle it")


class TestPaymentStageSettings:
    """Test Dashboard Payment Stage dropdown functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_payment_stages(self, headers):
        """Test GET /api/settings/payment-stages returns array of stages"""
        response = requests.get(f"{API}/settings/payment-stages", headers=headers)
        assert response.status_code == 200, f"Failed to get payment stages: {response.text}"
        
        stages = response.json()
        assert isinstance(stages, list), "Response should be a list"
        assert len(stages) > 0, "Should have at least one payment stage"
        
        # Check structure of first stage
        first_stage = stages[0]
        assert "key" in first_stage, "Stage should have 'key'"
        assert "name" in first_stage, "Stage should have 'name'"
        assert "cumulative" in first_stage, "Stage should have 'cumulative'"
        
        print(f"✓ GET /api/settings/payment-stages returns {len(stages)} stages")
        print(f"  First stage: {first_stage['name']} ({first_stage['cumulative']}%)")
    
    def test_get_current_stage(self, headers):
        """Test GET /api/settings/current-stage returns current stage info"""
        response = requests.get(f"{API}/settings/current-stage", headers=headers)
        assert response.status_code == 200, f"Failed to get current stage: {response.text}"
        
        data = response.json()
        # May be empty if no stage set, or have current_stage key
        print(f"✓ GET /api/settings/current-stage returns: {data}")
    
    def test_set_current_stage(self, headers):
        """Test POST /api/settings/current-stage sets the stage (admin only)"""
        # Set to podium stage
        response = requests.post(f"{API}/settings/current-stage", 
            headers=headers,
            json={"current_stage": "podium"}
        )
        assert response.status_code == 200, f"Failed to set current stage: {response.text}"
        
        # Verify it was set
        verify_response = requests.get(f"{API}/settings/current-stage", headers=headers)
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data.get("current_stage") == "podium", f"Stage not set correctly: {data}"
        
        print("✓ POST /api/settings/current-stage successfully sets stage to 'podium'")
    
    def test_get_overdue_by_stage(self, headers):
        """Test GET /api/dashboard/overdue-by-stage returns overdue data"""
        response = requests.get(f"{API}/dashboard/overdue-by-stage", headers=headers)
        assert response.status_code == 200, f"Failed to get overdue by stage: {response.text}"
        
        data = response.json()
        # Response is an object with overdue_customers list
        assert isinstance(data, dict), "Response should be a dict"
        assert "overdue_customers" in data, "Response should have 'overdue_customers'"
        assert "current_stage" in data, "Response should have 'current_stage'"
        assert "overdue_count" in data, "Response should have 'overdue_count'"
        
        overdue_customers = data.get("overdue_customers", [])
        assert isinstance(overdue_customers, list), "overdue_customers should be a list"
        
        print(f"✓ GET /api/dashboard/overdue-by-stage returns:")
        print(f"  Current stage: {data.get('current_stage_name')}")
        print(f"  Overdue count: {data.get('overdue_count')}")
        print(f"  Total overdue amount: {data.get('total_overdue_amount')}")


class TestTransactionExportPDF:
    """Test Transaction Export PDF endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_export_transactions_html_endpoint(self, headers):
        """Test GET /api/transactions/{customer_id}/export-html returns HTML with customer details"""
        response = requests.get(f"{API}/transactions/{TEST_CUSTOMER_ID}/export-html", headers=headers)
        assert response.status_code == 200, f"Failed to export transactions: {response.text}"
        
        data = response.json()
        assert "content" in data, "Response should have 'content' field"
        assert "customer_name" in data, "Response should have 'customer_name' field"
        
        html_content = data["content"]
        customer_name = data["customer_name"]
        
        # Verify HTML structure
        assert "<!DOCTYPE html>" in html_content, "Should be valid HTML document"
        assert "Transaction Details" in html_content, "Should have Transaction Details title"
        assert "Ramya test lead" in html_content, "Should contain customer name"
        
        # Check for co-applicant in transaction export
        assert "Co-Applicant" in html_content or "Marketly" in html_content, "Should show co-applicant info"
        
        print(f"✓ GET /api/transactions/{TEST_CUSTOMER_ID}/export-html returns valid HTML")
        print(f"  Customer name: {customer_name}")
        print(f"  HTML length: {len(html_content)} characters")
    
    def test_export_transactions_has_table_structure(self, headers):
        """Test that export HTML has proper table structure for transactions"""
        response = requests.get(f"{API}/transactions/{TEST_CUSTOMER_ID}/export-html", headers=headers)
        assert response.status_code == 200
        
        html_content = response.json()["content"]
        
        # Check for table headers
        assert "<table" in html_content, "Should have table element"
        assert "Date" in html_content, "Should have Date column"
        assert "Stage" in html_content, "Should have Stage column"
        assert "Bank" in html_content, "Should have Bank column"
        assert "Amount" in html_content, "Should have Amount column"
        
        # Check for summary section
        assert "Total Property Value" in html_content or "Total" in html_content, "Should have total value"
        assert "Total Received" in html_content or "Received" in html_content, "Should have received amount"
        assert "Balance" in html_content, "Should have balance amount"
        
        print("✓ Transaction export HTML has proper table structure")


class TestDashboardStats:
    """Test Dashboard stats endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{API}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_dashboard_stats(self, headers):
        """Test GET /api/dashboard/stats returns expected fields"""
        response = requests.get(f"{API}/dashboard/stats", headers=headers)
        assert response.status_code == 200, f"Failed to get dashboard stats: {response.text}"
        
        data = response.json()
        assert "total_customers" in data, "Should have total_customers"
        assert "total_revenue" in data, "Should have total_revenue"
        assert "total_pending" in data, "Should have total_pending"
        
        print(f"✓ Dashboard stats: {data.get('total_customers')} customers, Revenue: {data.get('total_revenue')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
