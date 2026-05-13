"""
Customer routes for RRL CRM.
Handles customer CRUD operations.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import re
from fastapi import APIRouter, HTTPException, Depends
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
    """Get canonical bank names for the customer filter dropdown.

    Returns each bank exactly once even when the DB has aliases
    (e.g. "HDFC" + "HDFC Bank" both collapse to "HDFC Bank").
    """
    db = get_database()
    raw_banks = await db.customers.distinct("finance_bank")
    canonical_set = set()
    for raw in raw_banks:
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
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"customer_id": {"$regex": search, "$options": "i"}},
            {"unit_number": {"$regex": search, "$options": "i"}}
        ]
    if project:
        query["project"] = project
    if agreement_status:
        query["agreement_status"] = agreement_status
    if finance_bank:
        # Match any DB alias of the chosen canonical bank, case-insensitive.
        # e.g. user picks "HDFC Bank" → also matches rows with "HDFC", "HDFC BANK".
        canonical = to_canonical(finance_bank) or finance_bank
        alias_patterns = [re.escape(a) for a in aliases_for(canonical)]
        query["finance_bank"] = {
            "$regex": f"^({'|'.join(alias_patterns)})$",
            "$options": "i",
        }
    if agreement_filter == "pending_agreement":
        query["agreement_status"] = {"$in": ["draft", "sent"]}
    elif agreement_filter == "agreement_due":
        query["agreement_status"] = "sent"
    return query


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
