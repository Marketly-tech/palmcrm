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
from documents.generators import render_document_content

logger = logging.getLogger(__name__)

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
    schedule = await db.payment_schedules.find_one({"customer_id": customer_id}, {"_id": 0})
    schedule_items = schedule.get('items', []) if schedule else []
    if not schedule_items:
        raise HTTPException(status_code=404, detail="No payment schedule found. Please generate one first.")
    html_content = generate_payment_schedule_html(customer, schedule_items)
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
        pdf_bytes = HTML(string=doc["content"]).write_pdf()
    except Exception as e:
        logger.error(f"PDF generation failed for doc {doc_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

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
