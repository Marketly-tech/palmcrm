"""
Configuration module for RRL CRM backend.
Centralizes all environment variables and app settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    MONGO_URL: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    DB_NAME: str = os.environ.get("DB_NAME", "test_database")
    
    # JWT
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "rrl-crm-secure-jwt-secret-2026-prod")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # SendGrid
    SENDGRID_API_KEY: str = os.environ.get("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL: str = os.environ.get("SENDGRID_FROM_EMAIL", "crm@rrlbuildersanddevelopers.com")
    SENDGRID_FROM_NAME: str = os.environ.get("SENDGRID_FROM_NAME", "RRL Group")
    
    # CORS
    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")
    
    # Company Info
    COMPANY_NAME: str = "RRL Builders & Developers"
    COMPANY_TAGLINE: str = "Beyond homes. A lifestyle"
    COMPANY_ADDRESS: str = "No.54, 1ST FLOOR, 5TH CROSS, RBI LAYOUT, JP NAGAR 7TH PHASE, BANGALORE-560078"
    COMPANY_PHONE: str = "9845082999"
    COMPANY_GSTIN: str = "29AAFFR0821H1ZI"
    COMPANY_RERA: str = "PRM/KA/RERA/1251/446/PR/220413/004905"


settings = Settings()
