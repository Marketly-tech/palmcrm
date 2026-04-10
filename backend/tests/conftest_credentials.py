"""
Shared test configuration for RRL CRM test suite.
Reads credentials from environment variables to avoid hardcoded secrets.
"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Test server URL
TEST_BASE_URL = os.environ.get(
    "REACT_APP_BACKEND_URL",
    os.environ.get("TEST_BASE_URL", "http://localhost:8001")
)
API_URL = f"{TEST_BASE_URL}/api"

# Admin credentials (from environment)
ADMIN_EMAIL = os.environ.get("TEST_ADMIN_EMAIL", "crm@rrlbuildersanddevelopers.com")
ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "#RRLnew2026")

# Accounts role credentials
ACCOUNTS_EMAIL = os.environ.get("TEST_ACCOUNTS_EMAIL", "accounts@rrlbuilders.com")
ACCOUNTS_PASSWORD = os.environ.get("TEST_ACCOUNTS_PASSWORD", "accounts123")

# Test customer - Ramya test lead ONLY
TEST_CUSTOMER_UUID = os.environ.get("TEST_CUSTOMER_UUID", "6d902613-5106-4294-bc3e-b907f85127f7")
TEST_CUSTOMER_ID = os.environ.get("TEST_CUSTOMER_ID", "RRL-00036")
TEST_CUSTOMER_NAME = os.environ.get("TEST_CUSTOMER_NAME", "Ramya test lead")
