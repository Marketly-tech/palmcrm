"""
Dashboard module for RRL CRM.
"""
from dashboard.routes import router
from dashboard.models import DashboardStats

__all__ = [
    "router",
    "DashboardStats",
]
