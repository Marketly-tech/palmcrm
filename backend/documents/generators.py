"""
Document content generators.
Dispatches to the correct HTML template builder based on DocumentType.
Extracted from documents/routes.py to keep route handlers thin and reduce
cyclomatic complexity.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import HTTPException

from utils.enums import DocumentType
from utils import format_indian_currency
from utils.payment_helpers import PAYMENT_STAGES
from payments.models import DEFAULT_PAYMENT_SCHEDULE

from documents.templates import (
    generate_sales_agreement_html,
    generate_price_breakup_html,
    generate_cost_breakup_html,
    generate_allotment_letter_html,
    generate_payment_schedule_html,
    generate_noc_hdfc_html,
    generate_noc_bob_html,
    generate_noc_tata_html,
    generate_demand_letter_html,
    generate_payment_receipt_html,
    get_default_template,
)


# Simple synchronous generators (no DB lookups beyond the customer doc)
_SIMPLE_GENERATORS = {
    DocumentType.PRICE_BREAKUP: generate_price_breakup_html,
    DocumentType.COST_BREAKUP: generate_cost_breakup_html,
    DocumentType.ALLOTMENT_LETTER: generate_allotment_letter_html,
}


# NOC generators that need transactions to compute "received excl TDS"
_NOC_GENERATORS = {
    DocumentType.NOC_HDFC: generate_noc_hdfc_html,
    DocumentType.NOC_BOB: generate_noc_bob_html,
    DocumentType.NOC_TATA: generate_noc_tata_html,
}


async def _render_noc(db, customer: dict, doc_type: DocumentType) -> str:
    transactions = await db.payment_transactions.find(
        {"customer_id": customer.get('id')}, {"_id": 0}
    ).sort("transaction_date", 1).to_list(1000)
    generator = _NOC_GENERATORS[doc_type]
    # TATA NOC doesn't include the received-amount line; call without transactions
    if doc_type == DocumentType.NOC_TATA:
        return generator(customer)
    return generator(customer, transactions)


async def _render_sales_agreement(db, customer: dict) -> str:
    schedule = await db.payment_schedules.find_one(
        {"customer_id": customer.get('id')}, {"_id": 0}
    )
    schedule_items = schedule.get('items', []) if schedule else []
    transactions = await db.payment_transactions.find(
        {"customer_id": customer.get('id')}, {"_id": 0}
    ).sort("transaction_date", 1).to_list(1000)
    return generate_sales_agreement_html(customer, schedule_items, transactions)


async def _auto_generate_schedule(db, customer: dict) -> list:
    """Build a default payment schedule for the customer from the template and
    persist it. Returns the items list."""
    total_amount = customer.get("total_price", 0) or 0
    if total_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot generate payment schedule: customer has no total price set. "
                "Please complete the price calculator first."
            ),
        )
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
            "payment_date": None,
        })
    schedule_doc = {
        "id": str(uuid.uuid4()),
        "customer_id": customer.get("id"),
        "items": items,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.payment_schedules.update_one(
        {"customer_id": customer.get("id")},
        {"$set": schedule_doc},
        upsert=True,
    )
    return items


async def _render_payment_schedule(db, customer: dict) -> str:
    schedule = await db.payment_schedules.find_one(
        {"customer_id": customer.get('id')}, {"_id": 0}
    )
    schedule_items = schedule.get('items', []) if schedule else []
    if not schedule_items:
        # Auto-generate from the default template so document generation is a
        # one-click action for users who haven't manually built a schedule yet.
        schedule_items = await _auto_generate_schedule(db, customer)
    return generate_payment_schedule_html(customer, schedule_items)


async def _render_demand_letter(db, customer: dict) -> str:
    transactions = await db.payment_transactions.find(
        {"customer_id": customer.get('id')}, {"_id": 0}
    ).sort("transaction_date", 1).to_list(1000)
    stage_settings = await db.settings.find_one({"type": "payment_stage"}, {"_id": 0})
    stage_info = {}
    if stage_settings and stage_settings.get("current_stage"):
        stage_key = stage_settings.get("current_stage")
        stage_info = next((s for s in PAYMENT_STAGES if s["key"] == stage_key), {})
    return generate_demand_letter_html(customer, transactions, stage_info)


def _build_placeholders(customer: dict, custom_fields: Dict[str, Any]) -> Dict[str, str]:
    """Build the {placeholder} → value map for fallback/templated documents."""
    total_price = customer.get('total_price', 0)
    total_price_formatted = (
        format_indian_currency(total_price, decimals=False) if total_price else "0"
    )
    uds = customer.get('uds', 0)
    if not uds and customer.get('saleable_area'):
        uds = round(customer.get('saleable_area', 0) * 0.495046, 2)

    placeholders = {
        "{customer_name}": customer.get('name', ''),
        "{customer_id}": customer.get('customer_id', ''),
        "{unit_number}": customer.get('unit_number', ''),
        "{tower}": customer.get('tower', ''),
        "{project}": customer.get('project', ''),
        "{total_price}": str(total_price),
        "{total_price_formatted}": total_price_formatted,
        "{saleable_area}": str(customer.get('saleable_area', 0)),
        "{uds}": str(uds),
        "{booking_amount}": str(customer.get('booking_amount', 0)),
        "{booking_date}": customer.get('booking_date', ''),
        "{date}": datetime.now().strftime("%d-%m-%Y"),
        "{father_name}": customer.get('father_name', ''),
        "{pan_number}": customer.get('pan_number', ''),
        "{phone}": customer.get('phone', ''),
        "{email}": customer.get('email', ''),
        "{address}": customer.get('address', ''),
        "{bhk_type}": customer.get('bhk_type', ''),
        "{floor}": str(customer.get('floor', '')),
        "{rate_per_sqft}": str(customer.get('rate_per_sqft', 0)),
        "{base_price}": str(customer.get('base_price', 0)),
        "{gst_amount}": str(customer.get('gst_amount', 0)),
        "{labour_cess}": str(customer.get('labour_cess', 0)),
        "{club_house_charges}": str(customer.get('club_house_charges', 0)),
    }
    for key, value in (custom_fields or {}).items():
        placeholders[f"{{{key}}}"] = value
    return placeholders


async def _render_from_template(
    db, customer: dict, doc_type: DocumentType, custom_fields: Dict[str, Any]
) -> str:
    template = await db.document_templates.find_one(
        {"doc_type": doc_type.value}, {"_id": 0}
    )
    if not template:
        template = {"content": get_default_template(doc_type)}
    content = template['content']
    for placeholder, value in _build_placeholders(customer, custom_fields).items():
        content = content.replace(placeholder, str(value))
    return content


async def _render_payment_receipt(db, customer: dict, custom_fields: Dict[str, Any]) -> str:
    transaction_id = (custom_fields or {}).get("transaction_id")
    if not transaction_id:
        raise HTTPException(
            status_code=400,
            detail="transaction_id is required in custom_fields for payment_receipt"
        )
    transaction = await db.payment_transactions.find_one(
        {"id": transaction_id, "customer_id": customer.get("id")}, {"_id": 0}
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return generate_payment_receipt_html(customer, transaction)


async def render_document_content(
    db, customer: dict, doc_type: DocumentType, custom_fields: Dict[str, Any] = None
) -> str:
    """Return the rendered HTML content for the requested document type.

    Admin precedence: if a DocumentTemplate with matching doc_type and
    `is_active=True` exists in the database, use it (with placeholder
    substitution) instead of the built-in file-based generator. This is the
    backend half of the Admin Template Editor feature.
    """
    override = await db.document_templates.find_one(
        {"doc_type": doc_type.value, "is_active": True}, {"_id": 0}
    )
    if override and override.get('content'):
        content = override['content']
        for placeholder, value in _build_placeholders(customer, custom_fields or {}).items():
            content = content.replace(placeholder, str(value))
        return content

    if doc_type == DocumentType.SALES_AGREEMENT:
        return await _render_sales_agreement(db, customer)
    if doc_type == DocumentType.PAYMENT_SCHEDULE:
        return await _render_payment_schedule(db, customer)
    if doc_type == DocumentType.DEMAND_LETTER:
        return await _render_demand_letter(db, customer)
    if doc_type == DocumentType.PAYMENT_RECEIPT:
        return await _render_payment_receipt(db, customer, custom_fields or {})
    if doc_type in _NOC_GENERATORS:
        return await _render_noc(db, customer, doc_type)
    if doc_type in _SIMPLE_GENERATORS:
        return _SIMPLE_GENERATORS[doc_type](customer)
    return await _render_from_template(db, customer, doc_type, custom_fields or {})
