"""
Test Document Templates - Iteration 22
Tests for document generation with updated company name, logo, applicant format, repo rate, and sales agreement total received.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://builder-crm-dev.preview.emergentagent.com')
TEST_CUSTOMER_ID = os.environ.get('TEST_CUSTOMER_ID', '6d902613-5106-4294-bc3e-b907f85127f7')
ADMIN_EMAIL = os.environ.get('TEST_ADMIN_EMAIL', 'crm@rrlbuildersanddevelopers.com')
ADMIN_PASSWORD = os.environ.get('TEST_ADMIN_PASSWORD', '#RRLnew2026')


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def authenticated_session(auth_token):
    """Session with auth header"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestHealthCheck:
    """Health check tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ API health check passed")


class TestAuthentication:
    """Authentication tests"""
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        assert "user" in data
        print("✓ Login successful")


class TestDocumentGeneration:
    """Document generation tests - all 9 document types"""
    
    DOC_TYPES = [
        "demand_letter",
        "allotment_letter", 
        "price_breakup",
        "cost_breakup",
        "payment_schedule",
        "sales_agreement",
        "noc_hdfc",
        "noc_bob",
        "noc_tata"
    ]
    
    @pytest.mark.parametrize("doc_type", DOC_TYPES)
    def test_document_generation_success(self, authenticated_session, doc_type):
        """Test that all document types generate successfully (200 OK)"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": doc_type
            }
        )
        assert response.status_code == 200, f"Failed to generate {doc_type}: {response.text}"
        data = response.json()
        assert "document" in data, f"No document in response for {doc_type}"
        assert "content" in data["document"], f"No content in document for {doc_type}"
        print(f"✓ {doc_type} generated successfully")


class TestAllotmentLetterContent:
    """Test allotment letter content verification"""
    
    def test_allotment_letter_has_logo_img_tag(self, authenticated_session):
        """Test allotment letter contains logo img tag with base64"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "allotment_letter"
            }
        )
        assert response.status_code == 200
        content = response.json()["document"]["content"]
        assert "data:image/png;base64," in content, "Logo img tag with base64 not found in allotment letter"
        print("✓ Allotment letter contains logo img tag with base64")
    
    def test_allotment_letter_has_pvt_ltd_company_name(self, authenticated_session):
        """Test allotment letter contains 'Pvt. Ltd.' company name"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "allotment_letter"
            }
        )
        assert response.status_code == 200
        content = response.json()["document"]["content"]
        assert "Pvt. Ltd." in content or "PVT. LTD." in content, "Company name with 'Pvt. Ltd.' not found in allotment letter"
        print("✓ Allotment letter contains 'Pvt. Ltd.' company name")
    
    def test_allotment_letter_has_repo_rate_text(self, authenticated_session):
        """Test allotment letter point 14 contains repo rate 7.15% text"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "allotment_letter"
            }
        )
        assert response.status_code == 200
        content = response.json()["document"]["content"]
        assert "7.15%" in content, "Repo rate 7.15% not found in allotment letter"
        print("✓ Allotment letter contains repo rate 7.15% text")


class TestSalesAgreementContent:
    """Test sales agreement content verification"""
    
    def test_sales_agreement_has_logo_img_tag(self, authenticated_session):
        """Test sales agreement contains logo img tag"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "sales_agreement"
            }
        )
        assert response.status_code == 200
        content = response.json()["document"]["content"]
        assert "data:image/png;base64," in content, "Logo img tag with base64 not found in sales agreement"
        print("✓ Sales agreement contains logo img tag with base64")
    
    def test_sales_agreement_has_pvt_ltd_company_name(self, authenticated_session):
        """Test sales agreement contains 'Pvt. Ltd.' company name"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "sales_agreement"
            }
        )
        assert response.status_code == 200
        content = response.json()["document"]["content"]
        assert "Pvt. Ltd." in content or "PVT. LTD." in content, "Company name with 'Pvt. Ltd.' not found in sales agreement"
        print("✓ Sales agreement contains 'Pvt. Ltd.' company name")
    
    def test_sales_agreement_has_applicant_details_block(self, authenticated_session):
        """Test sales agreement contains applicant details block with Aadhaar/PAN/Phone"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "sales_agreement"
            }
        )
        assert response.status_code == 200
        content = response.json()["document"]["content"]
        # Check for applicant details block markers
        has_aadhaar = "Aadhaar:" in content or "aadhaar" in content.lower()
        has_pan = "PAN:" in content or "pan" in content.lower()
        has_phone = "Phone:" in content or "phone" in content.lower()
        assert has_aadhaar or has_pan or has_phone, "Applicant details block (Aadhaar/PAN/Phone) not found in sales agreement"
        print("✓ Sales agreement contains applicant details block")


