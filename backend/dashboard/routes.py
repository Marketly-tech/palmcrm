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


# ---------------------------------------------------------------------------
# Bank Disbursement Summary (admin)
# ---------------------------------------------------------------------------
# Bank-name normalization
# ---------------------------------------------------------------------------
# Suffixes that are part of the corporate name / loan-product label but not
# the bank identity. Stripped iteratively (case-insensitive, already upper).
_BANK_SUFFIXES_TO_STRIP = (
    " HOME LOAN",
    " HOUSING LOAN",
    " HOUSING FINANCE",
    " HOME FINANCE",
    " BANK LTD.",
    " BANK LIMITED",
    " BANK LTD",
    " BANK",
    " LIMITED",
    " LTD.",
    " LTD",
    " LOAN",
    " FINANCE",
)

# Canonical display labels for common variants. The key is the *fully-stripped
# uppercase* form (i.e. after suffix-strip); the value is the pretty display
# label the dashboard renders. Add aliases here rather than fanning out the
# suffix stripper — keeps the mapping declarative and grep-friendly.
_BANK_CANONICAL_MAP: dict[str, str] = {
    # Bank of Baroda
    "BOB": "Bank of Baroda",
    "BOB LOAN": "Bank of Baroda",
    "BANK OF BARODA": "Bank of Baroda",
    "BARODA": "Bank of Baroda",
    # HDFC
    "HDFC": "HDFC Bank",
    "HDC": "HDFC Bank",  # Common data-entry typo captured from live data.
    "HDFC HOUSING": "HDFC Bank",
    "HDFC HOUSING DEVELOPMENT FINANCE CORPORATION": "HDFC Bank",
    # Canara
    "CANARA": "Canara Bank",
    "CANNARA": "Canara Bank",
    # SBI
    "SBI": "State Bank of India",
    "STATE BANK OF INDIA": "State Bank of India",
    "STATE BANK": "State Bank of India",
    # ICICI
    "ICICI": "ICICI Bank",
    # Axis
    "AXIS": "Axis Bank",
    # Kotak
    "KOTAK": "Kotak Mahindra Bank",
    "KOTAK MAHINDRA": "Kotak Mahindra Bank",
    # IDBI / IDFC
    "IDBI": "IDBI Bank",
    "IDFC": "IDFC First Bank",
    "IDFC FIRST": "IDFC First Bank",
    # Public sector
    "PNB": "Punjab National Bank",
    "PUNJAB NATIONAL": "Punjab National Bank",
    "UNION": "Union Bank of India",
    "UNION BANK OF INDIA": "Union Bank of India",
    "INDIAN": "Indian Bank",
    "INDIAN OVERSEAS": "Indian Overseas Bank",
    "IOB": "Indian Overseas Bank",
    "UCO": "UCO Bank",
    "CENTRAL": "Central Bank of India",
    "CENTRAL BANK OF INDIA": "Central Bank of India",
    "BANK OF INDIA": "Bank of India",
    "BOI": "Bank of India",
    "BANK OF MAHARASHTRA": "Bank of Maharashtra",
    "BOM": "Bank of Maharashtra",
    # Private
    "YES": "Yes Bank",
    "FEDERAL": "Federal Bank",
    "SOUTH INDIAN": "South Indian Bank",
    "KARNATAKA": "Karnataka Bank",
    "KARUR VYSYA": "Karur Vysya Bank",
    "RBL": "RBL Bank",
    "INDUSIND": "IndusInd Bank",
    # NBFCs commonly used for home loans
    "LIC HOUSING": "LIC Housing Finance",
    "LICHFL": "LIC Housing Finance",
    "TATA CAPITAL": "Tata Capital",
    "TATA CAPITAL HOUSING": "Tata Capital",
    "BAJAJ": "Bajaj Finance",
    "BAJAJ HOUSING": "Bajaj Housing Finance",
    "BAJAJ FINSERV": "Bajaj Finance",
    "PIRAMAL": "Piramal Finance",
    "PNB HOUSING": "PNB Housing Finance",
    "GRUH": "GRUH Finance",
    "DHFL": "DHFL",
    # Placeholder
    "UNSPECIFIED": "Unspecified",
}


