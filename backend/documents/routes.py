"""
Document routes for RRL CRM.
Handles document generation, templates, PDF export, upload/download, and checklist.
"""
from typing import Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import Response
import uuid
import base64
import logging

from weasyprint import HTML

from database import get_database
from utils.enums import UserRole, DocumentType, AgreementStatus
from auth import get_current_user, log_activity, check_role
from documents.models import (
    DocumentTemplate, DocumentGenerate, GeneratedDocument
)
from customers.models import DocumentChecklist

from documents.templates import (
    generate_price_breakup_html, generate_cost_breakup_html,
    generate_payment_schedule_html,
    generate_transactions_export_html,
)
from documents.templates.common import (
    build_agreement_date_text,
    build_applicant_details_block,
    build_payment_schedule_rows_html,
    build_transaction_rows_html,
)
from documents.generators import render_document_content
from utils import format_indian_currency, number_to_indian_words

logger = logging.getLogger(__name__)


async def _scrub_customer_values_to_placeholders(
    db, content: str, customer: dict
) -> str:
    """Reverse the placeholder substitution: replace literal customer-specific
    values in the HTML back with their {placeholder} tokens, so the saved
    master template renders correctly for ANY future customer.

    Only the document *format* (layout, styling, static legal text) is preserved.
    Customer-specific fields (name, unit, address, prices, dates, word-form
    amounts, applicant details, and the payment-schedule / transaction row
    tables) become placeholders again.
    """
    # Field name -> placeholder token. Order matters: long/specific first so
    # we don't partially-match a short value that's a prefix of a longer one.
    field_to_placeholder = [
        # Full names first (longest, most specific)
        ("co_applicant_address", "{co_applicant_address}"),
        ("co_applicant_father_name", "{co_applicant_father_name}"),
        ("co_applicant_aadhar", "{co_applicant_aadhar}"),
        ("co_applicant_email", "{co_applicant_email}"),
        ("co_applicant_phone", "{co_applicant_phone}"),
        ("co_applicant_name", "{co_applicant_name}"),
        ("co_applicant_pan", "{co_applicant_pan}"),
        # Applicant
        ("address", "{address}"),
        ("father_name", "{father_name}"),
        ("aadhar_number", "{aadhar_number}"),
        ("pan_number", "{pan_number}"),
        ("email", "{email}"),
        ("phone", "{phone}"),
        ("name", "{customer_name}"),
        # Property
        ("project", "{project}"),
        ("bhk_type", "{bhk_type}"),
        ("unit_number", "{unit_number}"),
        ("tower", "{tower}"),
        ("customer_id", "{customer_id}"),
        ("booking_date", "{booking_date}"),
    ]
    # Numeric/computed fields — replace both raw and formatted-indian forms.
    # (field, placeholder, word_placeholder) — word_placeholder is optional
    # and, when set, the word-form ("Rupees ... Only" / "... Rupees") gets
    # scrubbed back to that token too.
    numeric_fields = [
        ("total_price", "{total_price}", "{total_price_words}", "{total_price_formatted}"),
        ("saleable_area", "{saleable_area}", None, None),
        ("uds", "{uds}", None, None),
        ("booking_amount", "{booking_amount}", "{booking_amount_words}", "{booking_amount_formatted}"),
        ("rate_per_sqft", "{rate_per_sqft}", None, None),
        ("base_price", "{base_price}", None, None),
        ("gst_amount", "{gst_amount}", None, None),
        ("labour_cess", "{labour_cess}", None, None),
        ("club_house_charges", "{club_house_charges}", None, None),
        ("interest_amount", "{interest_amount}", None, None),
        ("floor", "{floor}", None, None),
    ]

    pairs: list[tuple[str, str]] = []  # (literal, placeholder)
    for field, token in field_to_placeholder:
        val = customer.get(field)
        if not val or not isinstance(val, str):
            continue
        val = val.strip()
        # Skip tiny strings (1-2 chars) — high chance of corrupting layout
        if len(val) < 3:
            continue
        pairs.append((val, token))

    for field, token, words_token, formatted_token in numeric_fields:
        raw = customer.get(field)
        if raw in (None, 0, "0", "", "0.0"):
            continue
        try:
            num = float(raw)
        except (ValueError, TypeError):
            continue
        # Raw integer/float representations
        if num == int(num):
            pairs.append((str(int(num)), token))
        pairs.append((str(num), token))
        # Indian-format with and without ₹, both decimal variants
        try:
            for formatted in {
                format_indian_currency(num, decimals=False),
                format_indian_currency(num, decimals=True),
            }:
                if not formatted or len(formatted) < 3:
                    continue
                fmt_placeholder = formatted_token or token
                pairs.append((formatted, fmt_placeholder))
                pairs.append((f"₹{formatted}", fmt_placeholder))
                pairs.append((f"Rs. {formatted}", fmt_placeholder))
                pairs.append((f"Rs.{formatted}", fmt_placeholder))
        except (TypeError, ValueError):
            pass
        # Word form ("Rupees ... Only") — scrub back to {..._words}
        if words_token:
            try:
                words = number_to_indian_words(int(num))
                if words and len(words) > 3:
                    pairs.append((words, words_token))
            except (TypeError, ValueError):
                pass

    # Fetch transactions + schedule so we can compute the row-heavy blocks
    # that the source document rendered for this customer.
    cust_id = customer.get('id')
    transactions: list = []
    schedule_items: list = []
    if cust_id:
        transactions = await db.payment_transactions.find(
            {"customer_id": cust_id}, {"_id": 0}
        ).sort("transaction_date", 1).to_list(1000)
        schedule = await db.payment_schedules.find_one(
            {"customer_id": cust_id}, {"_id": 0}
        )
        schedule_items = (schedule or {}).get('items', []) if schedule else []

    # Total received (used by Sales Agreement clause + TOTAL RECEIVED footer)
    total_received = sum(float(t.get('amount', 0) or 0) for t in transactions)
    if total_received > 0:
        try:
            for formatted in {
                format_indian_currency(total_received, decimals=False),
                format_indian_currency(total_received, decimals=True),
            }:
                if not formatted or len(formatted) < 3:
                    continue
                pairs.append((formatted, "{total_received_formatted}"))
                pairs.append((f"₹{formatted}", "{total_received_formatted}"))
                pairs.append((f"Rs. {formatted}", "{total_received_formatted}"))
                pairs.append((f"Rs.{formatted}", "{total_received_formatted}"))
        except (TypeError, ValueError):
            pass
        try:
            words = number_to_indian_words(int(total_received))
            if words and len(words) > 3:
                pairs.append((words, "{total_received_words}"))
        except (TypeError, ValueError):
            pass

    # ---- Multi-line HTML blocks ----
    # These must be scrubbed BEFORE the scalar replacements below (which iterate
    # `pairs` sorted by length). By adding them to `pairs`, the longest-first
    # sort ensures they win over shorter scalar overlaps.
    applicant_block_html = build_applicant_details_block(customer)
    if applicant_block_html and len(applicant_block_html) > 10:
        pairs.append((applicant_block_html, "{applicant_details_block}"))

    schedule_rows_html = build_payment_schedule_rows_html(customer, schedule_items)
    if schedule_rows_html and len(schedule_rows_html) > 10:
        pairs.append((schedule_rows_html, "{payment_schedule_rows}"))

    txn_rows_html = build_transaction_rows_html(customer, transactions)
    if txn_rows_html and len(txn_rows_html) > 10:
        pairs.append((txn_rows_html, "{transaction_rows}"))

    # Agreement date text — the document was generated on some day; we don't
    # know exactly when, so scrub any "<Nth> Day of <Month>, ... - (dd-mm-yyyy)"
    # pattern back to {agreement_date_text}. Also try today's variant.
    import re as _re
    scrubbed = content
    agreement_pattern = _re.compile(
        r"\d+(?:st|nd|rd|th) Day of [A-Z][a-z]+, [A-Z][A-Za-z ]+- \(\d{2}-\d{2}-\d{4}\)"
    )
    scrubbed = agreement_pattern.sub("{agreement_date_text}", scrubbed)
    # Also cover today's exact literal in case the pattern above missed a variant.
    today_agreement = build_agreement_date_text()
    if today_agreement in scrubbed:
        scrubbed = scrubbed.replace(today_agreement, "{agreement_date_text}")

    # Replace longest values first so multi-line HTML blocks and long
    # customer values win over shorter overlapping fragments.
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    for literal, token in pairs:
        if literal and literal in scrubbed:
            scrubbed = scrubbed.replace(literal, token)
    return scrubbed

