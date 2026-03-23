"""
Payment routes for RRL CRM.
Handles payment schedules, transactions, and price calculations.
"""
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends
import uuid

from database import get_database
from auth import get_current_user, log_activity
from payments.models import (
    PaymentScheduleCreate, PaymentScheduleItem, PaymentTransaction, PaymentTransactionCreate,
    PriceCalculation, PriceResult, DisbursementCalculation, DisbursementResult, PaymentTrackingResult,
    DEFAULT_PAYMENT_SCHEDULE
)

# Create routers
schedule_router = APIRouter(prefix="/payments", tags=["Payment Schedules"])
transactions_router = APIRouter(prefix="/transactions", tags=["Transactions"])
calculator_router = APIRouter(prefix="/calculator", tags=["Price Calculator"])


# ==================== PAYMENT SCHEDULE ROUTES ====================
@schedule_router.post("/schedule")
async def create_payment_schedule(data: PaymentScheduleCreate, user: dict = Depends(get_current_user)):
    """Create or update payment schedule."""
    db = get_database()
    existing = await db.payment_schedules.find_one({"customer_id": data.customer_id}, {"_id": 0})
    
    schedule_doc = {
        "id": existing['id'] if existing else str(uuid.uuid4()),
        "customer_id": data.customer_id,
        "items": [item.model_dump() for item in data.items],
        "created_at": existing['created_at'] if existing else datetime.now(timezone.utc).isoformat()
    }
    
    if existing:
        await db.payment_schedules.update_one({"customer_id": data.customer_id}, {"$set": schedule_doc})
    else:
        await db.payment_schedules.insert_one(schedule_doc)
    
    await log_activity(user['id'], user['name'], "update", "payment_schedule", data.customer_id, "Updated payment schedule")
    return {"message": "Payment schedule saved", "schedule": schedule_doc}


@schedule_router.get("/schedule/{customer_id}")
async def get_payment_schedule(customer_id: str, user: dict = Depends(get_current_user)):
    """Get payment schedule for a customer."""
    db = get_database()
    schedule = await db.payment_schedules.find_one({"customer_id": customer_id}, {"_id": 0})
    if not schedule:
        return {"customer_id": customer_id, "items": []}
    return schedule


