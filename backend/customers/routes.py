"""
Customer routes for RRL CRM.
Handles customer CRUD operations.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import base64
import re
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pymongo import ReturnDocument

from database import get_database
from utils.enums import UserRole
from auth import get_current_user, log_activity, check_role
from customers.models import Customer, CustomerCreate, DocumentChecklist
from utils.banks import to_canonical, aliases_for

# Create router
router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/banks")
async def get_unique_banks(user: dict = Depends(get_current_user)):
    """Get canonical bank names sourced from the **Bank Opted for Loan** field
    (`bank_name` + `bank_name_other` for "Others") for the customer filter dropdown.

    Booking-form bank (`finance_bank`) is intentionally NOT used here — the
    "opted for" bank is the authoritative one customers chose during booking
    finalization.
    """
    db = get_database()
    raw_banks = await db.customers.distinct("bank_name")
    other_banks = await db.customers.distinct(
        "bank_name_other", {"bank_name": "Others"}
    )
    canonical_set = set()
    for raw in list(raw_banks) + list(other_banks):
        if raw == "Others":
            continue  # placeholder, real value lives in bank_name_other
        canonical = to_canonical(raw)
        if canonical:
            canonical_set.add(canonical)
    return sorted(canonical_set)


@router.get("/banks/registry")
async def get_bank_registry(user: dict = Depends(get_current_user)):
    """Canonical bank list used by frontend Select inputs."""
    from utils.banks import list_canonical_names
    return list_canonical_names()


async def generate_customer_id():
    """Generate unique customer ID using atomic counter."""
    db = get_database()
    result = await db.counters.find_one_and_update(
        {"_id": "customer_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return f"RRL-{str(result['seq']).zfill(5)}"


@router.post("", response_model=Dict[str, Any])
async def create_customer(customer_data: CustomerCreate, user: dict = Depends(get_current_user)):
    """Create a new customer."""
    db = get_database()
    customer = Customer(**customer_data.model_dump())
    customer.customer_id = await generate_customer_id()
    customer.created_by = user['id']
    
    doc = customer.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.customers.insert_one(doc)
    
    # Create default document checklist
    checklist = DocumentChecklist(customer_id=customer.id)
    checklist_doc = checklist.model_dump()
    checklist_doc['updated_at'] = checklist_doc['updated_at'].isoformat()
    await db.document_checklists.insert_one(checklist_doc)
    
    await log_activity(user['id'], user['name'], "create", "customer", customer.id, f"Created customer {customer.name}")
    
    return {**doc, "_id": None}


def _build_customer_query(search, project, agreement_status, finance_bank, agreement_filter):
    """Build MongoDB query from filter parameters."""
    and_clauses = []
    if search:
        and_clauses.append({"$or": [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"customer_id": {"$regex": search, "$options": "i"}},
            {"unit_number": {"$regex": search, "$options": "i"}}
        ]})
    base = {}
    if project:
        base["project"] = project
    if agreement_status:
        base["agreement_status"] = agreement_status
    if agreement_filter == "pending_agreement":
        base["agreement_status"] = {"$in": ["draft", "sent"]}
    elif agreement_filter == "agreement_due":
        base["agreement_status"] = "sent"
    if finance_bank:
        # NOTE: the query param is still named `finance_bank` for backwards-compat,
        # but it filters the **Bank Opted for Loan** field (`bank_name` /
        # `bank_name_other`), not the booking-form bank.
        canonical = to_canonical(finance_bank) or finance_bank
        alias_patterns = [re.escape(a) for a in aliases_for(canonical)]
        regex = {"$regex": f"^({'|'.join(alias_patterns)})$", "$options": "i"}
        and_clauses.append({"$or": [
            {"bank_name": regex},
            {"bank_name": "Others", "bank_name_other": regex},
        ]})
    if and_clauses:
        base["$and"] = and_clauses
    return base


def _filter_upcoming_due(customers, limit):
    """Post-filter customers by upcoming due date."""
    today = datetime.now(timezone.utc).date()
    filtered = []
    for customer in customers:
        booking_date_str = customer.get('booking_date')
        if not booking_date_str:
            continue
        try:
            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date() if isinstance(booking_date_str, str) else booking_date_str
            due_date = booking_date + timedelta(days=10)
            days_until_due = (due_date - today).days
            if -3 <= days_until_due <= 5:
                customer['_due_date'] = due_date.isoformat()
                customer['_days_until_due'] = days_until_due
                filtered.append(customer)
        except Exception:
            continue
    filtered.sort(key=lambda x: x.get('_days_until_due', 999))
    return filtered[:limit]


async def _enrich_with_overdue(db, customers):
    """Add _overdue_amount to each customer based on current payment stage."""
    from utils.payment_helpers import PAYMENT_STAGES
    settings_doc = await db.settings.find_one({"type": "payment_stage"}, {"_id": 0})
    cumulative_pct = 0
    if settings_doc and settings_doc.get("current_stage"):
        stage_info = next((s for s in PAYMENT_STAGES if s["key"] == settings_doc["current_stage"]), None)
        if stage_info:
            cumulative_pct = stage_info["cumulative"]

    customer_ids = [c["id"] for c in customers]
    all_txns = await db.payment_transactions.find(
        {"customer_id": {"$in": customer_ids}}, {"_id": 0, "customer_id": 1, "amount": 1}
    ).to_list(100000)
    txn_totals = {}
    for txn in all_txns:
        cid = txn.get("customer_id")
        txn_totals[cid] = txn_totals.get(cid, 0) + (txn.get("amount", 0) or 0)

    for customer in customers:
        total_price = customer.get("total_price", 0) or 0
        expected = (total_price * cumulative_pct) / 100
        customer["_overdue_amount"] = round(max(0, expected - txn_totals.get(customer["id"], 0)), 2)


@router.get("")
async def get_customers(
    search: Optional[str] = None,
    project: Optional[str] = None,
    agreement_status: Optional[str] = None,
    agreement_filter: Optional[str] = None,
    finance_bank: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """Get customers with filters."""
    db = get_database()
    query = _build_customer_query(search, project, agreement_status, finance_bank, agreement_filter)

    fetch_limit = limit * 2 if agreement_filter == "upcoming_due" else limit
    customers = await db.customers.find(query, {"_id": 0}).skip(skip).limit(fetch_limit).to_list(fetch_limit)

    if agreement_filter == "upcoming_due":
        customers = _filter_upcoming_due(customers, limit)

    if finance_bank or agreement_filter == "overdue":
        await _enrich_with_overdue(db, customers)

    # Derive latest_call_status for the Customers list column. We only surface
    # the *most recent* follow-up entry's status — the column is intentionally
    # a quick at-a-glance view; full multi-level history lives on the profile.
    for c in customers:
        fus = c.get("follow_ups") or []
        if fus:
            latest = max(fus, key=lambda f: f.get("created_at") or "")
            c["latest_call_status"] = latest.get("status")
            c["latest_call_status_at"] = latest.get("created_at")
            c["latest_call_status_stage"] = latest.get("stage_name")
        else:
            c["latest_call_status"] = None

    total = await db.customers.count_documents(query) if agreement_filter != "upcoming_due" else len(customers)
    return {"customers": customers, "total": total}


@router.get("/{customer_id}")
async def get_customer(customer_id: str, user: dict = Depends(get_current_user)):
    """Get a single customer by ID."""
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}")
async def update_customer(customer_id: str, updates: Dict[str, Any], user: dict = Depends(get_current_user)):
    """Update a customer."""
    db = get_database()
    # Accounts role can only update agreement_status, not other customer details
    if user['role'] == 'accounts':
        allowed_fields = {'agreement_status'}
        if not set(updates.keys()).issubset(allowed_fields):
            raise HTTPException(status_code=403, detail="Accounts role can only update agreement status")
    
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    # Booking-form snapshot is immutable — strip any attempt to overwrite it.
    updates.pop('original_booking_form_html', None)
    updates.pop('original_booking_form_snapshot_at', None)
    updates.pop('original_booking_form_pdf_b64', None)
    updates.pop('original_booking_form_pdf_recovered_from', None)
    result = await db.customers.update_one({"id": customer_id}, {"$set": updates})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    await log_activity(user['id'], user['name'], "update", "customer", customer_id, "Updated customer")
    return {"message": "Customer updated"}


@router.delete("/{customer_id}")
async def delete_customer(customer_id: str, user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    """Delete a customer (admin/manager only)."""
    db = get_database()
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Clean up related data
    await db.payment_schedules.delete_many({"customer_id": customer_id})
    await db.document_checklists.delete_one({"customer_id": customer_id})
    await db.generated_documents.delete_many({"customer_id": customer_id})
    await db.communication_logs.delete_many({"customer_id": customer_id})
    
    await log_activity(user['id'], user['name'], "delete", "customer", customer_id, "Deleted customer")
    return {"message": "Customer deleted"}



@router.post("/admin/backfill-booking-form-snapshots")
async def backfill_booking_form_snapshots(user: dict = Depends(check_role([UserRole.ADMIN]))):
    """One-time admin utility: locks in a Booking Form Preview snapshot for every
    customer that doesn't already have one, using their *current* customer record.

    NOTE: This is best-effort recovery for customers booked BEFORE the snapshot
    feature existed. Their live profile may have been edited since booking, so
    the resulting snapshot reflects the state AT BACKFILL TIME, not original
    booking time. New bookings (post-Feb-2026) snapshot automatically at submit.

    Idempotent — skips customers that already have a snapshot.
    """
    from documents.templates import generate_booking_form_preview_html
    db = get_database()
    cursor = db.customers.find(
        {"$or": [
            {"original_booking_form_html": {"$exists": False}},
            {"original_booking_form_html": None},
            {"original_booking_form_html": ""},
        ]},
        {"_id": 0},
    )
    backfilled = 0
    failed = 0
    failed_ids = []
    async for customer in cursor:
        try:
            html = generate_booking_form_preview_html(customer)
            await db.customers.update_one(
                {"id": customer['id']},
                {"$set": {
                    "original_booking_form_html": html,
                    "original_booking_form_snapshot_at": datetime.now(timezone.utc).isoformat(),
                }},
            )
            backfilled += 1
        except Exception as e:
            failed += 1
            failed_ids.append({"id": customer.get('id'), "error": str(e)[:120]})

    await log_activity(
        user['id'], user['name'], "backfill", "customer",
        "all", f"Backfilled {backfilled} booking-form snapshots ({failed} failed)"
    )
    return {
        "message": "Backfill complete",
        "backfilled": backfilled,
        "failed": failed,
        "failed_details": failed_ids,
    }


@router.get("/{customer_id}/original-booking-form.pdf")
async def get_original_booking_form_pdf(
    customer_id: str, user: dict = Depends(get_current_user)
):
    """Download the ORIGINAL booking form PDF that was emailed to the customer
    on booking day. Served as a static, non-editable file.

    Source priority:
      1. ``original_booking_form_pdf_b64`` — true binary recovered from Resend
         (perfect fidelity to what the customer received).
      2. ``original_booking_form_html`` snapshot rendered to PDF on the fly
         (frozen HTML from snapshot/backfill time, NOT live profile data).
      3. 404 if neither exists.
    """
    db = get_database()
    customer = await db.customers.find_one(
        {"id": customer_id},
        {
            "_id": 0,
            "name": 1,
            "original_booking_form_pdf_b64": 1,
            "original_booking_form_html": 1,
        },
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    name_safe = (customer.get("name") or "Customer").strip().replace(" ", "_")
    filename = f"RRL_OriginalBookingForm_{name_safe}.pdf"

    pdf_bytes: Optional[bytes] = None
    if customer.get("original_booking_form_pdf_b64"):
        try:
            pdf_bytes = base64.b64decode(customer["original_booking_form_pdf_b64"])
        except Exception:
            pdf_bytes = None

    if pdf_bytes is None and customer.get("original_booking_form_html"):
        # Render the frozen HTML snapshot to PDF as a fallback
        from weasyprint import HTML  # local import to keep startup light
        try:
            pdf_bytes = HTML(string=customer["original_booking_form_html"]).write_pdf()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF render failed: {e}")

    if not pdf_bytes:
        raise HTTPException(
            status_code=404,
            detail="No original booking form snapshot on file for this customer.",
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
