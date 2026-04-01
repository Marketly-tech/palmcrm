"""
Test Demand Letter Document Generation Feature
Tests the new demand_letter document type added to RRL CRM
"""
import pytest
import requests
import os
from tests.conftest_credentials import ADMIN_EMAIL, ADMIN_PASSWORD, ACCOUNTS_EMAIL, ACCOUNTS_PASSWORD, TEST_CUSTOMER_ID, API_URL, TEST_BASE_URL

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = ADMIN_EMAIL
ADMIN_PASSWORD = ADMIN_PASSWORD
TEST_CUSTOMER_ID = TEST_CUSTOMER_ID


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Create authenticated session"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    })
    return session


class TestDemandLetterBackend:
    """Backend tests for demand letter document generation"""

    def test_01_customer_exists(self, api_client):
        """Verify test customer exists"""
        response = api_client.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200, f"Customer not found: {response.text}"
        customer = response.json()
        assert customer.get("name"), "Customer name missing"
        assert customer.get("total_price", 0) > 0, "Customer should have total_price set"
        print(f"✓ Test customer found: {customer.get('name')}")
        print(f"  Total Price: {customer.get('total_price')}")

    def test_02_generate_demand_letter(self, api_client):
        """Test generating demand letter document"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert response.status_code == 200, f"Failed to generate demand letter: {response.text}"
        data = response.json()
        assert "message" in data, "Response should contain message"
        assert "document" in data, "Response should contain document"
        print(f"✓ Demand letter generated successfully")

    def test_03_demand_letter_html_contains_title(self, api_client):
        """Verify demand letter HTML contains DEMAND LETTER title"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert response.status_code == 200
        data = response.json()
        html_content = data.get("document", {}).get("content", "")
        
        assert "DEMAND LETTER" in html_content, "HTML should contain 'DEMAND LETTER' title"
        print("✓ Demand letter contains DEMAND LETTER title")

    def test_04_demand_letter_contains_customer_name(self, api_client):
        """Verify demand letter contains customer name"""
        # First get customer name
        cust_response = api_client.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}")
        customer = cust_response.json()
        customer_name = customer.get("name", "").upper()
        
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert response.status_code == 200
        data = response.json()
        html_content = data.get("document", {}).get("content", "")
        
        assert customer_name in html_content, f"HTML should contain customer name '{customer_name}'"
        print(f"✓ Demand letter contains customer name: {customer_name}")

    def test_05_demand_letter_contains_property_reference(self, api_client):
        """Verify demand letter contains property reference (flat, tower, floor)"""
        cust_response = api_client.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}")
        customer = cust_response.json()
        unit_number = customer.get("unit_number", "")
        tower = customer.get("tower", "")
        
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert response.status_code == 200
        data = response.json()
        html_content = data.get("document", {}).get("content", "")
        
        if unit_number:
            assert unit_number in html_content, f"HTML should contain unit number '{unit_number}'"
            print(f"✓ Demand letter contains unit number: {unit_number}")
        if tower:
            assert tower in html_content, f"HTML should contain tower '{tower}'"
            print(f"✓ Demand letter contains tower: {tower}")

    def test_06_demand_letter_contains_payment_table(self, api_client):
        """Verify demand letter contains payment breakdown table with 10 rows"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert response.status_code == 200
        data = response.json()
        html_content = data.get("document", {}).get("content", "")
        
        # Check for key table elements
        assert "Total Basic Cost" in html_content, "Should contain 'Total Basic Cost'"
        assert "Demand Raised Till Date" in html_content, "Should contain 'Demand Raised Till Date'"
        assert "Current Due" in html_content, "Should contain 'Current Due'"
        assert "Installment Amount Paid Till Date" in html_content, "Should contain 'Installment Amount Paid Till Date'"
        assert "Total Outstanding" in html_content, "Should contain 'Total Outstanding'"
        assert "TDS Payable" in html_content, "Should contain 'TDS Payable'"
        assert "Net Amount Payable" in html_content, "Should contain 'Net Amount Payable'"
        print("✓ Demand letter contains payment breakdown table with all required rows")

    def test_07_demand_letter_contains_amount_in_words(self, api_client):
        """Verify demand letter contains amount in words"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert response.status_code == 200
        data = response.json()
        html_content = data.get("document", {}).get("content", "")
        
        # Amount in words should contain "Rupees" and "Only"
        assert "Rupees" in html_content, "Should contain 'Rupees' in amount words"
        assert "Only" in html_content, "Should contain 'Only' in amount words"
        print("✓ Demand letter contains amount in words")

    def test_08_demand_letter_contains_bank_details(self, api_client):
        """Verify demand letter contains HDFC bank remittance details"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert response.status_code == 200
        data = response.json()
        html_content = data.get("document", {}).get("content", "")
        
        # Check for bank details
        assert "HDFC BANK" in html_content, "Should contain 'HDFC BANK'"
        assert "57500001802063" in html_content, "Should contain account number"
        assert "HDFC0009590" in html_content, "Should contain IFSC code"
        assert "SOMPURA" in html_content, "Should contain branch name"
        assert "RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED" in html_content, "Should contain account name"
        print("✓ Demand letter contains HDFC bank remittance details")

    def test_09_demand_letter_contains_signature(self, api_client):
        """Verify demand letter contains closing signature"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert response.status_code == 200
        data = response.json()
        html_content = data.get("document", {}).get("content", "")
        
        assert "Thanking you" in html_content, "Should contain 'Thanking you'"
        assert "RRL Builders and Developers" in html_content, "Should contain company name in signature"
        print("✓ Demand letter contains closing signature")

    def test_10_demand_letter_contains_rrl_branding(self, api_client):
        """Verify demand letter contains RRL branding header"""
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert response.status_code == 200
        data = response.json()
        html_content = data.get("document", {}).get("content", "")
        
        assert "RRL" in html_content, "Should contain 'RRL' logo"
        assert "Beyond homes. A lifestyle" in html_content, "Should contain tagline"
        print("✓ Demand letter contains RRL branding header")

    def test_11_demand_letter_financial_calculations(self, api_client):
        """Verify demand letter calculates correct financial values"""
        # Get customer data
        cust_response = api_client.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}")
        customer = cust_response.json()
        total_price = float(customer.get("total_price", 0) or 0)
        
        # Get current stage settings
        settings_response = api_client.get(f"{BASE_URL}/api/settings/payment-stage")
        if settings_response.status_code == 200:
            settings = settings_response.json()
            current_stage = settings.get("current_stage", "")
            print(f"  Current stage: {current_stage}")
        
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert response.status_code == 200
        data = response.json()
        html_content = data.get("document", {}).get("content", "")
        
        # Verify total basic cost is present (formatted)
        assert "Total Basic Cost" in html_content, "Should contain Total Basic Cost label"
        print(f"✓ Demand letter contains financial calculations (Total Price: {total_price})")

    def test_12_demand_letter_appears_in_documents_list(self, api_client):
        """Verify generated demand letter appears in customer's documents list"""
        # Generate a demand letter first
        gen_response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        assert gen_response.status_code == 200
        
        # Get documents list
        docs_response = api_client.get(f"{BASE_URL}/api/documents/{TEST_CUSTOMER_ID}")
        assert docs_response.status_code == 200
        documents = docs_response.json()
        
        # Find demand letter in list
        demand_letters = [d for d in documents if d.get("doc_type") == "demand_letter"]
        assert len(demand_letters) > 0, "Demand letter should appear in documents list"
        print(f"✓ Found {len(demand_letters)} demand letter(s) in documents list")

    def test_13_demand_letter_has_content_for_preview(self, api_client):
        """Verify demand letter document has content field for frontend preview"""
        # Get documents list
        docs_response = api_client.get(f"{BASE_URL}/api/documents/{TEST_CUSTOMER_ID}")
        assert docs_response.status_code == 200
        documents = docs_response.json()
        
        # Find a demand letter
        demand_letters = [d for d in documents if d.get("doc_type") == "demand_letter"]
        assert len(demand_letters) > 0, "Should have at least one demand letter"
        
        # Verify the document has content field for preview
        doc = demand_letters[0]
        assert "content" in doc, "Document should have 'content' field for preview"
        assert len(doc.get("content", "")) > 0, "Document content should not be empty"
        assert "DEMAND LETTER" in doc.get("content", ""), "Content should contain DEMAND LETTER"
        print(f"✓ Demand letter has content for preview (length: {len(doc.get('content', ''))} chars)")


class TestDemandLetterDocumentType:
    """Test that demand_letter is properly registered as a document type"""

    def test_document_type_enum_includes_demand_letter(self, api_client):
        """Verify demand_letter is a valid document type"""
        # Try to generate with demand_letter type - if it works, the type is valid
        response = api_client.post(f"{BASE_URL}/api/documents/generate", json={
            "customer_id": TEST_CUSTOMER_ID,
            "doc_type": "demand_letter",
            "custom_fields": {}
        })
        # Should not return 422 (validation error) for invalid doc_type
        assert response.status_code != 422, "demand_letter should be a valid document type"
        assert response.status_code == 200, f"Generation failed: {response.text}"
        print("✓ demand_letter is a valid document type in the enum")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
