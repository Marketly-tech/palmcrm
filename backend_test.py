#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class RRLCRMTester:
    def __init__(self, base_url="https://property-crm-test-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "status": "PASSED" if success else "FAILED",
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, use_auth=True):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = self.headers.copy()
        
        if use_auth and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return response.json()
                except:
                    return {"status": "success", "status_code": response.status_code}
            else:
                error_details = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_body = response.json()
                    error_details += f" - {error_body.get('detail', error_body)}"
                except:
                    error_details += f" - {response.text[:200]}"
                
                self.log_test(name, False, error_details)
                return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n🔍 Testing Health Endpoints...")
        
        # Test root endpoint
        self.run_test(
            "Root endpoint (/api/)",
            "GET",
            "",
            200,
            use_auth=False
        )
        
        # Test health endpoint
        self.run_test(
            "Health check (/api/health)",
            "GET", 
            "health",
            200,
            use_auth=False
        )

    def test_authentication(self):
        """Test authentication flow"""
        print("\n🔍 Testing Authentication...")
        
        # Test login with valid credentials
        login_data = {
            "email": "admin@rrlbuilders.com",
            "password": "admin123"
        }
        
        response = self.run_test(
            "Admin login",
            "POST",
            "auth/login", 
            200,
            data=login_data,
            use_auth=False
        )
        
        if response and 'access_token' in response:
            self.token = response['access_token']
            print(f"  🔑 Token obtained: {self.token[:20]}...")
            
            # Test getting current user
            self.run_test(
                "Get current user (/api/auth/me)",
                "GET",
                "auth/me",
                200
            )
        
        # Test login with invalid credentials
        invalid_login = {
            "email": "invalid@example.com", 
            "password": "wrongpass"
        }
        
        self.run_test(
            "Invalid login (should fail)",
            "POST",
            "auth/login",
            401,
            data=invalid_login,
            use_auth=False
        )

    def test_dashboard_apis(self):
        """Test dashboard statistics"""
        print("\n🔍 Testing Dashboard APIs...")
        
        self.run_test(
            "Dashboard stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        self.run_test(
            "Recent activities",
            "GET",
            "dashboard/recent-activities",
            200
        )

    def test_projects_api(self):
        """Test projects API for dropdowns"""
        print("\n🔍 Testing Projects API...")
        
        response = self.run_test(
            "Get projects list",
            "GET",
            "projects",
            200
        )
        
        if response and isinstance(response, list) and len(response) > 0:
            print(f"  📋 Found {len(response)} projects")
            return True
        else:
            print("  ⚠️  No projects found or invalid response")
            return False

    def test_customer_apis(self):
        """Test customer management APIs"""
        print("\n🔍 Testing Customer APIs...")
        
        # Get customers
        customers_response = self.run_test(
            "Get customers list",
            "GET",
            "customers",
            200
        )
        
        # Create a new customer
        test_customer = {
            "name": f"Test Customer {datetime.now().strftime('%H%M%S')}",
            "phone": "9876543210",
            "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
            "father_name": "Test Father",
            "pan_number": "ABCDE1234F",
            "project": "RRL Palm Altezze",
            "tower": "A",
            "unit_number": "101",
            "carpet_area": 1200,
            "saleable_area": 1400,
            "parking": "1 Covered",
            "total_price": 6600000,
            "booking_amount": 500000,
            "booking_date": "2024-01-15"
        }
        
        create_response = self.run_test(
            "Create new customer",
            "POST",
            "customers",
            200,
            data=test_customer
        )
        
        customer_id = None
        if create_response and 'id' in create_response:
            customer_id = create_response['id']
            print(f"  👤 Created customer with ID: {customer_id}")
            
            # Test get specific customer
            self.run_test(
                "Get customer details",
                "GET",
                f"customers/{customer_id}",
                200
            )
            
            # Test update customer
            update_data = {"total_price": 6700000}
            self.run_test(
                "Update customer",
                "PUT",
                f"customers/{customer_id}",
                200,
                data=update_data
            )
        
        return customer_id

    def test_payment_apis(self, customer_id=None):
        """Test payment schedule APIs"""
        print("\n🔍 Testing Payment APIs...")
        
        # Test payments overview
        self.run_test(
            "Get payments overview",
            "GET",
            "payments/overview",
            200
        )
        
        if customer_id:
            # Test get payment schedule
            self.run_test(
                "Get payment schedule",
                "GET",
                f"payments/schedule/{customer_id}",
                200
            )
            
            # Test create payment schedule
            payment_schedule = {
                "customer_id": customer_id,
                "items": [
                    {
                        "installment_name": "Booking Amount",
                        "milestone": "booking",
                        "amount": 500000,
                        "due_date": "2024-01-15",
                        "payment_status": "paid"
                    },
                    {
                        "installment_name": "Agreement Stage",
                        "milestone": "agreement", 
                        "amount": 1000000,
                        "due_date": "2024-02-15",
                        "payment_status": "pending"
                    }
                ]
            }
            
            self.run_test(
                "Create payment schedule",
                "POST",
                "payments/schedule",
                200,
                data=payment_schedule
            )

    def test_calculator_api(self):
        """Test price calculator API"""
        print("\n🔍 Testing Calculator API...")
        
        calculation_data = {
            "carpet_area": 1200,
            "rate_per_sqft": 5500,
            "floor_rise_charges": 50000,
            "parking_charges": 300000,
            "gst_percentage": 5,
            "other_charges": 100000
        }
        
        response = self.run_test(
            "Calculate price",
            "POST",
            "calculator/price",
            200,
            data=calculation_data
        )
        
        if response:
            expected_base = 1200 * 5500  # 6,600,000
            if abs(response.get('base_price', 0) - expected_base) < 1:
                print(f"  💰 Price calculation correct: ₹{response.get('total_agreement_value', 0):,.0f}")
            else:
                print(f"  ⚠️  Price calculation may be incorrect")

    def test_document_apis(self, customer_id=None):
        """Test document generation APIs"""
        print("\n🔍 Testing Document APIs...")
        
        # Test get templates
        self.run_test(
            "Get document templates",
            "GET",
            "templates",
            200
        )
        
        if customer_id:
            # Test document generation
            doc_data = {
                "customer_id": customer_id,
                "doc_type": "sales_agreement",
                "custom_fields": {}
            }
            
            generate_response = self.run_test(
                "Generate sales agreement",
                "POST",
                "documents/generate",
                200,
                data=doc_data
            )
            
            # Test get customer documents
            self.run_test(
                "Get customer documents",
                "GET",
                f"documents/{customer_id}",
                200
            )
            
            # Test document checklist
            self.run_test(
                "Get document checklist",
                "GET",
                f"checklist/{customer_id}",
                200
            )

    def test_communication_apis(self, customer_id=None):
        """Test communication APIs (mocked)"""
        print("\n🔍 Testing Communication APIs...")
        
        if customer_id:
            # Test send email (mocked)
            email_params = f"customer_id={customer_id}&subject=Test Email&message=This is a test email"
            self.run_test(
                "Send email notification (MOCKED)",
                "POST",
                f"communication/email?{email_params}",
                200
            )
            
            # Test send WhatsApp (mocked)
            whatsapp_params = f"customer_id={customer_id}&message=Test WhatsApp message"
            self.run_test(
                "Send WhatsApp notification (MOCKED)",
                "POST",
                f"communication/whatsapp?{whatsapp_params}",
                200
            )
            
            # Test get communication history
            self.run_test(
                "Get communication history",
                "GET",
                f"communication/{customer_id}",
                200
            )

    def test_webhook_api(self):
        """Test Google Forms webhook"""
        print("\n🔍 Testing Webhook APIs...")
        
        webhook_data = {
            "customer_name": f"Webhook Customer {datetime.now().strftime('%H%M%S')}",
            "phone": "9876543211",
            "email": f"webhook{datetime.now().strftime('%H%M%S')}@example.com",
            "project": "RRL Palm Altezze",
            "tower": "B",
            "unit_number": "202",
            "father_name": "Webhook Father",
            "pan_number": "FGHIJ5678K",
            "booking_amount": 300000,
            "booking_date": "2024-01-20"
        }
        
        self.run_test(
            "Google Forms webhook",
            "POST",
            "webhook/google-form",
            200,
            data=webhook_data,
            use_auth=False
        )

    def test_user_management_apis(self):
        """Test user management APIs (admin only)"""
        print("\n🔍 Testing User Management APIs...")
        
        # Get users (admin only)
        self.run_test(
            "Get users list (admin only)",
            "GET",
            "users",
            200
        )

    def run_all_tests(self):
        """Run comprehensive API tests"""
        print("🚀 Starting RRL Builders CRM API Testing...")
        print(f"🌐 Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Basic connectivity
        self.test_health_check()
        
        # Authentication
        self.test_authentication()
        
        if not self.token:
            print("❌ Cannot proceed without authentication token")
            return False
        
        # Core APIs
        self.test_projects_api()
        self.test_dashboard_apis()
        
        # Customer flow
        customer_id = self.test_customer_apis()
        
        # Payment APIs
        self.test_payment_apis(customer_id)
        
        # Calculator
        self.test_calculator_api()
        
        # Documents
        self.test_document_apis(customer_id)
        
        # Communication
        self.test_communication_apis(customer_id)
        
        # Webhook
        self.test_webhook_api()
        
        # Admin APIs
        self.test_user_management_apis()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "0%")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if test['status'] == 'FAILED']
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    try:
        tester = RRLCRMTester()
        
        # Run all tests
        success = tester.run_all_tests()
        
        # Print summary
        all_passed = tester.print_summary()
        
        # Return appropriate exit code
        return 0 if all_passed else 1
        
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Fatal error during testing: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())