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
    generate_noc_bajaj_html,
    generate_demand_letter_html,
    generate_payment_receipt_html,
    get_default_template,
)
from documents.templates.common import (
    build_agreement_date_text,
    build_applicant_details_block,
    build_payment_schedule_rows_html,
    build_transaction_rows_html,
    format_customer_names,
    calculate_age,
    get_salutation,
    get_logo_img_tag,
    COMPANY_NAME,
)
from utils import number_to_indian_words, get_ordinal_suffix


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
    DocumentType.NOC_BAJAJ: generate_noc_bajaj_html,
}


async def _render_noc(db, customer: dict, doc_type: DocumentType) -> str:
    transactions = await db.payment_transactions.find(
        {"customer_id": customer.get('id')}, {"_id": 0}
    ).sort("transaction_date", 1).to_list(1000)
    generator = _NOC_GENERATORS[doc_type]
    # TATA and Bajaj NOCs don't include the received-amount line; call without transactions
    if doc_type in (DocumentType.NOC_TATA, DocumentType.NOC_BAJAJ):
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


async def _build_placeholders(
    db, customer: dict, custom_fields: Dict[str, Any]
) -> Dict[str, str]:
    """Build the {placeholder} → value map for fallback/templated documents.

    Async because it fetches transactions and the payment schedule so that
    saved master templates can resolve row-heavy placeholders like
    ``{payment_schedule_rows}``, ``{transaction_rows}``, and
    ``{total_received_words}`` at render time.
    """
    total_price = customer.get('total_price', 0) or 0
    booking_amount = customer.get('booking_amount', 0) or 0
    total_price_formatted = (
        format_indian_currency(total_price) if total_price else "0"
    )
    booking_amount_formatted = (
        format_indian_currency(booking_amount) if booking_amount else "0"
    )
    uds = customer.get('uds', 0)
    if not uds and customer.get('saleable_area'):
        uds = round(customer.get('saleable_area', 0) * 0.495046, 2)

    # Fetch transactions + schedule so row-heavy placeholders can be resolved.
    cust_id = customer.get('id')
    transactions = []
    schedule_items: list = []
    if cust_id:
        transactions = await db.payment_transactions.find(
            {"customer_id": cust_id}, {"_id": 0}
        ).sort("transaction_date", 1).to_list(1000)
        schedule = await db.payment_schedules.find_one(
            {"customer_id": cust_id}, {"_id": 0}
        )
        schedule_items = (schedule or {}).get('items', []) if schedule else []

    total_received = sum(float(t.get('amount', 0) or 0) for t in transactions)
    total_received_formatted = (
        format_indian_currency(total_received) if total_received else "0"
    )

    # Sales-Agreement-style derived fields (kept in sync with sales_agreement_html.py
    # so a master template saved from a Sales Agreement re-renders correctly).
    base_price = customer.get('base_price', 0) or 0
    club_house = customer.get('club_house_charges', 200000) or 200000
    parking_charges = customer.get('additional_parking_charges', 0) or 0
    labour_cess = customer.get('labour_cess', 0) or 0
    gst_amount = customer.get('gst_amount', 0) or 0
    additional_parking = customer.get('additional_parking', 0) or 0
    additional_parking_text = (
        f" + {additional_parking} additional parking space(s)"
        if additional_parking else ""
    )
    floor_val = customer.get('floor', 0) or 0
    try:
        floor_int = int(floor_val)
    except (TypeError, ValueError):
        floor_int = 0
    floor_ordinal = (
        f"{floor_int}{get_ordinal_suffix(floor_int)}" if floor_int > 0 else "Ground"
    )

    placeholders = {
        "{customer_name}": customer.get('name', ''),
        "{customer_names}": format_customer_names(customer),
        "{age}": calculate_age(customer.get('date_of_birth')),
        "{salutation}": get_salutation(customer.get('gender')),
        "{customer_id}": customer.get('customer_id', ''),
        "{unit_number}": customer.get('unit_number', ''),
        "{tower}": customer.get('tower', ''),
        "{project}": customer.get('project', ''),
        "{total_price}": str(total_price),
        "{total_price_formatted}": total_price_formatted,
        "{total_price_words}": number_to_indian_words(total_price),
        "{saleable_area}": str(customer.get('saleable_area', 0)),
        "{uds}": str(uds),
        "{booking_amount}": str(booking_amount),
        "{booking_amount_formatted}": booking_amount_formatted,
        "{booking_amount_words}": number_to_indian_words(booking_amount),
        "{booking_date}": customer.get('booking_date', ''),
        "{possession_date}": customer.get('possession_date', '30-09-2030'),
        "{date}": datetime.now().strftime("%d-%m-%Y"),
        # Main-applicant scalars
        "{father_name}": customer.get('father_name', ''),
        "{pan_number}": customer.get('pan_number', ''),
        "{aadhaar_number}": (
            customer.get('aadhar_number', '') or customer.get('aadhaar_number', '')
        ),
        "{phone}": customer.get('phone', ''),
        "{email}": customer.get('email', ''),
        "{address}": customer.get('address', ''),
        # Co-applicant scalars — required so signature blocks and paragraphs
        # scrubbed by save-as-master resolve correctly for the new customer.
        "{co_applicant_name}": customer.get('co_applicant_name', ''),
        "{co_applicant_father_name}": customer.get('co_applicant_father_name', ''),
        "{co_applicant_aadhar}": customer.get('co_applicant_aadhar', ''),
        "{co_applicant_pan}": customer.get('co_applicant_pan', ''),
        "{co_applicant_email}": customer.get('co_applicant_email', ''),
        "{co_applicant_phone}": customer.get('co_applicant_phone', ''),
        "{co_applicant_address}": customer.get('co_applicant_address', ''),
        # Property & pricing scalars
        "{bhk_type}": customer.get('bhk_type', ''),
        "{floor}": str(customer.get('floor', '')),
        "{floor_ordinal}": floor_ordinal,
        "{additional_parking}": str(additional_parking),
        "{additional_parking_text}": additional_parking_text,
        "{rate_per_sqft}": str(customer.get('rate_per_sqft', 0)),
        "{base_price}": str(base_price),
        "{base_price_formatted}": format_indian_currency(base_price) if base_price else "0",
        "{gst_amount}": str(gst_amount),
        "{gst_formatted}": format_indian_currency(gst_amount) if gst_amount else "0",
        "{labour_cess}": str(labour_cess),
        "{labour_cess_formatted}": format_indian_currency(labour_cess) if labour_cess else "0",
        "{club_house_charges}": str(club_house),
        "{club_house_formatted}": format_indian_currency(club_house) if club_house else "0",
        "{parking_charges_formatted}": (
            format_indian_currency(parking_charges) if parking_charges else "0"
        ),
        "{interest_amount}": str(customer.get('interest_amount', 0)),
        # Branding
        "{logo_img}": get_logo_img_tag(120),
        "{company_name}": COMPANY_NAME,
        # Narrative / row-heavy placeholders
        "{total_received}": str(total_received),
        "{total_received_formatted}": total_received_formatted,
        "{total_received_words}": number_to_indian_words(int(total_received)),
        "{agreement_date_text}": build_agreement_date_text(),
        "{applicant_details_block}": build_applicant_details_block(customer),
        "{payment_schedule_rows}": build_payment_schedule_rows_html(customer, schedule_items),
        "{transaction_rows}": build_transaction_rows_html(customer, transactions),
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
    for placeholder, value in (await _build_placeholders(db, customer, custom_fields)).items():
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
        for placeholder, value in (await _build_placeholders(db, customer, custom_fields or {})).items():
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