@schedule_router.put("/item/{customer_id}/{item_id}")
async def update_payment_item(customer_id: str, item_id: str, updates: Dict[str, Any], user: dict = Depends(get_current_user)):
    """Update a payment schedule item."""
    db = get_database()
    schedule = await db.payment_schedules.find_one({"customer_id": customer_id}, {"_id": 0})
    if not schedule:
        raise HTTPException(status_code=404, detail="Payment schedule not found")
    
    for item in schedule['items']:
        if item['id'] == item_id:
            item.update(updates)
            break
    
    await db.payment_schedules.update_one({"customer_id": customer_id}, {"$set": {"items": schedule['items']}})
    
    # Auto-calculate total_received based on paid items
    total_received = 0
    for item in schedule['items']:
        if item.get('payment_status') == 'paid':
            total_received += item.get('amount', 0)
        elif item.get('payment_status') == 'partial':
            total_received += item.get('amount', 0) * 0.5
    
    # Get customer's total price to calculate percentages
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0, "total_price": 1})
    total_price = customer.get('total_price', 0) if customer else 0
    
    # Calculate payment percentages
    payment_received_percentage = round((total_received / total_price * 100), 2) if total_price > 0 else 0
    payment_pending_percentage = round(100 - payment_received_percentage, 2)
    balance_amount = round(total_price - total_received, 2)
    
    # Update customer's payment tracking fields
    await db.customers.update_one(
        {"id": customer_id},
        {"$set": {
            "total_received": round(total_received, 2),
            "balance_amount": balance_amount,
            "payment_received_percentage": payment_received_percentage,
            "payment_pending_percentage": payment_pending_percentage,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    await log_activity(user['id'], user['name'], "update", "payment_item", item_id, f"Updated payment status - Total Received: {total_received}")
    
    return {
        "message": "Payment item updated",
        "total_received": round(total_received, 2),
        "balance_amount": balance_amount,
        "payment_received_percentage": payment_received_percentage,
        "payment_pending_percentage": payment_pending_percentage
    }


@schedule_router.get("/overview")
async def get_payments_overview(user: dict = Depends(get_current_user)):
    """Get payments overview (pending, overdue, upcoming)."""
    db = get_database()
    today = datetime.now(timezone.utc).date()
    week_end = today + timedelta(days=7)
    
    schedules = await db.payment_schedules.find({}, {"_id": 0}).to_list(1000)
    
    # Fetch all relevant customers in one query
    customer_ids = list(set(s.get('customer_id') for s in schedules if s.get('customer_id')))
    customers_list = await db.customers.find(
        {"id": {"$in": customer_ids}}, 
        {"_id": 0, "id": 1, "name": 1, "customer_id": 1, "unit_number": 1}
    ).to_list(1000)
    customers_dict = {c['id']: c for c in customers_list}
    
    pending = []
    overdue = []
    upcoming = []
    
    for schedule in schedules:
        customer = customers_dict.get(schedule.get('customer_id'))
        for item in schedule.get('items', []):
            if item['payment_status'] == 'paid':
                continue
            
            try:
                due_date = datetime.strptime(item['due_date'], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue
            
            item_data = {**item, "customer_name": customer.get('name', 'N/A') if customer else 'N/A', 
                        "customer_ref": customer.get('customer_id', '') if customer else '',
                        "unit_number": customer.get('unit_number', '') if customer else ''}
            
            if due_date < today:
                overdue.append(item_data)
            elif due_date <= week_end:
                upcoming.append(item_data)
            else:
                pending.append(item_data)
    
    return {"pending": pending, "overdue": overdue, "upcoming": upcoming}


# ==================== PAYMENT TRANSACTIONS ====================
@transactions_router.get("/{customer_id}")
async def get_transactions(customer_id: str, user: dict = Depends(get_current_user)):
    """Get all transactions for a customer."""
    db = get_database()
    transactions = await db.payment_transactions.find(
        {"customer_id": customer_id}, {"_id": 0}
    ).sort("transaction_date", -1).to_list(1000)
    return transactions


@transactions_router.post("/{customer_id}")
async def create_transaction(customer_id: str, transaction: PaymentTransactionCreate, user: dict = Depends(get_current_user)):
    """Create a new transaction."""
    db = get_database()
    # Verify customer exists
    customer = await db.customers.find_one({"$or": [{"id": customer_id}, {"customer_id": customer_id}]})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    new_transaction = PaymentTransaction(
        customer_id=customer_id,
        transaction_stage=transaction.transaction_stage,
        transaction_date=transaction.transaction_date,
        bank_name=transaction.bank_name,
        transaction_number=transaction.transaction_number,
        amount=transaction.amount,
        notes=transaction.notes
    )
    
    await db.payment_transactions.insert_one(new_transaction.model_dump())
    
    # Update customer's total_received and balance_amount
    all_transactions = await db.payment_transactions.find({"customer_id": customer_id}, {"_id": 0, "amount": 1}).to_list(1000)
    total_received = sum(t.get('amount', 0) or 0 for t in all_transactions)
    total_price = customer.get('total_price', 0) or 0
    balance_amount = total_price - total_received
    
    await db.customers.update_one(
        {"$or": [{"id": customer_id}, {"customer_id": customer_id}]},
        {"$set": {
            "total_received": total_received,
            "balance_amount": balance_amount,
            "payment_received_percentage": round((total_received / total_price) * 100, 2) if total_price > 0 else 0,
            "payment_pending_percentage": round((balance_amount / total_price) * 100, 2) if total_price > 0 else 100
        }}
    )
    
    await log_activity(user['id'], user['name'], "create", "transaction", new_transaction.id, f"Created transaction for customer {customer_id}")
    
    return {"message": "Transaction created", "transaction": new_transaction.model_dump()}


@transactions_router.put("/{customer_id}/{transaction_id}")
async def update_transaction(customer_id: str, transaction_id: str, transaction: PaymentTransactionCreate, user: dict = Depends(get_current_user)):
    """Update an existing transaction."""
    db = get_database()
    existing = await db.payment_transactions.find_one({"id": transaction_id, "customer_id": customer_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    update_data = {
        "transaction_stage": transaction.transaction_stage.value if hasattr(transaction.transaction_stage, 'value') else transaction.transaction_stage,
        "transaction_date": transaction.transaction_date,
        "bank_name": transaction.bank_name,
        "transaction_number": transaction.transaction_number,
        "amount": transaction.amount,
        "notes": transaction.notes,
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.payment_transactions.update_one(
        {"id": transaction_id},
        {"$set": update_data}
    )
    
    # Update customer's total_received and balance_amount
    customer = await db.customers.find_one({"$or": [{"id": customer_id}, {"customer_id": customer_id}]})
    if customer:
        all_transactions = await db.payment_transactions.find({"customer_id": customer_id}, {"_id": 0, "amount": 1}).to_list(1000)
        total_received = sum(t.get('amount', 0) or 0 for t in all_transactions)
        total_price = customer.get('total_price', 0) or 0
        balance_amount = total_price - total_received
        
        await db.customers.update_one(
            {"$or": [{"id": customer_id}, {"customer_id": customer_id}]},
            {"$set": {
                "total_received": total_received,
                "balance_amount": balance_amount,
                "payment_received_percentage": round((total_received / total_price) * 100, 2) if total_price > 0 else 0,
                "payment_pending_percentage": round((balance_amount / total_price) * 100, 2) if total_price > 0 else 100
            }}
        )
    
    await log_activity(user['id'], user['name'], "update", "transaction", transaction_id, f"Updated transaction for customer {customer_id}")
    
    return {"message": "Transaction updated"}


@transactions_router.delete("/{customer_id}/{transaction_id}")
async def delete_transaction(customer_id: str, transaction_id: str, user: dict = Depends(get_current_user)):
    """Delete a transaction - restricted for accounts role."""
    db = get_database()
    # Accounts role cannot delete transactions
    if user['role'] == 'accounts':
        raise HTTPException(status_code=403, detail="Accounts role cannot delete transactions")
    
    result = await db.payment_transactions.delete_one({"id": transaction_id, "customer_id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update customer's total_received and balance_amount
    customer = await db.customers.find_one({"$or": [{"id": customer_id}, {"customer_id": customer_id}]})
    if customer:
        all_transactions = await db.payment_transactions.find({"customer_id": customer_id}, {"_id": 0, "amount": 1}).to_list(1000)
        total_received = sum(t.get('amount', 0) or 0 for t in all_transactions)
        total_price = customer.get('total_price', 0) or 0
        balance_amount = total_price - total_received
        
        await db.customers.update_one(
            {"$or": [{"id": customer_id}, {"customer_id": customer_id}]},
            {"$set": {
                "total_received": total_received,
                "balance_amount": balance_amount,
                "payment_received_percentage": round((total_received / total_price) * 100, 2) if total_price > 0 else 0,
                "payment_pending_percentage": round((balance_amount / total_price) * 100, 2) if total_price > 0 else 100
            }}
        )
    
    await log_activity(user['id'], user['name'], "delete", "transaction", transaction_id, f"Deleted transaction for customer {customer_id}")
    
    return {"message": "Transaction deleted"}


# ==================== PRICE CALCULATOR ====================
@calculator_router.post("/price", response_model=PriceResult)
async def calculate_price(data: PriceCalculation):
    """
    Calculate total flat value with all charges.
    Formula: (Rate/sqft × Saleable Area) + Club House + Additional Charges + Labour Cess + GST
    """
    # Base price = Rate × Saleable Area
    base_price = data.rate_per_sqft * data.saleable_area
    
    # Club house charges (editable, default Rs. 2,00,000)
    club_house = data.club_house_charges if data.include_club_house else 0
    
    # Additional manual charges
    additional_charges = data.additional_charges or 0
    
    # Subtotal before taxes
    subtotal = base_price + club_house + additional_charges
    
    # Labour cess (0.70% of subtotal)
    labour_cess = subtotal * (data.labour_cess_percentage / 100)
    
    # GST (5% of subtotal)
    gst_amount = subtotal * (data.gst_percentage / 100)
    
    # Total flat value
    total_flat_value = subtotal + labour_cess + gst_amount
    
    # UDS calculation
    uds = data.saleable_area * 0.495046
    
    return PriceResult(
        unit_number=data.unit_number,
        unit_type=data.unit_type,
        floor_number=data.floor_number,
        saleable_area=data.saleable_area,
        rate_per_sqft=data.rate_per_sqft,
        base_price=round(base_price, 2),
        club_house_charges=round(club_house, 2),
        additional_charges=round(additional_charges, 2),
        subtotal_before_taxes=round(subtotal, 2),
        labour_cess=round(labour_cess, 2),
        gst_amount=round(gst_amount, 2),
        total_flat_value=round(total_flat_value, 2),
        uds=round(uds, 2)
    )


@calculator_router.post("/disbursement", response_model=DisbursementResult)
async def calculate_disbursement(data: DisbursementCalculation):
    """
    Calculate disbursement amount.
    Formula: Total Flat Value × Disbursement Percentage
    """
    disbursement_amount = data.total_flat_value * (data.disbursement_percentage / 100)
    
    return DisbursementResult(
        total_flat_value=round(data.total_flat_value, 2),
        disbursement_percentage=data.disbursement_percentage,
        disbursement_amount=round(disbursement_amount, 2)
    )


@calculator_router.post("/payment-tracking", response_model=PaymentTrackingResult)
async def calculate_payment_tracking(total_flat_value: float, total_received: float):
    """
    Calculate payment tracking metrics.
    - Balance = Total - Received
    - Received % = (Received / Total) × 100
    - Pending % = 100 - Received %
    """
    balance = total_flat_value - total_received
    received_percentage = (total_received / total_flat_value * 100) if total_flat_value > 0 else 0
    pending_percentage = 100 - received_percentage
    
    return PaymentTrackingResult(
        total_flat_value=round(total_flat_value, 2),
        total_received=round(total_received, 2),
        balance_amount=round(balance, 2),
        payment_received_percentage=round(received_percentage, 2),
        payment_pending_percentage=round(pending_percentage, 2)
    )


@calculator_router.get("/payment-schedule-template")
async def get_payment_schedule_template(total_amount: float = 0):
    """Get the default payment schedule template with calculated amounts."""
    schedule = []
    cumulative = 0
    for item in DEFAULT_PAYMENT_SCHEDULE:
        amount = total_amount * (item["percentage"] / 100) if total_amount > 0 else 0
        cumulative += amount
        schedule.append({
            **item,
            "amount": round(amount, 2),
            "cumulative": round(cumulative, 2)
        })
    return schedule


@calculator_router.post("/generate-schedule/{customer_id}")
async def generate_payment_schedule_for_customer(customer_id: str, user: dict = Depends(get_current_user)):
    """Auto-generate payment schedule based on customer's total price."""
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    total_amount = customer.get("total_price", 0)
    if total_amount <= 0:
        raise HTTPException(status_code=400, detail="Customer has no total price set")
    
    items = []
    cumulative = 0
    for item in DEFAULT_PAYMENT_SCHEDULE:
        amount = total_amount * (item["percentage"] / 100)
        cumulative += amount
        items.append({
            "id": str(uuid.uuid4()),
            "installment_name": item["installment_name"],
            "milestone": item["milestone"],
            "description": item.get("description", ""),
            "percentage": item["percentage"],
            "amount": round(amount, 2),
            "cumulative": round(cumulative, 2),
            "due_date": "",
            "payment_status": "pending",
            "payment_date": None
        })
    
    schedule_doc = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "items": items,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Upsert the schedule
    await db.payment_schedules.update_one(
        {"customer_id": customer_id},
        {"$set": schedule_doc},
        upsert=True
    )
    
    await log_activity(user['id'], user['name'], "generate", "payment_schedule", customer_id, "Auto-generated payment schedule")
    
    return {"message": "Payment schedule generated", "schedule": schedule_doc}