router = APIRouter(tags=["Documents"])
checklist_router = APIRouter(tags=["Document Checklist"])
upload_router = APIRouter(tags=["Document Upload"])


# ==================== DOCUMENT TEMPLATES ====================
@router.get("/templates")
async def get_templates(user: dict = Depends(get_current_user)):
    db = get_database()
    templates = await db.document_templates.find({}, {"_id": 0}).to_list(100)
    return templates


@router.post("/templates")
async def create_template(template: DocumentTemplate, user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    db = get_database()
    doc = template.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.document_templates.insert_one(doc)
    await log_activity(user['id'], user['name'], "create", "template", template.id, f"Created template {template.name}")
    return {"message": "Template created", "id": template.id}


@router.put("/templates/{template_id}")
async def update_template(template_id: str, updates: Dict[str, Any], user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    db = get_database()
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    result = await db.document_templates.update_one({"id": template_id}, {"$set": updates})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    await log_activity(user['id'], user['name'], "update", "template", template_id, "Updated template")
    return {"message": "Template updated"}


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str, user: dict = Depends(check_role([UserRole.ADMIN]))):
    """Revert to the built-in default by removing the admin override template."""
    db = get_database()
    result = await db.document_templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    await log_activity(user['id'], user['name'], "delete", "template", template_id, "Reverted to default template")
    return {"message": "Template removed, default restored"}


@router.post("/templates/bulk-delete")
async def bulk_delete_templates(
    body: Dict[str, Any], user: dict = Depends(check_role([UserRole.ADMIN]))
):
    """Bulk-remove admin override templates (admin only). Body: ``{"ids": [...]}``.
    Reverts each affected doc_type to the built-in default.
    """
    ids = body.get("ids") or []
    if not isinstance(ids, list) or not ids:
        raise HTTPException(status_code=400, detail="ids (non-empty list) is required")
    ids = [i for i in ids if isinstance(i, str) and i]
    if not ids:
        raise HTTPException(status_code=400, detail="No valid IDs provided")
    db = get_database()
    result = await db.document_templates.delete_many({"id": {"$in": ids}})
    await log_activity(
        user['id'], user['name'], "bulk_delete", "template", ",".join(ids),
        f"Bulk removed {result.deleted_count} override templates",
    )
    return {"message": "Templates removed, defaults restored", "deleted_count": result.deleted_count}


@router.post("/templates/snapshot/{doc_type}")
async def snapshot_default_template(doc_type: DocumentType, body: Dict[str, Any], user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    """Render the default document for a sample customer and save the HTML as
    a starting-point template the admin can then edit. Returns the new template."""
    db = get_database()
    sample_customer_id = body.get('customer_id')
    if not sample_customer_id:
        raise HTTPException(status_code=400, detail="customer_id required to render a sample")
    customer = await db.customers.find_one({"id": sample_customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Sample customer not found")
    # Temporarily disable any existing override so we render the built-in default
    existing = await db.document_templates.find_one({"doc_type": doc_type.value}, {"_id": 0})
    if existing:
        await db.document_templates.update_one({"id": existing['id']}, {"$set": {"is_active": False}})
    try:
        content = await render_document_content(db, customer, doc_type, {})
    finally:
        if existing:
            await db.document_templates.update_one({"id": existing['id']}, {"$set": {"is_active": existing.get('is_active', True)}})
    # Create new template (or overwrite existing) with the rendered HTML as starting point
    if existing:
        await db.document_templates.update_one(
            {"id": existing['id']},
            {"$set": {"content": content, "is_active": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        tmpl_id = existing['id']
    else:
        new_tmpl = DocumentTemplate(
            name=f"{doc_type.value} (custom)",
            doc_type=doc_type,
            content=content,
            is_active=True,
        )
        doc = new_tmpl.model_dump()
        doc['doc_type'] = doc_type.value
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.document_templates.insert_one(doc)
        tmpl_id = new_tmpl.id
    await log_activity(user['id'], user['name'], "snapshot", "template", tmpl_id, f"Created editable template for {doc_type.value}")
    saved = await db.document_templates.find_one({"id": tmpl_id}, {"_id": 0})
    return saved


@router.post("/templates/save-from-document/{doc_id}")
async def save_master_from_document(
    doc_id: str,
    user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER])),
):
    """Promote a generated, customer-edited document into the active master
    template for its doc_type. Future generations of the same doc_type will
    start from this content (with customer-specific placeholders re-substituted
    via the standard render pipeline)."""
    db = get_database()
    gen_doc = await db.generated_documents.find_one({"id": doc_id}, {"_id": 0})
    if not gen_doc:
        raise HTTPException(status_code=404, detail="Generated document not found")
    doc_type_value = gen_doc.get('doc_type')
    content = gen_doc.get('content') or ''
    if not content:
        raise HTTPException(status_code=400, detail="Document has no content to save")

    # CRITICAL: scrub the source customer's specific values (name, unit, prices,
    # dates, etc.) back to {placeholder} tokens, so the saved master template is
    # truly a FORMAT template — future customers' details get filled in by the
    # standard render pipeline. Only the document's structure/styling/legal text
    # is preserved.
    source_customer = await db.customers.find_one(
        {"id": gen_doc.get('customer_id')}, {"_id": 0}
    )
    if source_customer:
        content = await _scrub_customer_values_to_placeholders(db, content, source_customer)

    existing = await db.document_templates.find_one({"doc_type": doc_type_value}, {"_id": 0})
    now_iso = datetime.now(timezone.utc).isoformat()
    if existing:
        await db.document_templates.update_one(
            {"id": existing['id']},
            {"$set": {
                "content": content,
                "is_active": True,
                "updated_at": now_iso,
            }},
        )
        tmpl_id = existing['id']
    else:
        new_tmpl = DocumentTemplate(
            name=f"{doc_type_value} (master)",
            doc_type=DocumentType(doc_type_value),
            content=content,
            is_active=True,
        )
        doc = new_tmpl.model_dump()
        doc['doc_type'] = doc_type_value
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.document_templates.insert_one(doc)
        tmpl_id = new_tmpl.id
    await log_activity(
        user['id'], user['name'], "save_master", "template", tmpl_id,
        f"Saved {doc_type_value} as master template from doc {doc_id}",
    )
    return {"message": "Saved as master template", "template_id": tmpl_id, "doc_type": doc_type_value}


# ==================== DOCUMENT GENERATION ====================
@router.post("/documents/generate")
async def generate_document(data: DocumentGenerate, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": data.customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    content = await render_document_content(
        db, customer, data.doc_type, data.custom_fields
    )

    gen_doc = GeneratedDocument(
        customer_id=data.customer_id,
        doc_type=data.doc_type,
        content=content,
        generated_by=user['id']
    )
    doc = gen_doc.model_dump()
    doc['generated_at'] = doc['generated_at'].isoformat()
    await db.generated_documents.insert_one(doc)
    await log_activity(user['id'], user['name'], "generate", "document", gen_doc.id, f"Generated {data.doc_type.value}")
    return {"message": "Document generated", "document": {**doc, "_id": None}}


@router.post("/documents/generate-pdf/{customer_id}")
async def generate_price_breakup_pdf(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    html_content = generate_price_breakup_html(customer)
    gen_doc = GeneratedDocument(customer_id=customer_id, doc_type=DocumentType.PRICE_BREAKUP, content=html_content, generated_by=user['id'])
    doc = gen_doc.model_dump()
    doc['generated_at'] = doc['generated_at'].isoformat()
    await db.generated_documents.insert_one(doc)
    await log_activity(user['id'], user['name'], "generate", "price_breakup_pdf", customer_id, "Generated Price Breakup PDF")
    return {
        "message": "Price breakup generated",
        "document_id": gen_doc.id,
        "html_content": html_content,
        "filename": f"RRL_PalmAltezze_PriceBreakup_{customer.get('name', 'Customer').replace(' ', '_')}.pdf"
    }


@router.post("/documents/generate-payment-schedule-pdf/{customer_id}")
async def generate_payment_schedule_pdf(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    html_content = await render_document_content(db, customer, DocumentType.PAYMENT_SCHEDULE, {})
    await log_activity(user['id'], user['name'], "generate", "payment_schedule_pdf", customer_id, "Generated Payment Schedule PDF")
    return {"html": html_content, "filename": f"RRL_PaymentSchedule_{customer.get('name', 'Customer').replace(' ', '_')}.pdf"}


@router.post("/documents/generate-cost-breakup-pdf/{customer_id}")
async def generate_cost_breakup_pdf(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    html_content = generate_cost_breakup_html(customer)
    await log_activity(user['id'], user['name'], "generate", "cost_breakup_pdf", customer_id, "Generated Cost Breakup PDF")
    return {"html": html_content, "filename": f"RRL_CostBreakup_{customer.get('name', 'Customer').replace(' ', '_')}.pdf"}


# ==================== DOCUMENT HTML / LISTING ====================
@router.get("/documents/pdf/{doc_id}")
async def download_document_as_pdf(doc_id: str, user: dict = Depends(get_current_user)):
    """Convert a generated document's HTML to PDF and return it for download."""
    db = get_database()
    doc = await db.generated_documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    customer = await db.customers.find_one({"id": doc.get("customer_id")}, {"_id": 0, "name": 1, "unit_number": 1})
    customer_name = (customer.get("name", "Customer") if customer else "Customer").replace(" ", "_")
    doc_type_label = (doc.get("doc_type", "Document") or "Document").replace("_", " ").title().replace(" ", "_")
    filename = f"RRL_{doc_type_label}_{customer_name}.pdf"

    try:
        pdf_bytes: bytes = HTML(string=doc["content"]).write_pdf()
    except Exception as e:
        logger.error(f"PDF generation failed for doc {doc_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF") from e

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/documents/html/{doc_id}")
async def get_document_html(doc_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    doc = await db.generated_documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc['id'], "doc_type": doc['doc_type'], "content": doc['content'], "generated_at": doc['generated_at']}


@router.put("/documents/html/{doc_id}")
async def update_document_html(doc_id: str, body: Dict[str, Any], user: dict = Depends(get_current_user)):
    """Update the HTML content of a generated document (in-place edit before download)."""
    if user.get('role') == 'accounts':
        raise HTTPException(status_code=403, detail="Accounts role cannot edit documents")
    content = body.get('content')
    if not isinstance(content, str) or not content.strip():
        raise HTTPException(status_code=400, detail="content (string) is required")
    db = get_database()
    result = await db.generated_documents.update_one(
        {"id": doc_id},
        {"$set": {"content": content, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    await log_activity(user['id'], user['name'], "edit", "document", doc_id, "Edited generated document HTML")
    return {"message": "Document updated"}


@router.get("/documents/{customer_id}")
async def get_customer_documents(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    documents = await db.generated_documents.find({"customer_id": customer_id}, {"_id": 0}).to_list(100)
    return documents


@router.put("/documents/{doc_id}/status")
async def update_document_status(doc_id: str, status: AgreementStatus, user: dict = Depends(get_current_user)):
    db = get_database()
    result = await db.generated_documents.update_one({"id": doc_id}, {"$set": {"status": status.value}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    await log_activity(user['id'], user['name'], "update", "document", doc_id, f"Status changed to {status.value}")
    return {"message": "Document status updated"}


@router.delete("/documents/{doc_id}")
async def delete_generated_document(doc_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    if user['role'] == 'accounts':
        raise HTTPException(status_code=403, detail="Accounts role cannot delete documents")
    doc = await db.generated_documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.generated_documents.delete_one({"id": doc_id})
    await log_activity(user['id'], user['name'], "delete", "document", doc_id, f"Deleted generated document: {doc.get('doc_type')}")
    return {"message": "Document deleted successfully"}


@router.post("/documents/bulk-delete")
async def bulk_delete_generated_documents(
    body: Dict[str, Any], user: dict = Depends(check_role([UserRole.ADMIN]))
):
    """Bulk delete generated documents (admin only). Body: ``{"ids": [...]}``."""
    ids = body.get("ids") or []
    if not isinstance(ids, list) or not ids:
        raise HTTPException(status_code=400, detail="ids (non-empty list) is required")
    ids = [i for i in ids if isinstance(i, str) and i]
    if not ids:
        raise HTTPException(status_code=400, detail="No valid IDs provided")
    db = get_database()
    result = await db.generated_documents.delete_many({"id": {"$in": ids}})
    await log_activity(
        user['id'], user['name'], "bulk_delete", "document", ",".join(ids),
        f"Bulk deleted {result.deleted_count} generated documents",
    )
    return {"message": "Documents deleted", "deleted_count": result.deleted_count}


# ==================== PAYMENT RECEIPT ====================
async def _ensure_receipt_number(db, transaction: dict) -> dict:
    """Backfill a receipt_number on legacy transactions that don't have one."""
    if transaction.get("receipt_number"):
        return transaction
    counter = await db.settings.find_one_and_update(
        {"type": "receipt_counter"},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=True,
    )
    seq = int((counter or {}).get("value", 1) or 1)
    receipt_number = f"PAR-{seq:03d}"
    await db.payment_transactions.update_one(
        {"id": transaction["id"]}, {"$set": {"receipt_number": receipt_number}}
    )
    transaction["receipt_number"] = receipt_number
    return transaction


@router.post("/documents/payment-receipt/{customer_id}/{transaction_id}")
async def generate_payment_receipt(
    customer_id: str,
    transaction_id: str,
    user: dict = Depends(get_current_user),
):
    """Generate (or refresh) the Payment Receipt for a single transaction and
    return both its `doc_id` (for the EditableDocumentDialog) and `content`.
    Reuses an existing receipt for this transaction if already generated."""
    db = get_database()
    customer = await db.customers.find_one(
        {"$or": [{"id": customer_id}, {"customer_id": customer_id}]}, {"_id": 0}
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    transaction = await db.payment_transactions.find_one(
        {"id": transaction_id, "customer_id": customer.get("id")}, {"_id": 0}
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction = await _ensure_receipt_number(db, transaction)

    # Render fresh receipt HTML
    from documents.templates import generate_payment_receipt_html
    content = generate_payment_receipt_html(customer, transaction)

    # Re-use existing generated document for this transaction if present
    existing = await db.generated_documents.find_one(
        {
            "customer_id": customer.get("id"),
            "doc_type": DocumentType.PAYMENT_RECEIPT.value,
            "transaction_id": transaction_id,
        },
        {"_id": 0},
    )
    now_iso = datetime.now(timezone.utc).isoformat()
    if existing:
        await db.generated_documents.update_one(
            {"id": existing["id"]},
            {"$set": {"content": content, "updated_at": now_iso}},
        )
        doc_id = existing["id"]
    else:
        gen_doc = GeneratedDocument(
            customer_id=customer.get("id"),
            doc_type=DocumentType.PAYMENT_RECEIPT,
            content=content,
            generated_by=user["id"],
        )
        doc = gen_doc.model_dump()
        doc["generated_at"] = doc["generated_at"].isoformat()
        doc["transaction_id"] = transaction_id
        doc["receipt_number"] = transaction.get("receipt_number")
        await db.generated_documents.insert_one(doc)
        doc_id = gen_doc.id

    await log_activity(
        user["id"], user["name"], "generate", "document", doc_id,
        f"Generated payment receipt {transaction.get('receipt_number')}"
    )
    return {
        "id": doc_id,
        "doc_type": DocumentType.PAYMENT_RECEIPT.value,
        "content": content,
        "receipt_number": transaction.get("receipt_number"),
    }


@router.get("/documents/download/{doc_id}")
async def download_document(doc_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    doc = await db.customer_documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    content = base64.b64decode(doc['content_base64'])
    return Response(
        content=content,
        media_type=doc.get('content_type', 'application/octet-stream'),
        headers={"Content-Disposition": f"attachment; filename={doc['filename']}"}
    )


@router.get("/documents/preview/{doc_id}")
async def preview_document(doc_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    doc = await db.customer_documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc['id'],
        "filename": doc['filename'],
        "content_type": doc.get('content_type', 'application/octet-stream'),
        "content_base64": doc['content_base64']
    }


# ==================== TRANSACTION EXPORT HTML ====================
@router.get("/transactions/{customer_id}/export-html")
async def export_transactions_html(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one(
        {"$or": [{"id": customer_id}, {"customer_id": customer_id}]}, {"_id": 0}
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    cust_uuid = customer.get('id', '')
    cust_display_id = customer.get('customer_id', '')
    possible_ids = list(set(filter(None, [customer_id, cust_uuid, cust_display_id])))

    transactions = await db.payment_transactions.find(
        {"customer_id": {"$in": possible_ids}}, {"_id": 0}
    ).sort("transaction_date", 1).to_list(1000)

    for t in transactions:
        if not t.get("transaction_stage") and t.get("transaction_type"):
            t["transaction_stage"] = t["transaction_type"]

    html = generate_transactions_export_html(customer, transactions)
    return {"content": html, "customer_name": customer.get('name', 'Customer')}


# ==================== DOCUMENT UPLOAD ====================
@upload_router.post("/customers/{customer_id}/upload-document")
async def upload_customer_document(
    customer_id: str,
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    content = await file.read()
    base64_content = base64.b64encode(content).decode('utf-8')

    doc_record = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "doc_type": doc_type,
        "filename": file.filename,
        "content_type": file.content_type,
        "content_base64": base64_content,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "uploaded_by": user['id']
    }
    await db.customer_documents.insert_one(doc_record)

    uploaded_docs = customer.get('uploaded_documents', {})
    uploaded_docs[doc_type] = doc_record['id']
    await db.customers.update_one({"id": customer_id}, {"$set": {"uploaded_documents": uploaded_docs}})

    await log_activity(user['id'], user['name'], "upload", "document", customer_id, f"Uploaded {doc_type}")
    return {"message": "Document uploaded", "doc_id": doc_record['id']}


@upload_router.get("/customers/{customer_id}/documents-list")
async def get_customer_uploaded_documents(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    docs = await db.customer_documents.find(
        {"customer_id": customer_id},
        {"_id": 0, "content_base64": 0}
    ).to_list(100)
    return docs


@upload_router.delete("/customers/{customer_id}/documents/{doc_id}")
async def delete_uploaded_document(customer_id: str, doc_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    if user['role'] == 'accounts':
        raise HTTPException(status_code=403, detail="Accounts role cannot delete documents")
    doc = await db.customer_documents.find_one({"id": doc_id, "customer_id": customer_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.customer_documents.delete_one({"id": doc_id})

    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if customer:
        uploaded_docs = customer.get('uploaded_documents', {})
        for key, val in list(uploaded_docs.items()):
            if val == doc_id:
                del uploaded_docs[key]
                break
        await db.customers.update_one({"id": customer_id}, {"$set": {"uploaded_documents": uploaded_docs}})

    await log_activity(user['id'], user['name'], "delete", "uploaded_document", doc_id, f"Deleted uploaded document: {doc.get('filename', doc.get('doc_type'))}")
    return {"message": "Document deleted successfully"}


@upload_router.post("/customers/{customer_id}/documents/bulk-delete")
async def bulk_delete_uploaded_documents(
    customer_id: str, body: Dict[str, Any],
    user: dict = Depends(check_role([UserRole.ADMIN])),
):
    """Bulk delete uploaded documents for a customer (admin only). Body:
    ``{"ids": ["<doc_id>", ...]}``. Also strips the pointers from the
    customer's ``uploaded_documents`` map."""
    ids = body.get("ids") or []
    if not isinstance(ids, list) or not ids:
        raise HTTPException(status_code=400, detail="ids (non-empty list) is required")
    ids = [i for i in ids if isinstance(i, str) and i]
    if not ids:
        raise HTTPException(status_code=400, detail="No valid IDs provided")
    db = get_database()
    result = await db.customer_documents.delete_many(
        {"id": {"$in": ids}, "customer_id": customer_id}
    )
    # Strip these ids from the customer's uploaded_documents pointer map
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if customer:
        uploaded_docs = customer.get('uploaded_documents', {}) or {}
        pruned = {k: v for k, v in uploaded_docs.items() if v not in ids}
        if pruned != uploaded_docs:
            await db.customers.update_one(
                {"id": customer_id}, {"$set": {"uploaded_documents": pruned}}
            )
    await log_activity(
        user['id'], user['name'], "bulk_delete", "uploaded_document",
        customer_id, f"Bulk deleted {result.deleted_count} uploaded documents",
    )
    return {"message": "Documents deleted", "deleted_count": result.deleted_count}


# ==================== DOCUMENT CHECKLIST ====================
@checklist_router.get("/checklist/{customer_id}")
async def get_checklist(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    checklist = await db.document_checklists.find_one({"customer_id": customer_id}, {"_id": 0})
    if not checklist:
        checklist = DocumentChecklist(customer_id=customer_id)
        doc = checklist.model_dump()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.document_checklists.insert_one(doc)
        return doc
    return checklist


@checklist_router.put("/checklist/{customer_id}")
async def update_checklist(customer_id: str, items: Dict[str, bool], user: dict = Depends(get_current_user)):
    db = get_database()
    result = await db.document_checklists.update_one(
        {"customer_id": customer_id},
        {"$set": {"items": items, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Checklist not found")
    await log_activity(user['id'], user['name'], "update", "checklist", customer_id, "Updated document checklist")
    return {"message": "Checklist updated"}
