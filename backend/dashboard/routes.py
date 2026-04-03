"""
Dashboard routes for RRL CRM.
"""
from typing import Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
import logging

from database import get_database
from auth import get_current_user
from dashboard.models import DashboardStats

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    """Get dashboard statistics."""
    db = get_database()
    total_customers = await db.customers.count_documents({})
    pending_agreements = await db.customers.count_documents({"agreement_status": {"$in": ["draft", "sent"]}})
    
    # Calculate payments
    today = datetime.now(timezone.utc).date()
    week_end = today + timedelta(days=7)
    
    # === REVENUE CALCULATION USING AGGREGATION ===
    revenue_pipeline = await db.payment_transactions.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    total_revenue = revenue_pipeline[0]["total"] if revenue_pipeline else 0
    
    # Get total flat value using aggregation
    flat_value_pipeline = await db.customers.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$total_price"}}}
    ]).to_list(1)
    total_flat_value = flat_value_pipeline[0]["total"] if flat_value_pipeline else 0
    
    # Total revenue = sum of all transactions (booking amounts are already included as transactions)
    # No need to add booking_amount separately
    
    # Total balance = total flat value - total revenue collected
    total_balance = total_flat_value - total_revenue
    
    # Total pending = same as balance
    total_pending = total_balance
    
    # === PAYMENT SCHEDULE ANALYSIS (for due dates) ===
    schedules = await db.payment_schedules.find({}, {"_id": 0, "items": 1, "customer_id": 1}).to_list(1000)
    
    payments_due_this_week = 0
    overdue_payments = 0
    payment_status_counts = {"pending": 0, "paid": 0, "overdue": 0, "partial": 0}
    
    for schedule in schedules:
        for item in schedule.get('items', []):
            status = item.get('payment_status', 'pending')
            payment_status_counts[status] = payment_status_counts.get(status, 0) + 1
            
            if status in ['pending', 'partial']:
                try:
                    due_date = datetime.strptime(item['due_date'], "%Y-%m-%d").date()
                    if due_date < today:
                        overdue_payments += 1
                    elif due_date <= week_end:
                        payments_due_this_week += 1
                except (ValueError, TypeError):
                    pass
    
    # Calculate pending percentage
    total_amount = total_revenue + total_pending
    pending_percentage = round((total_pending / total_amount * 100), 2) if total_amount > 0 else 0
    
    # Monthly revenue (last 6 months)
    monthly_revenue = []
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        month_name = month_date.strftime("%b")
        monthly_revenue.append({"month": month_name, "revenue": total_revenue / 6 if total_revenue > 0 else 0})
    
    return DashboardStats(
        total_customers=total_customers,
        pending_agreements=pending_agreements,
        payments_due_this_week=payments_due_this_week,
        overdue_payments=overdue_payments,
        total_revenue=total_revenue if user['role'] == 'admin' else 0,
        total_pending=total_pending if user['role'] == 'admin' else 0,
        total_flat_value=total_flat_value if user['role'] == 'admin' else 0,
        total_balance=total_balance if user['role'] == 'admin' else 0,
        pending_percentage=pending_percentage if user['role'] == 'admin' else 0,
        monthly_revenue=monthly_revenue if user['role'] == 'admin' else [],
        payment_status_breakdown=payment_status_counts
    )


@router.get("/recent-activities")
async def get_recent_activities(limit: int = 20, user: dict = Depends(get_current_user)):
    """Get recent activity logs."""
    db = get_database()
    activities = await db.activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return activities


@router.get("/upcoming-due-dates")
async def get_upcoming_due_dates(user: dict = Depends(get_current_user)):
    """
    Get customers with payment due dates in the next 5 days.
    Due date rule: 10 days from booking date.
    """
    db = get_database()
    today = datetime.now(timezone.utc).date()
    
    # Get all customers
    customers = await db.customers.find(
        {"stage": {"$ne": "pending_approval"}},
        {"_id": 0}
    ).to_list(1000)
    
    upcoming = []
    
    for customer in customers:
        booking_date_str = customer.get('booking_date')
        if not booking_date_str:
            continue
        
        try:
            # Parse booking date
            if isinstance(booking_date_str, str):
                booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
            else:
                booking_date = booking_date_str
            
            # Due date is 10 days from booking date
            due_date = booking_date + timedelta(days=10)
            
            # Check if due date is within next 5 days (including overdue up to 3 days)
            days_until_due = (due_date - today).days
            
            if -3 <= days_until_due <= 5:
                upcoming.append({
                    "customer_id": customer.get('id'),
                    "customer_name": customer.get('name'),
                    "project": customer.get('project'),
                    "unit_number": customer.get('unit_number'),
                    "booking_date": booking_date.isoformat(),
                    "due_date": due_date.isoformat(),
                    "days_until_due": days_until_due,
                    "total_price": customer.get('total_price', 0),
                    "balance_amount": customer.get('balance_amount', 0),
                })
        except Exception as e:
            logger.error(f"Error parsing dates for customer {customer.get('id')}: {e}")
            continue
    
    # Sort by due date (closest first)
    upcoming.sort(key=lambda x: x['days_until_due'])
    
    return upcoming
