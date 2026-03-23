"""
Dashboard models for RRL CRM.
"""
from typing import List, Dict, Any
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_customers: int
    pending_agreements: int
    payments_due_this_week: int
    overdue_payments: int
    total_revenue: float
    total_pending: float
    total_flat_value: float
    total_balance: float
    pending_percentage: float
    monthly_revenue: List[Dict[str, Any]]
    payment_status_breakdown: Dict[str, int]
