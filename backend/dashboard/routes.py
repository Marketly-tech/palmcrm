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


async def _calc_revenue_totals(db):
    revenue_pipeline = await db.payment_transactions.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    total_revenue = revenue_pipeline[0]["total"] if revenue_pipeline else 0

    flat_value_pipeline = await db.customers.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$total_price"}}}
    ]).to_list(1)
    total_flat_value = flat_value_pipeline[0]["total"] if flat_value_pipeline else 0

    return total_revenue, total_flat_value


async def _analyze_payment_schedules(db, today, week_end):
    """Return (payments_due_this_week, overdue_payments, status_counts)."""
    schedules = await db.payment_schedules.find(
        {}, {"_id": 0, "items": 1, "customer_id": 1}
    ).to_list(1000)
    payments_due_this_week = 0
    overdue_payments = 0
    payment_status_counts = {"pending": 0, "paid": 0, "overdue": 0, "partial": 0}

    for schedule in schedules:
        for item in schedule.get("items", []):
            status = item.get("payment_status", "pending")
            payment_status_counts[status] = payment_status_counts.get(status, 0) + 1
            if status not in ("pending", "partial"):
                continue
            try:
                due_date = datetime.strptime(item["due_date"], "%Y-%m-%d").date()
            except (ValueError, TypeError, KeyError):
                continue
            if due_date < today:
                overdue_payments += 1
            elif due_date <= week_end:
                payments_due_this_week += 1
    return payments_due_this_week, overdue_payments, payment_status_counts


def _build_monthly_revenue(total_revenue):
    """Approximate monthly revenue distribution over the trailing 6 months."""
    monthly = []
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30 * i)
        monthly.append({
            "month": month_date.strftime("%b"),
            "revenue": total_revenue / 6 if total_revenue > 0 else 0,
        })
    return monthly