def _normalize_bank(raw: Optional[str]) -> str:
    """Collapse bank-name variants into a canonical display label.

    Pipeline:
      1. Uppercase + trim (also normalize interior whitespace).
      2. Iteratively strip loan/product/corporate suffixes
         ("BANK", "LOAN", "HOME LOAN", "LTD.", "LIMITED", "FINANCE" etc.)
         until the string stops changing.
      3. Look the residue up in ``_BANK_CANONICAL_MAP``; if found, return
         the pretty label. Otherwise return the stripped uppercase residue
         so unknown banks still surface (rather than getting bucketed into
         a catch-all).
    """
    if not raw:
        return _BANK_CANONICAL_MAP["UNSPECIFIED"]
    s = " ".join(str(raw).strip().upper().split())
    if not s:
        return _BANK_CANONICAL_MAP["UNSPECIFIED"]
    changed = True
    while changed:
        changed = False
        for suf in _BANK_SUFFIXES_TO_STRIP:
            if s.endswith(suf):
                s = s[: -len(suf)].strip()
                changed = True
    if not s:
        return _BANK_CANONICAL_MAP["UNSPECIFIED"]
    return _BANK_CANONICAL_MAP.get(s, s.title())


@router.get("/disbursement-summary")
async def get_disbursement_summary(user: dict = Depends(get_current_user)):
    """Per-bank disbursement snapshot for the main dashboard (admin only).

    Aggregates a per-bank row (grouped on the *normalized* canonical bank
    name) with these columns:
      • **Sanctioned** (``loan_amount``) — SUM of ``customers.loan_amount``
        for every customer with a positive ``loan_amount``. NO filter on
        ``finance_type`` — a record entered as ``self`` or blank still
        counts if the admin captured a loan figure, so lenders' books
        match the CRM.
      • **Loans** (``customer_count``) — unique customer count per bank.
      • **Total Disbursed** — SUM(amount) of ``payment_transactions`` rows
        whose ``transaction_stage == 'scheduled_disbursement'``, grouped
        by the bank (customer's ``finance_bank`` preferred, transaction's
        own ``bank_name`` as fallback).
      • **Pending** — ``max(SUM(customers.total_price) − Total Disbursed, 0)``
        per bank. Formulated as "total flat value assigned to this bank
        minus what the bank has already disbursed" so accounts sees the
        remaining amount they still have to collect from each lender.

    Orphan scheduled_disbursement rows (customer_id no longer in the
    customers collection) are surfaced separately under ``unmatched`` so
    the grand total stays accurate and an admin can clean them up via
    ``POST /api/dashboard/reconciliation/delete-orphan/{transaction_id}``.
    """
    if user.get("role") != "admin":
        return {"error": "Admin role required."}

    db = get_database()

    # 1. Index every customer that has a positive loan_amount — regardless of
    #    finance_type (some records are booked as 'self' but still carry a
    #    partial loan figure that the bank has sanctioned).
    financed_customers = await db.customers.find(
        {"loan_amount": {"$gt": 0}},
        {"_id": 0, "id": 1, "name": 1, "unit_number": 1, "project": 1,
         "finance_bank": 1, "loan_amount": 1, "total_price": 1,
         "finance_type": 1},
    ).to_list(10000)
    customer_index = {c.get("id"): c for c in financed_customers}

    # 2. Index the full customer set (for orphan detection).
    all_customer_ids: set = set()
    async for c in db.customers.find({}, {"_id": 0, "id": 1}):
        all_customer_ids.add(c.get("id"))

    # 3. Pull every scheduled_disbursement transaction.
    txns = await db.payment_transactions.find(
        {"transaction_stage": "scheduled_disbursement"},
        {"_id": 0, "id": 1, "customer_id": 1, "amount": 1, "bank_name": 1,
         "transaction_date": 1, "transaction_number": 1, "notes": 1},
    ).to_list(100000)

    per_bank: dict[str, dict] = {}
    disbursed_by_customer: dict[str, float] = {}
    unmatched: list[dict] = []
    unmatched_total = 0.0

    def _bucket(name: str) -> dict:
        return per_bank.setdefault(
            name,
            {"bank": name, "total_disbursed": 0.0, "flat_value_total": 0.0,
             "loan_amount": 0.0, "customer_count": 0, "customer_ids": set()},
        )

    for t in txns:
        amt = float(t.get("amount") or 0)
        cid = t.get("customer_id")
        cust = customer_index.get(cid)
        # Bank preference: financed customer's bank > txn's own bank_name.
        raw_bank = (cust or {}).get("finance_bank") or t.get("bank_name")
        bank = _normalize_bank(raw_bank)

        if cid and cid not in all_customer_ids:
            unmatched.append({
                "transaction_id": t.get("id"),
                "customer_id": cid,
                "amount": amt,
                "bank_name": t.get("bank_name") or "",
                "transaction_date": t.get("transaction_date") or "",
                "transaction_number": t.get("transaction_number") or "",
                "notes": t.get("notes") or "",
            })
            unmatched_total += amt
            continue

        _bucket(bank)["total_disbursed"] += amt
        if cid:
            disbursed_by_customer[cid] = disbursed_by_customer.get(cid, 0.0) + amt

    # 4. Roll up per-customer sanctioned & flat_value → bank buckets. Use a
    #    set to compute a unique customer_count in case the same customer
    #    somehow gets indexed twice.
    grand_loan = 0.0
    grand_flat_value = 0.0
    for c in financed_customers:
        cid = c.get("id")
        loan = float(c.get("loan_amount") or 0)
        flat_value = float(c.get("total_price") or 0)
        bank = _normalize_bank(c.get("finance_bank"))
        row = _bucket(bank)
        row["loan_amount"] += loan
        row["flat_value_total"] += flat_value
        if cid:
            row["customer_ids"].add(cid)
        grand_loan += loan
        grand_flat_value += flat_value

    # 5. Finalize each bank row.
    grand_pending = 0.0
    banks: list[dict] = []
    for b in per_bank.values():
        disbursed = b["total_disbursed"]
        flat_value = b["flat_value_total"]
        # Pending = remaining flat value still to be disbursed by this bank.
        # Floor at 0 so an over-disbursed edge case doesn't show a negative.
        pending = max(flat_value - disbursed, 0.0)
        grand_pending += pending
        banks.append({
            "bank": b["bank"],
            "total_disbursed": round(disbursed, 2),
            "pending_disbursement": round(pending, 2),
            "loan_amount": round(b["loan_amount"], 2),
            "flat_value_total": round(flat_value, 2),
            "customer_count": len(b["customer_ids"]),
        })

    banks.sort(key=lambda r: r["pending_disbursement"], reverse=True)

    grand_disbursed = sum(b["total_disbursed"] for b in banks)

    unmatched.sort(key=lambda o: o["amount"] or 0, reverse=True)

    return {
        "grand_total_disbursed": round(grand_disbursed, 2),
        "grand_total_pending": round(grand_pending, 2),
        "grand_total_loan": round(grand_loan, 2),
        "grand_total_flat_value": round(grand_flat_value, 2),
        "banks": banks,
        "unmatched_total": round(unmatched_total, 2),
        "unmatched_count": len(unmatched),
        "unmatched": unmatched[:50],
    }


