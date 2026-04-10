"""
Email service module for RRL CRM.
"""
from email_service.routes import router as email_router

__all__ = [
    "email_router",
]
