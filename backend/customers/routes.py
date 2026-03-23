"""
Customer routes for RRL CRM.
Handles customer CRUD operations.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends
from pymongo import ReturnDocument

from database import get_database
from utils.enums import UserRole
from auth import get_current_user, log_activity, check_role
from customers.models import Customer, CustomerCreate, DocumentChecklist

# Create router
router = APIRouter(prefix="/customers", tags=["Customers"])


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


@router.get("")
async def get_customers(
    search: Optional[str] = None,
    project: Optional[str] = None,
    agreement_status: Optional[str] = None,
    agreement_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """Get customers with filters."""
    db = get_database()
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
    
    # Apply agreement filters
    if agreement_filter:
        today = datetime.now(timezone.utc).date()
        
        if agreement_filter == "upcoming_due":
            pass  # Will filter in Python
        elif agreement_filter == "pending_agreement":
            query["agreement_status"] = {"$in": ["draft", "sent"]}
        elif agreement_filter == "agreement_due":
            query["agreement_status"] = "sent"
    
    customers = await db.customers.find(query, {"_id": 0}).skip(skip).limit(limit * 2 if agreement_filter == "upcoming_due" else limit).to_list(limit * 2 if agreement_filter == "upcoming_due" else limit)
    
    # Post-filter for upcoming_due
    if agreement_filter == "upcoming_due":
        today = datetime.now(timezone.utc).date()
        filtered_customers = []
        
        for customer in customers:
            booking_date_str = customer.get('booking_date')
            if not booking_date_str:
                continue
            try:
                if isinstance(booking_date_str, str):
                    booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
                else:
                    booking_date = booking_date_str
                
                # Due date is 10 days from booking
                due_date = booking_date + timedelta(days=10)
                days_until_due = (due_date - today).days
                
                # Include if due within next 5 days (including recently overdue up to 3 days)
                if -3 <= days_until_due <= 5:
                    customer['_due_date'] = due_date.isoformat()
                    customer['_days_until_due'] = days_until_due
                    filtered_customers.append(customer)
            except Exception:
                continue
        
        # Sort by due date (closest first)
        filtered_customers.sort(key=lambda x: x.get('_days_until_due', 999))
        customers = filtered_customers[:limit]
    
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
