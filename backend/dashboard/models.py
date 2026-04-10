"""
Dashboard models for RRL CRM.
"""
from typing import List, Dict, Any, Optional
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
    current_stage: Optional[str] = None
    current_stage_name: Optional[str] = None
    stage_overdue_count: int = 0
    stage_overdue_amount: float = 0
    overdue_customers: List[Dict[str, Any]] = []


class EmailSendRequest(BaseModel):
    email_type: str
    subject: str
    body: str
    recipient_email: Optional[str] = None
    cc: Optional[str] = None
