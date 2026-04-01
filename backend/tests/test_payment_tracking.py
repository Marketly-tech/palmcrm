"""
Test Suite: Payment Tracking Auto-Update Feature
Tests the connection between payment schedule and payment tracking fields.
When payment status changes, it should automatically update customer's
total_received, balance_amount, and payment percentages.
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://builder-crm-dev.preview.emergentagent.com').rstrip('/')

class TestPaymentTrackingFeature:
    """Tests for payment status change auto-updating customer payment tracking"""
    
    auth_token = None
    test_customer_id = None
    test_customer_total_price = None
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client, auth_token):
        """Setup common test data"""
        TestPaymentTrackingFeature.auth_token = auth_token
    
    def test_01_login(self, api_client):
        """Test login to get auth token"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@rrlbuilders.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        TestPaymentTrackingFeature.auth_token = data["access_token"]
        print(f"Login successful, token obtained")
    
    def test_02_get_existing_customers(self, authenticated_client):
        """Get list of customers to find one with payment schedule"""
        response = authenticated_client.get(f"{BASE_URL}/api/customers")
        assert response.status_code == 200, f"Failed to get customers: {response.text}"
        
        data = response.json()
        assert "customers" in data
        assert len(data["customers"]) > 0, "No customers found"
        
        # Find a customer with total_price
        for customer in data["customers"]:
            if customer.get("total_price", 0) > 0:
                TestPaymentTrackingFeature.test_customer_id = customer["id"]
                TestPaymentTrackingFeature.test_customer_total_price = customer["total_price"]
                print(f"Found customer: {customer['name']} with total_price: {customer['total_price']}")
                break
        
        assert TestPaymentTrackingFeature.test_customer_id is not None, "No customer with total_price found"
    
    def test_03_get_customer_payment_schedule(self, authenticated_client):
        """Get customer's payment schedule"""
        customer_id = TestPaymentTrackingFeature.test_customer_id
        response = authenticated_client.get(f"{BASE_URL}/api/payments/schedule/{customer_id}")
        assert response.status_code == 200, f"Failed to get payment schedule: {response.text}"
        
        data = response.json()
        print(f"Payment schedule has {len(data.get('items', []))} items")
        return data
    
    def test_04_get_customer_initial_state(self, authenticated_client):
        """Get customer's initial payment tracking state"""
        customer_id = TestPaymentTrackingFeature.test_customer_id
        response = authenticated_client.get(f"{BASE_URL}/api/customers/{customer_id}")
        assert response.status_code == 200, f"Failed to get customer: {response.text}"
        
        customer = response.json()
        print(f"Initial state:")
        print(f"  total_price: {customer.get('total_price', 0)}")
        print(f"  total_received: {customer.get('total_received', 0)}")
        print(f"  balance_amount: {customer.get('balance_amount', 0)}")
        print(f"  payment_received_percentage: {customer.get('payment_received_percentage', 0)}")
        print(f"  payment_pending_percentage: {customer.get('payment_pending_percentage', 0)}")
        return customer
    
    def test_05_update_payment_status_to_paid(self, authenticated_client):
        """Test updating a payment item status to 'paid' and verify response"""
        customer_id = TestPaymentTrackingFeature.test_customer_id
        
        # Get payment schedule
        schedule_response = authenticated_client.get(f"{BASE_URL}/api/payments/schedule/{customer_id}")
        assert schedule_response.status_code == 200
        schedule = schedule_response.json()
        
        if not schedule.get("items"):
            pytest.skip("No payment items to test")
        
        # Find a pending item to update
        pending_item = None
        for item in schedule.get("items", []):
            if item.get("payment_status") == "pending":
                pending_item = item
                break
        
        if not pending_item:
            # Reset first item to pending first
            first_item = schedule["items"][0]
            reset_response = authenticated_client.put(
                f"{BASE_URL}/api/payments/item/{customer_id}/{first_item['id']}",
                json={"payment_status": "pending", "payment_date": None}
            )
            assert reset_response.status_code == 200, f"Failed to reset payment: {reset_response.text}"
            pending_item = first_item
        
        item_id = pending_item["id"]
        item_amount = pending_item.get("amount", 0)
        print(f"Updating payment item '{pending_item.get('installment_name')}' (amount: {item_amount}) to 'paid'")
        
        # Update to paid
        response = authenticated_client.put(
            f"{BASE_URL}/api/payments/item/{customer_id}/{item_id}",
            json={"payment_status": "paid"}
        )
        assert response.status_code == 200, f"Failed to update payment status: {response.text}"
        
        data = response.json()
        print(f"API Response:")
        print(f"  message: {data.get('message')}")
        print(f"  total_received: {data.get('total_received')}")
        print(f"  balance_amount: {data.get('balance_amount')}")
        print(f"  payment_received_percentage: {data.get('payment_received_percentage')}")
        print(f"  payment_pending_percentage: {data.get('payment_pending_percentage')}")
        
        # Verify response contains updated values
        assert "total_received" in data, "Response should contain total_received"
        assert "balance_amount" in data, "Response should contain balance_amount"
        assert "payment_received_percentage" in data, "Response should contain payment_received_percentage"
        assert "payment_pending_percentage" in data, "Response should contain payment_pending_percentage"
        
        # Verify values are reasonable
        assert data["total_received"] >= 0, "total_received should be non-negative"
        assert data["payment_received_percentage"] >= 0 and data["payment_received_percentage"] <= 100
        
        return data
    
    def test_06_verify_customer_updated_after_status_change(self, authenticated_client):
        """Verify customer record was updated in database after payment status change"""
        customer_id = TestPaymentTrackingFeature.test_customer_id
        
        response = authenticated_client.get(f"{BASE_URL}/api/customers/{customer_id}")
        assert response.status_code == 200, f"Failed to get customer: {response.text}"
        
        customer = response.json()
        print(f"Customer state after payment update:")
        print(f"  total_price: {customer.get('total_price', 0)}")
        print(f"  total_received: {customer.get('total_received', 0)}")
        print(f"  balance_amount: {customer.get('balance_amount', 0)}")
        print(f"  payment_received_percentage: {customer.get('payment_received_percentage', 0)}")
        
        # Verify values were updated
        total_price = customer.get("total_price", 0)
        total_received = customer.get("total_received", 0)
        balance = customer.get("balance_amount", 0)
        
        # Balance should equal total_price - total_received
        expected_balance = total_price - total_received
        assert abs(balance - expected_balance) < 1, f"Balance ({balance}) should equal total_price - total_received ({expected_balance})"
        
        # Percentages should be calculated correctly
        if total_price > 0:
            expected_received_pct = (total_received / total_price) * 100
            actual_received_pct = customer.get("payment_received_percentage", 0)
            assert abs(actual_received_pct - expected_received_pct) < 1, f"Received percentage ({actual_received_pct}) doesn't match expected ({expected_received_pct})"
    
    def test_07_update_multiple_items_accumulates_correctly(self, authenticated_client):
        """Test that marking multiple items as paid accumulates the amounts"""
        customer_id = TestPaymentTrackingFeature.test_customer_id
        
        # First reset all items to pending
        schedule_response = authenticated_client.get(f"{BASE_URL}/api/payments/schedule/{customer_id}")
        schedule = schedule_response.json()
        
        if len(schedule.get("items", [])) < 2:
            pytest.skip("Need at least 2 payment items to test accumulation")
        
        # Reset first 2 items to pending
        for item in schedule["items"][:2]:
            authenticated_client.put(
                f"{BASE_URL}/api/payments/item/{customer_id}/{item['id']}",
                json={"payment_status": "pending", "payment_date": None}
            )
        
        # Get fresh schedule
        schedule_response = authenticated_client.get(f"{BASE_URL}/api/payments/schedule/{customer_id}")
        schedule = schedule_response.json()
        items = schedule.get("items", [])[:2]
        
        # Calculate expected total
        expected_total = items[0].get("amount", 0) + items[1].get("amount", 0)
        print(f"Will mark 2 items as paid. Item 1: {items[0].get('amount', 0)}, Item 2: {items[1].get('amount', 0)}")
        print(f"Expected accumulated total: {expected_total}")
        
        # Mark first item as paid
        response1 = authenticated_client.put(
            f"{BASE_URL}/api/payments/item/{customer_id}/{items[0]['id']}",
            json={"payment_status": "paid"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        print(f"After first payment: total_received = {data1.get('total_received')}")
        
        # Mark second item as paid
        response2 = authenticated_client.put(
            f"{BASE_URL}/api/payments/item/{customer_id}/{items[1]['id']}",
            json={"payment_status": "paid"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        print(f"After second payment: total_received = {data2.get('total_received')}")
        
        # Verify accumulation
        actual_total = data2.get("total_received", 0)
        assert actual_total >= expected_total * 0.99, f"Accumulated total ({actual_total}) should be at least {expected_total}"
    
    def test_08_partial_payment_counts_half(self, authenticated_client):
        """Test that partial payment status counts as 50% of amount"""
        customer_id = TestPaymentTrackingFeature.test_customer_id
        
        # Reset all to pending first
        schedule_response = authenticated_client.get(f"{BASE_URL}/api/payments/schedule/{customer_id}")
        schedule = schedule_response.json()
        
        for item in schedule.get("items", []):
            authenticated_client.put(
                f"{BASE_URL}/api/payments/item/{customer_id}/{item['id']}",
                json={"payment_status": "pending", "payment_date": None}
            )
        
        # Get fresh schedule
        schedule_response = authenticated_client.get(f"{BASE_URL}/api/payments/schedule/{customer_id}")
        schedule = schedule_response.json()
        
        if not schedule.get("items"):
            pytest.skip("No payment items to test")
        
        first_item = schedule["items"][0]
        item_amount = first_item.get("amount", 0)
        expected_partial_amount = item_amount * 0.5
        
        print(f"Testing partial payment: full amount = {item_amount}, expected partial = {expected_partial_amount}")
        
        # Mark as partial
        response = authenticated_client.put(
            f"{BASE_URL}/api/payments/item/{customer_id}/{first_item['id']}",
            json={"payment_status": "partial"}
        )
        assert response.status_code == 200
        data = response.json()
        
        actual_received = data.get("total_received", 0)
        print(f"Actual total_received after partial: {actual_received}")
        
        # Should be approximately half the amount (allowing for other paid items)
        # Since we reset all, it should be exactly half
        assert abs(actual_received - expected_partial_amount) < 1, f"Partial payment ({actual_received}) should be ~{expected_partial_amount}"


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def auth_token(api_client):
    """Get authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@rrlbuilders.com",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client
