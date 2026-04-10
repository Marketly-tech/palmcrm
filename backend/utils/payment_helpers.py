"""
Shared payment helper functions used across multiple modules.
"""
import logging
from datetime import datetime, timezone

from database import get_database
from payments.models import PaymentTransaction
from utils.enums import TransactionStage

logger = logging.getLogger(__name__)

PAYMENT_STAGES = [
    {"key": "podium", "name": "On Completion of Podium Slab", "percentage": 40, "cumulative": 40},
    {"key": "2nd_floor", "name": "Upon Completion of 2nd Floor Roof Slab", "percentage": 5, "cumulative": 45},
    {"key": "6th_floor", "name": "Upon Completion of 6th Floor Roof Slab", "percentage": 5, "cumulative": 50},
    {"key": "10th_floor", "name": "Upon Completion of 10th Floor Roof Slab", "percentage": 5, "cumulative": 55},
    {"key": "14th_floor", "name": "Upon Completion of 14th Floor Roof Slab", "percentage": 5, "cumulative": 60},
    {"key": "18th_floor", "name": "Upon Completion of 18th Floor Roof Slab", "percentage": 5, "cumulative": 65},
    {"key": "22nd_floor", "name": "Upon Completion of 22nd Floor Roof Slab", "percentage": 5, "cumulative": 70},
    {"key": "top_roof", "name": "Upon Completion of Top Roof Slab", "percentage": 10, "cumulative": 80},
    {"key": "flooring", "name": "Upon Completion of Flooring of Particular Property", "percentage": 10, "cumulative": 90},
    {"key": "handover", "name": "Upon Handover / Possession / Registration", "percentage": 10, "cumulative": 100},
]


async def auto_generate_booking_transaction(customer_id: str, customer: dict, created_by: str = "system"):
    """
    Auto-generate a booking transaction if the customer has a booking_amount
    that isn't already covered by existing booking-stage transactions.
    """
    db = get_database()
    booking_amount = customer.get("booking_amount", 0) or 0
    if booking_amount <= 0:
        return

    existing_txns = await db.payment_transactions.find(
        {"customer_id": customer_id, "$or": [
            {"transaction_stage": "booking"},
            {"transaction_type": "booking"}
        ]},
        {"_id": 0, "amount": 1}
    ).to_list(1000)
    existing_booking_sum = sum(t.get("amount", 0) or 0 for t in existing_txns)

    if existing_booking_sum >= booking_amount:
        return

    shortfall = booking_amount - existing_booking_sum
    booking_date = customer.get("booking_date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    txn_bank = customer.get("transaction_bank", "") or ""
    txn_ref = customer.get("transaction_details", "") or ""
    unit = customer.get("unit_number", "") or ""
    name = customer.get("name", "") or ""

    new_txn = PaymentTransaction(
        customer_id=customer_id,
        transaction_stage=TransactionStage.BOOKING,
        transaction_date=booking_date,
        bank_name=txn_bank,
        transaction_number=txn_ref,
        amount=shortfall,
        notes=f"Auto-generated from booking amount. Flat: {unit}, Client: {name}".strip(),
    )
    await db.payment_transactions.insert_one(new_txn.model_dump())

    all_txns = await db.payment_transactions.find(
        {"customer_id": customer_id}, {"_id": 0, "amount": 1}
    ).to_list(1000)
    total_received = sum(t.get("amount", 0) or 0 for t in all_txns)
    total_price = customer.get("total_price", 0) or 0
    balance_amount = total_price - total_received

    await db.customers.update_one(
        {"id": customer_id},
        {"$set": {
            "total_received": total_received,
            "balance_amount": balance_amount,
            "payment_received_percentage": round((total_received / total_price) * 100, 2) if total_price > 0 else 0,
            "payment_pending_percentage": round((balance_amount / total_price) * 100, 2) if total_price > 0 else 100
        }}
    )
    logger.info(f"Auto-generated booking transaction of {shortfall} for customer {customer_id} ({name})")