class TestDemandLetterContent:
    """Test demand letter content verification"""
    
    def test_demand_letter_has_logo_img_tag(self, authenticated_session):
        """Test demand letter contains logo img tag"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "demand_letter"
            }
        )
        assert response.status_code == 200
        content = response.json()["document"]["content"]
        assert "data:image/png;base64," in content, "Logo img tag with base64 not found in demand letter"
        print("✓ Demand letter contains logo img tag with base64")
    
    def test_demand_letter_has_private_limited_company_name(self, authenticated_session):
        """Test demand letter contains 'PRIVATE LIMITED' company name"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "demand_letter"
            }
        )
        assert response.status_code == 200
        content = response.json()["document"]["content"]
        assert "PRIVATE LIMITED" in content or "Pvt. Ltd." in content, "Company name with 'PRIVATE LIMITED' not found in demand letter"
        print("✓ Demand letter contains 'PRIVATE LIMITED' company name")
    
    def test_demand_letter_has_applicant_block(self, authenticated_session):
        """Test demand letter contains applicant block with Aadhaar/Phone"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_ID,
                "doc_type": "demand_letter"
            }
        )
        assert response.status_code == 200
        content = response.json()["document"]["content"]
        # Check for applicant details
        has_aadhaar = "Aadhaar:" in content or "aadhaar" in content.lower()
        has_phone = "Phone:" in content or "phone" in content.lower()
        assert has_aadhaar or has_phone, "Applicant block (Aadhaar/Phone) not found in demand letter"
        print("✓ Demand letter contains applicant block")


class TestCustomerDetailAPIs:
    """Test customer detail APIs"""
    
    def test_get_customer_details(self, authenticated_session):
        """Test getting customer details"""
        response = authenticated_session.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        print(f"✓ Customer details retrieved: {data.get('name')}")
    
    def test_get_customer_transactions(self, authenticated_session):
        """Test getting customer transactions"""
        response = authenticated_session.get(f"{BASE_URL}/api/transactions/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Customer transactions retrieved: {len(data)} transactions")
    
    def test_get_customer_payment_schedule(self, authenticated_session):
        """Test getting customer payment schedule"""
        response = authenticated_session.get(f"{BASE_URL}/api/payments/schedule/{TEST_CUSTOMER_ID}")
        assert response.status_code == 200
        data = response.json()
        # Payment schedule can be a list or an object with items
        if isinstance(data, list):
            print(f"✓ Customer payment schedule retrieved: {len(data)} items")
        elif isinstance(data, dict) and "items" in data:
            print(f"✓ Customer payment schedule retrieved: {len(data['items'])} items")
        else:
            assert False, f"Unexpected payment schedule format: {type(data)}"
    
    def test_get_customer_documents_list(self, authenticated_session):
        """Test getting customer documents list"""
        response = authenticated_session.get(f"{BASE_URL}/api/customers/{TEST_CUSTOMER_ID}/documents-list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Customer documents list retrieved: {len(data)} documents")


class TestCoApplicantDateOfBirth:
    """Test co_applicant_date_of_birth field in booking form API"""
    
    def test_booking_form_accepts_co_applicant_dob(self):
        """Test that booking form API accepts co_applicant_date_of_birth field"""
        # Create a test booking with co_applicant_date_of_birth
        test_booking = {
            "name": "TEST_CoApplicantDOB_Test",
            "phone": "9999999999",
            "email": "test_coapplicant_dob@test.com",
            "project": "RRL Palm Altezze",
            "tower": "Tower-1",
            "unit_number": "TEST-9999",
            "bhk_type": "3BHK",
            "saleable_area": 1500,
            "rate_per_sqft": 6600,
            "booking_amount": 100000,
            "co_applicant_name": "Test Co-Applicant",
            "co_applicant_date_of_birth": "1990-05-15"  # The field being tested
        }
        
        response = requests.post(f"{BASE_URL}/api/public/booking-form", json=test_booking)
        assert response.status_code == 200, f"Booking form submission failed: {response.text}"
        data = response.json()
        assert "reference_id" in data or "customer_id" in data
        print("✓ Booking form accepts co_applicant_date_of_birth field")
        
        # Clean up - delete the test customer
        customer_id = data.get("reference_id") or data.get("customer_id")
        if customer_id:
            # Login to get token for deletion
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            if login_response.status_code == 200:
                token = login_response.json().get("token")
                delete_response = requests.delete(
                    f"{BASE_URL}/api/customers/{customer_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if delete_response.status_code == 200:
                    print(f"✓ Test customer {customer_id} cleaned up")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