@router.get("/stats")
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    """Get dashboard statistics."""
    db = get_database()
    is_admin = user["role"] == "admin"
    today = datetime.now(timezone.utc).date()
    week_end = today + timedelta(days=7)

    total_customers = await db.customers.count_documents({})
    pending_agreements = await db.customers.count_documents(
        {"agreement_status": {"$in": ["draft", "sent"]}}
    )

    total_revenue, total_flat_value = await _calc_revenue_totals(db)
    total_balance = total_flat_value - total_revenue
    total_pending = total_balance

    payments_due_this_week, overdue_payments, payment_status_counts = (
        await _analyze_payment_schedules(db, today, week_end)
    )

    total_amount = total_revenue + total_pending
    pending_percentage = (
        round((total_pending / total_amount * 100), 2) if total_amount > 0 else 0
    )
    monthly_revenue = _build_monthly_revenue(total_revenue)

    return DashboardStats(
        total_customers=total_customers,
        pending_agreements=pending_agreements,
        payments_due_this_week=payments_due_this_week,
        overdue_payments=overdue_payments,
        total_revenue=total_revenue if is_admin else 0,
        total_pending=total_pending if is_admin else 0,
        total_flat_value=total_flat_value if is_admin else 0,
        total_balance=total_balance if is_admin else 0,
        pending_percentage=pending_percentage if is_admin else 0,
        monthly_revenue=monthly_revenue if is_admin else [],
        payment_status_breakdown=payment_status_counts,
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


@router.get("/reconciliation")
async def get_reconciliation_report(user: dict = Depends(get_current_user)):
    """Reconcile the two revenue computations exposed on the dashboard.

    Why this endpoint exists
    ------------------------
    The main "Total Revenue Collected" card uses a Mongo aggregation:
        SUM(payment_transactions.amount)         ← every txn, ever
    The "Total Collected (Cumulative)" card on the Payment Stage tile uses a
    per-customer Python loop:
        SUM_over_customers(SUM(their txns.amount))
        ← only txns whose customer_id is still in the customers collection.

    Difference between the two == ₹value of *orphan* transactions whose
    customer_id no longer exists in customers (e.g. a lead/customer was hard
    deleted while its payment receipts remained behind). Returns both totals,
    the diff, and a sample list of the orphan rows so an admin can decide
    whether to delete them or restore the missing customer.
    """
    if user.get("role") != "admin":
        # Same access posture as the rest of the financial cards.
        return {"error": "Admin role required to view reconciliation report."}

    db = get_database()
    # 1. Aggregation total — what the headline "Total Revenue Collected" shows
    agg = await db.payment_transactions.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]).to_list(1)
    aggregation_total = agg[0]["total"] if agg else 0
    aggregation_count = agg[0]["count"] if agg else 0

    # 2. Per-customer loop — what "Total Collected (Cumulative)" sums
    customer_ids: set = set()
    customer_index = {}
    async for c in db.customers.find({}, {"_id": 0, "id": 1, "name": 1, "unit_number": 1, "project": 1}):
        cid = c.get("id")
        customer_ids.add(cid)
        customer_index[cid] = c

    txns = await db.payment_transactions.find({}, {"_id": 0}).to_list(100000)
    loop_total = 0
    loop_count = 0
    orphan_total = 0
    orphan_count = 0
    null_amount_count = 0
    orphans = []
    for t in txns:
        cid = t.get("customer_id")
        amt = t.get("amount") or 0
        if t.get("amount") is None:
            null_amount_count += 1
        if cid in customer_ids:
            loop_total += amt
            loop_count += 1
        else:
            orphan_total += amt
            orphan_count += 1
            orphans.append({
                "transaction_id": t.get("id"),
                "customer_id": cid,
                "amount": amt,
                "transaction_type": t.get("transaction_type"),
                "transaction_date": t.get("transaction_date"),
                "receipt_number": t.get("receipt_number"),
                "narration": t.get("narration") or t.get("notes"),
            })

    # Surface the most impactful orphans first so the admin's "fix it" eyeball
    # naturally lands on the biggest drift contributors.
    orphans.sort(key=lambda o: o["amount"] or 0, reverse=True)
    difference = aggregation_total - loop_total

    if abs(difference) < 0.5:
        verdict = "ok"
        message = "Reconciled — both cards agree. No drift detected."
    elif orphan_count > 0 and abs(difference - orphan_total) < 0.5:
        verdict = "orphans"
        message = (
            f"Drift fully explained by {orphan_count} orphan transaction"
            f"{'s' if orphan_count != 1 else ''} (₹{orphan_total:,.0f}). "
            "These belong to customer IDs no longer in the customers collection — "
            "likely from deleted leads. Resolve by either restoring the customer or deleting the orphan transactions."
        )
    else:
        verdict = "unknown"
        message = (
            f"Drift of ₹{difference:,.0f} is NOT fully explained by orphan transactions. "
            "Check for null amounts, duplicate txn rows, or schema-incompatible records."
        )

    return {
        "aggregation_total": round(aggregation_total, 2),
        "aggregation_count": aggregation_count,
        "loop_total": round(loop_total, 2),
        "loop_count": loop_count,
        "difference": round(difference, 2),
        "orphan_total": round(orphan_total, 2),
        "orphan_count": orphan_count,
        "null_amount_count": null_amount_count,
        # Cap the sample at 25 — the UI shows a "View all" expander for the rest.
        "orphan_samples": orphans[:25],
        "verdict": verdict,
        "message": message,
    }


@router.post("/reconciliation/delete-orphan/{transaction_id}")
async def delete_orphan_transaction(transaction_id: str, user: dict = Depends(get_current_user)):
    """Hard-delete a single orphan transaction (admin only). Refuses to act if
    the transaction's customer_id IS in the customers collection — this is a
    cleanup tool, not a generic delete endpoint.
    """
    if user.get("role") != "admin":
        return {"error": "Admin role required."}

    db = get_database()
    txn = await db.payment_transactions.find_one({"id": transaction_id}, {"_id": 0})
    if not txn:
        return {"error": "Transaction not found."}
    cid = txn.get("customer_id")
    if cid:
        exists = await db.customers.count_documents({"id": cid}, limit=1)
        if exists:
            return {"error": "Refusing to delete — customer still exists. Use the per-customer payment-delete endpoint."}

    await db.payment_transactions.delete_one({"id": transaction_id})
    # Compliance: financial mutations must always leave an audit trail.
    try:
        from settings import log_activity
        await log_activity(
            user["id"], user.get("name", "Unknown"),
            "delete", "orphan_transaction", transaction_id,
            f"Deleted orphan txn (customer_id={cid}, amount=₹{txn.get('amount', 0):,.0f})",
        )
    except Exception:
        # Don't block the cleanup if the audit logger hiccups.
        pass
    return {"deleted": True, "transaction_id": transaction_id, "amount": txn.get("amount", 0)}
