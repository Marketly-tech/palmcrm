"""Dashboard module initialization."""
from typing import Optional, List
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_customers: int
    total_leads: int
    total_booked: int
    total_flat_value: float = 0
    total_revenue: float = 0
    pending_payments: float = 0
    total_balance: float = 0
    upcoming_due: int = 0
    overdue: int = 0
    recent_bookings: int = 0


class GoogleFormWebhook(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    project: Optional[str] = None
    bhk_type: Optional[str] = None
    source: Optional[str] = "Google Form"
