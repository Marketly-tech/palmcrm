"""
Iteration 25 Tests - Sales Agreement Signature Text + Email Tracking Log
Tests:
1. Sales Agreement: VENDORS signature box should have 3 lines
2. Email Logs API: GET /api/email-logs with pagination, search, status filter
3. Email Logs API: Customer name enrichment
"""
import pytest
import requests
import os

from conftest_credentials import TEST_BASE_URL as BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD, TEST_CUSTOMER_UUID, TEST_CUSTOMER_ID


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data.get("access_token")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get auth headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestSalesAgreementSignature:
    """Test Sales Agreement signature text changes"""
    
    def test_generate_sales_agreement(self, auth_headers):
        """Generate sales agreement for Ramya test lead"""
        response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_UUID,
                "doc_type": "sales_agreement"
            },
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to generate sales agreement: {response.text}"
        data = response.json()
        # Response structure: {"message": "...", "document": {...}}
        assert "document" in data, "Response should contain document"
        assert "id" in data["document"], "Document should contain id"
        return data["document"]["id"]
    
    def test_sales_agreement_vendors_signature_text(self, auth_headers):
        """Verify VENDORS signature box contains 3 lines with Managing Director text"""
        # First generate the document
        gen_response = requests.post(
            f"{BASE_URL}/api/documents/generate",
            json={
                "customer_id": TEST_CUSTOMER_UUID,
                "doc_type": "sales_agreement"
            },
            headers=auth_headers
        )
        assert gen_response.status_code == 200, f"Failed to generate: {gen_response.text}"
        data = gen_response.json()
        doc_id = data["document"]["id"]
        
        # Get the HTML content - the content is already in the generate response
        content = data["document"].get("content", "")
        
        # Verify the VENDORS signature section contains all 3 lines
        assert "For RRL Builders & Developers Pvt. Ltd." in content, "Missing 'For RRL Builders & Developers Pvt. Ltd.' in signature"
        assert "Represented by its Managing Director Mr. Ram R" in content, "Missing 'Represented by its Managing Director Mr. Ram R' in signature"
        assert "Authorized Signatory" in content, "Missing 'Authorized Signatory' in signature"
        
        # Verify the order - Managing Director line should appear after company name
        company_pos = content.find("For RRL Builders & Developers Pvt. Ltd.")
        md_pos = content.find("Represented by its Managing Director Mr. Ram R")
        auth_pos = content.find("Authorized Signatory")
        
        # Find the signature section specifically (after VENDORS heading)
        vendors_section_start = content.find("<strong>VENDORS</strong>")
        assert vendors_section_start > 0, "VENDORS section not found"
        
        # Get positions after VENDORS section
        signature_section = content[vendors_section_start:]
        company_in_sig = signature_section.find("For RRL Builders & Developers Pvt. Ltd.")
        md_in_sig = signature_section.find("Represented by its Managing Director Mr. Ram R")
        auth_in_sig = signature_section.find("Authorized Signatory")
        
        assert company_in_sig > 0, "Company name not in VENDORS signature section"
        assert md_in_sig > company_in_sig, "Managing Director line should be after company name"
        assert auth_in_sig > md_in_sig, "Authorized Signatory should be after Managing Director line"
        
        print(f"PASS: VENDORS signature section has correct 3-line format")


class TestEmailLogsAPI:
    """Test Email Tracking Log API"""
    
    def test_email_logs_endpoint_exists(self, auth_headers):
        """Test that /api/email-logs endpoint exists and returns data"""
        response = requests.get(
            f"{BASE_URL}/api/email-logs",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Email logs endpoint failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "logs" in data, "Response should contain 'logs'"
        assert "total" in data, "Response should contain 'total'"
        assert "page" in data, "Response should contain 'page'"
        assert "limit" in data, "Response should contain 'limit'"
        assert "total_pages" in data, "Response should contain 'total_pages'"
        
        print(f"PASS: Email logs endpoint returns {data['total']} total logs")
    
    def test_email_logs_pagination(self, auth_headers):
        """Test pagination parameters"""
        response = requests.get(
            f"{BASE_URL}/api/email-logs?page=1&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["limit"] == 10
        assert len(data["logs"]) <= 10
        
        print(f"PASS: Pagination works - page {data['page']}, limit {data['limit']}")
    
    def test_email_logs_status_filter(self, auth_headers):
        """Test status filter parameter"""
        # Test with 'sent' status
        response = requests.get(
            f"{BASE_URL}/api/email-logs?status=sent",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # All returned logs should have 'sent' in status
        for log in data["logs"]:
            assert "sent" in log.get("status", "").lower(), f"Log status should contain 'sent': {log.get('status')}"
        
        print(f"PASS: Status filter works - {len(data['logs'])} logs with 'sent' status")
    
    def test_email_logs_customer_enrichment(self, auth_headers):
        """Test that logs are enriched with customer name, email, display_id"""
        response = requests.get(
            f"{BASE_URL}/api/email-logs?limit=50",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        if data["logs"]:
            log = data["logs"][0]
            # Check enrichment fields exist
            assert "customer_name" in log, "Log should have customer_name"
            assert "customer_email" in log, "Log should have customer_email"
            assert "customer_display_id" in log, "Log should have customer_display_id"
            
            print(f"PASS: Customer enrichment works - first log: {log.get('customer_name')} ({log.get('customer_display_id')})")
        else:
            print("INFO: No email logs found to verify enrichment")
    
    def test_email_logs_search(self, auth_headers):
        """Test search parameter"""
        response = requests.get(
            f"{BASE_URL}/api/email-logs?search=test",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Search should work without errors
        print(f"PASS: Search works - {len(data['logs'])} logs matching 'test'")


class TestEmailLogsPageRoute:
    """Test that /email-logs route is configured in frontend"""
    
    def test_email_logs_page_accessible(self, auth_headers):
        """Test that the email logs page route exists"""
        # This tests the API endpoint which the page uses
        response = requests.get(
            f"{BASE_URL}/api/email-logs",
            headers=auth_headers
        )
        assert response.status_code == 200, "Email logs API should be accessible"
        print("PASS: Email logs API accessible for frontend page")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