# ---------------------------------------------------------------------------
# One-shot legacy backfill endpoint
# ---------------------------------------------------------------------------
# Purpose: for customers created between two ISO-date-strings (typically the
# early-onboarding batch RRL-00025..RRL-00035 created 2026-03-20 → 2026-03-22),
# explicitly set ``club_house_charges`` and ``additional_parking_charges``
# to 0 when they are currently null / missing / empty-string. This is a
# read-repair for legacy records that predate the "0 is respected" fix, so
# their UI cards and Price Breakup PDFs agree on the exact same numbers.
#
# Design guarantees:
#   1. Admin-only.
#   2. Idempotent — only touches rows where the field is null/missing/"";
#      any non-null value (even if it's 0 already) is left alone.
#   3. Dry-run by default — must pass ``?apply=true`` to actually mutate.
#   4. Returns a full audit trail (candidate ids, modified counts, verify pass).
# ---------------------------------------------------------------------------
@router.post("/backfill/legacy-zero-charges")
async def backfill_legacy_zero_charges(
    start_date: str = "2026-03-20",
    end_date_exclusive: str = "2026-03-23",
    apply: bool = False,
    user: dict = Depends(get_current_user),
):
    """Backfill null club_house_charges / additional_parking_charges → 0 for
    customers created in ``[start_date, end_date_exclusive)``.

    Args (query string):
      • ``start_date`` (inclusive, YYYY-MM-DD)   — default 2026-03-20
      • ``end_date_exclusive`` (YYYY-MM-DD)      — default 2026-03-23
      • ``apply`` (bool)                          — default false (dry-run)

    Response:
      ``{"candidates": [...], "would_update": {...}, "applied": {...} | null,
         "verify": {"in_window": N, "still_null": M}}``
    """
    if user.get("role") != "admin":
        return {"error": "Admin role required."}

    db = get_database()
    date_filter = {"created_at": {"$gte": start_date, "$lt": end_date_exclusive}}

    # Candidates: any row in window with at least one null/missing charge field.
    null_or_missing_or_empty = {"$in": [None, ""]}
    candidate_q = {
        **date_filter,
        "$or": [
            {"club_house_charges": null_or_missing_or_empty},
            {"additional_parking_charges": null_or_missing_or_empty},
            {"club_house_charges": {"$exists": False}},
            {"additional_parking_charges": {"$exists": False}},
        ],
    }
    candidates = await db.customers.find(
        candidate_q,
        {"_id": 0, "id": 1, "customer_id": 1, "name": 1, "created_at": 1,
         "club_house_charges": 1, "additional_parking_charges": 1},
    ).to_list(1000)

    # Per-field candidate counts (what an update_many WOULD hit).
    club_would = await db.customers.count_documents({
        **date_filter,
        "$or": [
            {"club_house_charges": None},
            {"club_house_charges": ""},
            {"club_house_charges": {"$exists": False}},
        ],
    })
    parking_would = await db.customers.count_documents({
        **date_filter,
        "$or": [
            {"additional_parking_charges": None},
            {"additional_parking_charges": ""},
            {"additional_parking_charges": {"$exists": False}},
        ],
    })

    applied = None
    if apply:
        club_result = await db.customers.update_many(
            {
                **date_filter,
                "$or": [
                    {"club_house_charges": None},
                    {"club_house_charges": ""},
                    {"club_house_charges": {"$exists": False}},
                ],
            },
            {"$set": {"club_house_charges": 0}},
        )
        parking_result = await db.customers.update_many(
            {
                **date_filter,
                "$or": [
                    {"additional_parking_charges": None},
                    {"additional_parking_charges": ""},
                    {"additional_parking_charges": {"$exists": False}},
                ],
            },
            {"$set": {"additional_parking_charges": 0}},
        )
        applied = {
            "club_house_charges_modified": club_result.modified_count,
            "additional_parking_charges_modified": parking_result.modified_count,
        }

    # Verify: after apply, count anything in-window that STILL has null.
    in_window = await db.customers.count_documents(date_filter)
    still_null = await db.customers.count_documents({
        **date_filter,
        "$or": [
            {"club_house_charges": null_or_missing_or_empty},
            {"additional_parking_charges": null_or_missing_or_empty},
            {"club_house_charges": {"$exists": False}},
            {"additional_parking_charges": {"$exists": False}},
        ],
    })

    return {
        "dry_run": not apply,
        "window": {"start": start_date, "end_exclusive": end_date_exclusive},
        "candidates": [
            {
                "customer_id": c.get("customer_id") or c.get("id"),
                "name": c.get("name"),
                "created_at": c.get("created_at"),
                "club_house_charges": c.get("club_house_charges"),
                "additional_parking_charges": c.get("additional_parking_charges"),
            }
            for c in candidates
        ],
        "would_update": {
            "club_house_charges": club_would,
            "additional_parking_charges": parking_would,
        },
        "applied": applied,
        "verify": {"in_window": in_window, "still_null": still_null},
    }
