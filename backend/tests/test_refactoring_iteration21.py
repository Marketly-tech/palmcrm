"""
Backend API Tests for Iteration 21 - Refactoring Verification
Tests document generation, customer detail page APIs, and transaction CRUD
"""
import pytest
import requests
import os

from conftest_credentials import TEST_BASE_URL as BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD, TEST_CUSTOMER_UUID as TEST_CUSTOMER_ID


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for API calls"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def api_client(auth_token):
    """Authenticated API client"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestHealthCheck:
    """Health check tests - run first"""
    
    def test_health_endpoint(self):
        """Test health endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data}")


class TestAuthentication:
    """Authentication flow tests"""
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"
        print(f"✓ Login successful for {ADMIN_EMAIL}")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "wrong@email.com", "password": "wrongpass"}
        )
        assert response.status_code == 401
        print("✓ Invalid credentials rejected correctly")


class TestCustomerDetailPage:
    """Customer detail page API tests"""
    
    def test_get_customer_details(self, api_client):
        """Test fetching customer details"""
        response = api_client.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == TEST_CUSTOMER_ID
        assert "name" in data
        assert "email" in data
        assert "phone" in data
        assert "project" in data
        assert "tower" in data
        assert "unit_number" in data
        print(f"✓ Customer details fetched: {data['name']}")
    
    def test_get_payment_schedule(self, api_client):
        """Test fetching payment schedule"""
        response = api_client.get(f"{BASE_URL}/api/payments/schedule/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✓ Payment schedule fetched: {len(data.get('items', []))} items")
    
    def test_get_checklist(self, api_client):
        """Test fetching checklist"""
        response = api_client.get(f"{BASE_URL}/api/checklist/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        print(f"✓ Checklist fetched")
    
    def test_get_documents(self, api_client):
        """Test fetching documents"""
        response = api_client.get(f"{BASE_URL}/api/documents/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Documents fetched: {len(data)} documents")
    
    def test_get_communications(self, api_client):
        """Test fetching communications"""
        response = api_client.get(f"{BASE_URL}/api/communication/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Communications fetched: {len(data)} records")
    
    def test_get_transactions(self, api_client):
        """Test fetching transactions"""
        response = api_client.get(f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Transactions fetched: {len(data)} transactions")
    
    def test_get_overdue_info(self, api_client):
        """Test fetching overdue info"""
        response = api_client.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/overdue")
        assert response.status_code == 200
        data = response.json()
        # May be null if no overdue
        print(f"✓ Overdue info fetched: {data}")
    
    def test_get_notes(self, api_client):
        """Test fetching notes"""
        response = api_client.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/notes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Notes fetched: {len(data)} notes")


class TestDocumentGeneration:
    """Document generation API tests - verifies refactored template imports"""
    
    def test_generate_demand_letter(self, api_client):
        """Test demand letter generation"""
        response = api_client.post(
            f"{BASE_URL}/api/documents/generate",
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "demand_letter"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert data["document"]["doc_type"] == "demand_letter"
        print("✓ Demand letter generated successfully")
    
    def test_generate_allotment_letter(self, api_client):
        """Test allotment letter generation"""
        response = api_client.post(
            f"{BASE_URL}/api/documents/generate",
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "allotment_letter"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert data["document"]["doc_type"] == "allotment_letter"
        print("✓ Allotment letter generated successfully")
    
    def test_generate_price_breakup(self, api_client):
        """Test price breakup generation"""
        response = api_client.post(
            f"{BASE_URL}/api/documents/generate",
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "price_breakup"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert data["document"]["doc_type"] == "price_breakup"
        print("✓ Price breakup generated successfully")
    
    def test_generate_cost_breakup(self, api_client):
        """Test cost breakup generation"""
        response = api_client.post(
            f"{BASE_URL}/api/documents/generate",
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "cost_breakup"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert data["document"]["doc_type"] == "cost_breakup"
        print("✓ Cost breakup generated successfully")
    
    def test_generate_payment_schedule(self, api_client):
        """Test payment schedule document generation"""
        response = api_client.post(
            f"{BASE_URL}/api/documents/generate",
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "payment_schedule"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert data["document"]["doc_type"] == "payment_schedule"
        print("✓ Payment schedule document generated successfully")
    
    def test_generate_sales_agreement(self, api_client):
        """Test sales agreement generation"""
        response = api_client.post(
            f"{BASE_URL}/api/documents/generate",
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "sales_agreement"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert data["document"]["doc_type"] == "sales_agreement"
        print("✓ Sales agreement generated successfully")
    
    def test_generate_noc_hdfc(self, api_client):
        """Test HDFC NOC generation"""
        response = api_client.post(
            f"{BASE_URL}/api/documents/generate",
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "noc_hdfc"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert data["document"]["doc_type"] == "noc_hdfc"
        print("✓ HDFC NOC generated successfully")
    
    def test_generate_noc_bob(self, api_client):
        """Test BOB NOC generation"""
        response = api_client.post(
            f"{BASE_URL}/api/documents/generate",
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "noc_bob"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert data["document"]["doc_type"] == "noc_bob"
        print("✓ BOB NOC generated successfully")
    
    def test_generate_noc_tata(self, api_client):
        """Test TATA NOC generation"""
        response = api_client.post(
            f"{BASE_URL}/api/documents/generate",
            json={"customer_id": TEST_CUSTOMER_ID, "doc_type": "noc_tata"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert data["document"]["doc_type"] == "noc_tata"
        print("✓ TATA NOC generated successfully")


class TestTransactionCRUD:
    """Transaction CRUD operations tests"""
    
    def test_create_transaction(self, api_client):
        """Test creating a new transaction"""
        import time
        unique_id = str(int(time.time()))[-6:]
        
        transaction_data = {
            "transaction_stage": "booking",
            "transaction_date": "2026-04-03",
            "bank_name": "Test Bank Pytest",
            "transaction_number": f"TXN-PYTEST-{unique_id}",
            "amount": 100,
            "notes": "Test transaction from pytest"
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}",
            json=transaction_data
        )
        assert response.status_code == 200
        data = response.json()
        # API returns {"message": "...", "transaction": {...}}
        assert "transaction" in data or "id" in data
        txn = data.get("transaction", data)
        assert "id" in txn
        print(f"✓ Transaction created: {txn['id']}")
        
        # Store for later tests
        TestTransactionCRUD.created_transaction_id = txn["id"]
        return txn["id"]
    
    def test_get_transactions_after_create(self, api_client):
        """Verify transaction appears in list after creation"""
        response = api_client.get(f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Find our created transaction
        found = any(t.get("id") == getattr(TestTransactionCRUD, 'created_transaction_id', None) for t in data)
        assert found, "Created transaction not found in list"
        print(f"✓ Transaction verified in list")
    
    def test_update_transaction(self, api_client):
        """Test updating a transaction"""
        txn_id = getattr(TestTransactionCRUD, 'created_transaction_id', None)
        if not txn_id:
            pytest.skip("No transaction ID from create test")
        
        update_data = {
            "transaction_stage": "booking",
            "transaction_date": "2026-04-03",
            "bank_name": "Updated Bank Pytest",
            "transaction_number": "TXN-PYTEST-UPDATED",
            "amount": 200,
            "notes": "Updated notes from pytest"
        }
        
        response = api_client.put(
            f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}/{txn_id}",
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        # API returns {"message": "Transaction updated"} - verify via GET
        assert "message" in data or "transaction" in data
        
        # Verify update via GET
        get_response = api_client.get(f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}")
        assert get_response.status_code == 200
        transactions = get_response.json()
        updated_txn = next((t for t in transactions if t.get("id") == txn_id), None)
        if updated_txn:
            assert updated_txn.get("bank_name") == "Updated Bank Pytest"
            assert updated_txn.get("amount") == 200
        print(f"✓ Transaction updated: {txn_id}")
    
    def test_delete_transaction(self, api_client):
        """Test deleting a transaction"""
        txn_id = getattr(TestTransactionCRUD, 'created_transaction_id', None)
        if not txn_id:
            pytest.skip("No transaction ID from create test")
        
        response = api_client.delete(
            f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}/{txn_id}"
        )
        assert response.status_code == 200
        print(f"✓ Transaction deleted: {txn_id}")
    
    def test_verify_transaction_deleted(self, api_client):
        """Verify transaction no longer exists after deletion"""
        txn_id = getattr(TestTransactionCRUD, 'created_transaction_id', None)
        if not txn_id:
            pytest.skip("No transaction ID from create test")
        
        response = api_client.get(f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify our transaction is gone
        found = any(t.get("id") == txn_id for t in data)
        assert not found, "Deleted transaction still found in list"
        print(f"✓ Transaction deletion verified")


class TestDashboard:
    """Dashboard API tests"""
    
    def test_dashboard_stats(self, api_client):
        """Test dashboard stats endpoint"""
        response = api_client.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_customers" in data
        assert "total_revenue" in data
        print(f"✓ Dashboard stats: {data['total_customers']} customers, ₹{data['total_revenue']} revenue")
    
    def test_dashboard_overdue_by_stage(self, api_client):
        """Test overdue by stage endpoint"""
        response = api_client.get(f"{BASE_URL}/api/dashboard/overdue-by-stage")
        assert response.status_code == 200
        data = response.json()
        # API returns dict with stage info, not a list
        assert isinstance(data, (list, dict))
        if isinstance(data, dict):
            print(f"✓ Overdue by stage: current_stage={data.get('current_stage')}, overdue_count={data.get('overdue_count')}")
        else:
            print(f"✓ Overdue by stage: {len(data)} stages")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
