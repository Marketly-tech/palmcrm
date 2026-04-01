"""
Shared test configuration for RRL CRM test suite.
Reads credentials from environment variables to avoid hardcoded secrets.
"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Test server URL
TEST_BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8001")
API_URL = f"{TEST_BASE_URL}/api"

# Admin credentials (from environment)
ADMIN_EMAIL = os.environ.get("TEST_ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "")

# Accounts role credentials
ACCOUNTS_EMAIL = os.environ.get("TEST_ACCOUNTS_EMAIL", "")
ACCOUNTS_PASSWORD = os.environ.get("TEST_ACCOUNTS_PASSWORD", "")

# Test customer
TEST_CUSTOMER_ID = os.environ.get("TEST_CUSTOMER_ID", "")
TEST_CUSTOMER_NAME = os.environ.get("TEST_CUSTOMER_NAME", "Ramya test lead")
