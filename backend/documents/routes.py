"""
Document routes for RRL CRM.
Handles document generation, templates, PDF export, upload/download, and checklist.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import Response
import uuid
import base64
import logging

from database import get_database
from config import settings
from utils.enums import UserRole, DocumentType, AgreementStatus
from utils import format_indian_currency
from utils.payment_helpers import PAYMENT_STAGES
from auth import get_current_user, log_activity, check_role
from documents.models import (
    DocumentTemplate, DocumentGenerate, GeneratedDocument, CommunicationLog
)
from customers.models import DocumentChecklist

from documents.templates import (
    generate_sales_agreement_template, get_default_template,
    generate_price_breakup_html, generate_cost_breakup_html,
    generate_noc_hdfc_html, generate_noc_bob_html, generate_noc_tata_html,
    generate_booking_form_preview_html, generate_terms_and_conditions_html,
    generate_welcome_email_html, generate_document_email_html,
    generate_sales_agreement_html, generate_allotment_letter_html,
    generate_payment_schedule_pdf_html, generate_payment_schedule_html,
    generate_demand_letter_html
)

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


# ==================== DOCUMENT GENERATION ====================
@router.post("/documents/generate")
async def generate_document(data: DocumentGenerate, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": data.customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if data.doc_type == DocumentType.SALES_AGREEMENT:
        schedule = await db.payment_schedules.find_one({"customer_id": data.customer_id}, {"_id": 0})
        schedule_items = schedule.get('items', []) if schedule else []
        transactions = await db.payment_transactions.find(
            {"customer_id": data.customer_id}, {"_id": 0}
        ).sort("transaction_date", 1).to_list(1000)
        content = generate_sales_agreement_html(customer, schedule_items, transactions)
    elif data.doc_type == DocumentType.PRICE_BREAKUP:
        content = generate_price_breakup_html(customer)
    elif data.doc_type == DocumentType.COST_BREAKUP:
        content = generate_cost_breakup_html(customer)
    elif data.doc_type == DocumentType.ALLOTMENT_LETTER:
        content = generate_allotment_letter_html(customer)
    elif data.doc_type == DocumentType.PAYMENT_SCHEDULE:
        transactions = await db.payment_transactions.find(
            {"customer_id": data.customer_id}, {"_id": 0}
        ).sort("transaction_date", 1).to_list(1000)
        content = generate_payment_schedule_pdf_html(customer, transactions)
    elif data.doc_type == DocumentType.NOC_HDFC:
        content = generate_noc_hdfc_html(customer)
    elif data.doc_type == DocumentType.NOC_BOB:
        content = generate_noc_bob_html(customer)
    elif data.doc_type == DocumentType.NOC_TATA:
        content = generate_noc_tata_html(customer)
    elif data.doc_type == DocumentType.DEMAND_LETTER:
        transactions = await db.payment_transactions.find(
            {"customer_id": data.customer_id}, {"_id": 0}
        ).sort("transaction_date", 1).to_list(1000)
        stage_settings = await db.settings.find_one({"type": "payment_stage"}, {"_id": 0})
        stage_info = {}
        if stage_settings and stage_settings.get("current_stage"):
            stage_key = stage_settings.get("current_stage")
            stage_info = next((s for s in PAYMENT_STAGES if s["key"] == stage_key), {})
        content = generate_demand_letter_html(customer, transactions, stage_info)
    else:
        template = await db.document_templates.find_one({"doc_type": data.doc_type.value}, {"_id": 0})
        if not template:
            template = {"content": get_default_template(data.doc_type)}
        content = template['content']

        total_price = customer.get('total_price', 0)
        total_price_formatted = format_indian_currency(total_price, decimals=False) if total_price else "0"
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
        for key, value in data.custom_fields.items():
            placeholders[f"{{{key}}}"] = value
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, str(value))

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
@router.get("/documents/html/{doc_id}")
async def get_document_html(doc_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    doc = await db.generated_documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc['id'], "doc_type": doc['doc_type'], "content": doc['content'], "generated_at": doc['generated_at']}


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

    from documents.templates.common import get_logo_img_tag, COMPANY_NAME, format_customer_names

    def fmt_inr(amount):
        amount = float(amount) if amount else 0
        int_part = int(amount)
        s = str(int_part)
        if len(s) > 3:
            result = s[-3:]
            s = s[:-3]
            while s:
                result = s[-2:] + ',' + result
                s = s[:-2]
        else:
            result = s
        return f"\u20b9{result}"

    total_received = sum(float(t.get('amount', 0) or 0) for t in transactions)
    total_price = float(customer.get('total_price', 0) or 0)
    balance = total_price - total_received
    customer_names = format_customer_names(customer)

    co_applicant_row = ""
    if customer.get('co_applicant_name'):
        co_applicant_row = f'''
            <div class="info-item">
                <div class="info-label">Co-Applicant</div>
                <div class="info-value">{customer.get('co_applicant_name', '')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Co-Applicant Phone</div>
                <div class="info-value">{customer.get('co_applicant_phone', '') or '-'}</div>
            </div>'''

    txn_rows = ""
    for i, txn in enumerate(transactions, 1):
        amount = txn.get('amount', 0) or 0
        stage = (txn.get('transaction_stage', '') or 'Payment').replace('_', ' ').title()
        txn_date = txn.get('transaction_date', '-')
        bank = txn.get('bank_name', '-') or '-'
        txn_no = txn.get('transaction_number', '-') or '-'
        notes = txn.get('notes', '') or ''
        txn_rows += f'''
        <tr>
            <td style="text-align: center;">{i}</td>
            <td>{txn_date}</td>
            <td>{stage}</td>
            <td>{bank}</td>
            <td>{txn_no}</td>
            <td style="text-align: right; font-weight: 500;">{fmt_inr(amount)}</td>
            <td>{notes}</td>
        </tr>'''

    if not txn_rows:
        txn_rows = '<tr><td colspan="7" style="text-align: center; padding: 20px; color: #666;">No transactions recorded</td></tr>'

    html = f'''<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Roboto', sans-serif; padding: 30px; color: #1A1A1A; background: #fff; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #D4AF37; padding-bottom: 20px; margin-bottom: 25px; }}
            .logo-section {{ display: flex; align-items: center; gap: 15px; }}
            .logo img {{ width: 100px; height: auto; }}
            .company-name {{ font-size: 20px; font-weight: 700; color: #1A1A1A; }}
            .company-tagline {{ font-size: 11px; color: #666; }}
            .document-title {{ background: #1A1A1A; color: #D4AF37; padding: 10px 20px; border-radius: 4px; font-weight: 500; font-size: 13px; text-transform: uppercase; }}
            .customer-info {{ background: #fafafa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #D4AF37; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .info-item {{ padding: 5px 0; }}
            .info-label {{ color: #666; font-size: 11px; }}
            .info-value {{ font-weight: 500; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th {{ background: #1A1A1A; color: #D4AF37; padding: 10px 8px; text-align: left; font-size: 11px; font-weight: 500; }}
            td {{ padding: 10px 8px; border-bottom: 1px solid #e0e0e0; font-size: 11px; }}
            tr:nth-child(even) {{ background: #fafafa; }}
            .summary {{ margin-top: 20px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
            .summary-box {{ padding: 15px; border-radius: 8px; text-align: center; }}
            .summary-box.total {{ background: #1A1A1A; color: #D4AF37; }}
            .summary-box.received {{ background: #e8f5e9; border: 1px solid #28a745; }}
            .summary-box.balance {{ background: #fff3e0; border: 1px solid #D4AF37; }}
            .summary-label {{ font-size: 10px; text-transform: uppercase; }}
            .summary-value {{ font-size: 18px; font-weight: 700; margin-top: 5px; }}
            .footer {{ margin-top: 30px; padding-top: 15px; border-top: 2px solid #D4AF37; text-align: center; font-size: 10px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-section">
                    <div class="logo">{get_logo_img_tag(100)}</div>
                    <div>
                        <div class="company-name">{COMPANY_NAME}</div>
                        <div class="company-tagline">Beyond homes. A lifestyle</div>
                    </div>
                </div>
                <div class="document-title">Transaction Details</div>
            </div>
            <div class="customer-info">
                <div class="info-item">
                    <div class="info-label">Customer Name</div>
                    <div class="info-value">{customer.get('name', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Phone</div>
                    <div class="info-value">{customer.get('phone', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Project</div>
                    <div class="info-value">{customer.get('project', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Unit Number</div>
                    <div class="info-value">{customer.get('tower', '')}-{customer.get('unit_number', '-')}</div>
                </div>
                {co_applicant_row}
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 4%;">#</th>
                        <th style="width: 12%;">Date</th>
                        <th style="width: 16%;">Stage</th>
                        <th style="width: 16%;">Bank</th>
                        <th style="width: 18%;">Transaction No.</th>
                        <th style="width: 14%; text-align: right;">Amount</th>
                        <th style="width: 20%;">Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {txn_rows}
                </tbody>
            </table>
            <div class="summary">
                <div class="summary-box total">
                    <div class="summary-label">Total Property Value</div>
                    <div class="summary-value">{fmt_inr(total_price)}</div>
                </div>
                <div class="summary-box received">
                    <div class="summary-label">Total Received</div>
                    <div class="summary-value" style="color: #28a745;">{fmt_inr(total_received)}</div>
                </div>
                <div class="summary-box balance">
                    <div class="summary-label">Balance Pending</div>
                    <div class="summary-value" style="color: #D4AF37;">{fmt_inr(balance)}</div>
                </div>
            </div>
            <div class="footer">
                <p>{COMPANY_NAME} | www.rrlbuildersanddevelopers.com</p>
                <p>Generated on {datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")} UTC</p>
            </div>
        </div>
    </body>
    </html>'''

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
