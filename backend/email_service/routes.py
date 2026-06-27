"""
Email/Communication routes for RRL CRM.
Handles email previews, sending, communication history, and email logs.
"""
import asyncio
import base64
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

import resend
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from weasyprint import HTML

from auth import get_current_user, log_activity
from config import settings
from dashboard.models import EmailSendRequest
from database import get_database
from documents.models import CommunicationLog, GeneratedDocument
from documents.templates.common import get_welcome_email_static_attachments
from documents.templates import (
    generate_allotment_letter_html,
    generate_booking_form_preview_html,
    generate_demand_letter_html,
    generate_document_email_html,
    generate_price_breakup_html,
    generate_sales_agreement_html,
    generate_terms_and_conditions_html,
    generate_welcome_email_html,
)
from utils.enums import DocumentType

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Communication"])

RESEND_API_KEY = settings.RESEND_API_KEY
RESEND_FROM_EMAIL = settings.RESEND_FROM_EMAIL
RESEND_FROM_NAME = settings.RESEND_FROM_NAME
RESEND_BCC_ARCHIVE = settings.RESEND_BCC_ARCHIVE
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


async def _resend_send(
    *,
    to_email: str,
    subject: str,
    html_content: str,
    attachments: Optional[list] = None,
) -> dict:
    """Send an email via Resend. Attachments: list of dicts shaped
    {"filename": str, "content": <bytes>, "content_type": str}.
    Resend expects raw bytes (or base64 string); we pass base64 strings.

    Resend SDK is sync — runs in a thread to keep the FastAPI loop free.
    Returns {"status": "sent"|"failed", "id": str|None, "error": str|None}.
    Always BCCs ``RESEND_BCC_ARCHIVE`` (when set) for a silent off-platform
    archive — see DEPLOYMENT_INVARIANTS.md § Email Archive BCC.
    """
    if not RESEND_API_KEY:
        return {"status": "mocked (no API key)", "id": None, "error": None}

    params: dict = {
        "from": f"{RESEND_FROM_NAME} <{RESEND_FROM_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }
    if RESEND_BCC_ARCHIVE and RESEND_BCC_ARCHIVE.strip():
        params["bcc"] = [RESEND_BCC_ARCHIVE.strip()]
    if attachments:
        params["attachments"] = [
            {
                "filename": a["filename"],
                "content": (
                    a["content"]
                    if isinstance(a["content"], str)
                    else base64.b64encode(a["content"]).decode()
                ),
            }
            for a in attachments
            if a.get("filename") and a.get("content") is not None
        ]
    try:
        result = await asyncio.to_thread(resend.Emails.send, params)
        return {"status": "sent", "id": result.get("id"), "error": None}
    except Exception as e:
        logger.error(f"Resend error: {e}")
        return {"status": "failed", "id": None, "error": str(e)}


# ==================== EMAIL PREVIEWS ====================
@router.get("/communication/preview-welcome-email/{customer_id}")
async def preview_welcome_email(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    welcome_html = generate_welcome_email_html(customer)
    # Booking Form Preview — use the IMMUTABLE snapshot captured at booking
    # submission if it exists, otherwise fall back to live render.
    form_preview_html = (
        customer.get('original_booking_form_html')
        or generate_booking_form_preview_html(customer)
    )
    terms_conditions_html = generate_terms_and_conditions_html(customer)
    price_breakup_html = generate_price_breakup_html(customer)

    customer_name_safe = customer.get('name', 'Customer').replace(' ', '_')
    filename_form = f"RRL_BookingFormPreview_{customer_name_safe}.pdf"
    filename_terms = f"RRL_TermsAndConditions_{customer_name_safe}.pdf"
    filename_price = f"RRL_PriceBreakup_{customer_name_safe}.pdf"

    recipient_email = customer.get('email')
    subject = f"Welcome to {customer.get('project', 'RRL Builders')} - Booking Confirmation & Documents"

    default_body = f"""Hello {customer.get('name', '')},

Greetings from RRL Builders and Developers Pvt Ltd.

It is our distinct pleasure to welcome you to {customer.get('project', 'RRL Palm Altezze')} and to congratulate you on the acquisition of your Residence Flat No. {customer.get('unit_number', '')}.

Please find attached the following documents for your reference:
1. Booking Form Preview - Your submitted booking details
2. Terms & Conditions - Important terms governing your allotment
3. Price Breakup - Detailed price calculation

Your dedicated Relationship Director will connect with you personally to ensure that every interaction with us is seamless and tailored to your expectations."""

    return {
        "email_type": "welcome",
        "customer_name": customer.get('name'),
        "recipient_email": recipient_email,
        "subject": subject,
        "body": default_body,
        "email_html": welcome_html,
        "attachment_html": form_preview_html,
        "attachment_filename": filename_form,
        "attachment_html_2": terms_conditions_html,
        "attachment_filename_2": filename_terms,
        "attachment_html_3": price_breakup_html,
        "attachment_filename_3": filename_price,
        "attachments": [filename_form, filename_terms, filename_price],
        "has_sendgrid": bool(RESEND_API_KEY)
    }


@router.get("/communication/preview-sales-agreement/{customer_id}")
async def preview_sales_agreement_email(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    schedule = await db.payment_schedules.find_one({"customer_id": customer_id}, {"_id": 0})
    schedule_items = schedule.get('items', []) if schedule else []
    transactions = await db.payment_transactions.find(
        {"customer_id": customer_id}, {"_id": 0}
    ).sort("transaction_date", 1).to_list(1000)

    sales_agreement_html = generate_sales_agreement_html(customer, schedule_items, transactions)
    price_breakup_html = generate_price_breakup_html(customer)

    recipient_email = customer.get('email')
    subject = f"SALE AGREEMENT DRAFT AND PRICE BREAK UP - {customer.get('unit_number', '')}"

    default_body = f"""Hello {customer.get('name', '')},

Greetings from RRL Builders and Developers Pvt Ltd.

We are delighted to take this process ahead, please find attached draft copy of the sale agreement.

We would like to know the date when you are signing up for sale agreement.

Please review the attached documents:
1. Sale Agreement Draft
2. Price Break Up

Looking forward to your confirmation."""

    email_html = generate_document_email_html(customer, subject, default_body)

    return {
        "email_type": "sales_agreement",
        "customer_name": customer.get('name'),
        "recipient_email": recipient_email,
        "subject": subject,
        "body": default_body,
        "email_html": email_html,
        "attachment_html": sales_agreement_html,
        "attachment_html_2": price_breakup_html,
        "attachment_filename": f"RRL_SaleAgreement_{customer.get('name', 'Customer').replace(' ', '_')}.pdf",
        "attachment_filename_2": f"RRL_PriceBreakup_{customer.get('name', 'Customer').replace(' ', '_')}.pdf",
        "has_sendgrid": bool(RESEND_API_KEY)
    }


@router.get("/communication/preview-allotment-letter/{customer_id}")
async def preview_allotment_letter_email(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    allotment_letter_html = generate_allotment_letter_html(customer)
    recipient_email = customer.get('email')
    subject = f"ALLOTMENT LETTER - {customer.get('project', 'RRL Palm Altezze')} - Flat No. {customer.get('unit_number', '')}"

    default_body = f"""Hello {customer.get('name', '')},

Greetings from RRL Builders and Developers Pvt Ltd.

We are pleased to confirm your allotment for Flat No. {customer.get('unit_number', '')} in {customer.get('project', 'RRL Palm Altezze')}.

Please find attached your Allotment Letter for your records.

Kindly review the terms and conditions mentioned in the letter and let us know if you have any queries."""

    email_html = generate_document_email_html(customer, subject, default_body)

    return {
        "email_type": "allotment_letter",
        "customer_name": customer.get('name'),
        "recipient_email": recipient_email,
        "subject": subject,
        "body": default_body,
        "email_html": email_html,
        "attachment_html": allotment_letter_html,
        "attachment_filename": f"RRL_AllotmentLetter_{customer.get('name', 'Customer').replace(' ', '_')}.pdf",
        "has_sendgrid": bool(RESEND_API_KEY)
    }


# ==================== EMAIL SENDING ====================
@router.post("/communication/send-document-email/{customer_id}")
async def send_document_email(customer_id: str, data: EmailSendRequest, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    recipient_email = data.recipient_email or customer.get('email')
    email_html = generate_document_email_html(customer, data.subject, data.body)
    attachments_data = []

    if data.email_type == "welcome":
        form_preview_html = (
            customer.get('original_booking_form_html')
            or generate_booking_form_preview_html(customer)
        )
        terms_conditions_html = generate_terms_and_conditions_html(customer)
        price_breakup_html = generate_price_breakup_html(customer)
        customer_name_safe = customer.get('name', 'Customer').replace(' ', '_')
        attachments_data.append({"filename": f"RRL_BookingFormPreview_{customer_name_safe}.pdf", "html": form_preview_html, "doc_type": DocumentType.WELCOME_LETTER})
        attachments_data.append({"filename": f"RRL_TermsAndConditions_{customer_name_safe}.pdf", "html": terms_conditions_html, "doc_type": DocumentType.WELCOME_LETTER})
        attachments_data.append({"filename": f"RRL_PriceBreakup_{customer_name_safe}.pdf", "html": price_breakup_html, "doc_type": DocumentType.PRICE_BREAKUP})
    elif data.email_type == "sales_agreement":
        schedule = await db.payment_schedules.find_one({"customer_id": customer_id}, {"_id": 0})
        schedule_items = schedule.get('items', []) if schedule else []
        transactions = await db.payment_transactions.find({"customer_id": customer_id}, {"_id": 0}).sort("transaction_date", 1).to_list(1000)
        sales_agreement_html = generate_sales_agreement_html(customer, schedule_items, transactions)
        price_breakup_html = generate_price_breakup_html(customer)
        attachments_data.append({"filename": f"RRL_SaleAgreement_{customer.get('name', 'Customer').replace(' ', '_')}.pdf", "html": sales_agreement_html, "doc_type": DocumentType.SALES_AGREEMENT})
        attachments_data.append({"filename": f"RRL_PriceBreakup_{customer.get('name', 'Customer').replace(' ', '_')}.pdf", "html": price_breakup_html, "doc_type": DocumentType.PRICE_BREAKUP})
    elif data.email_type == "allotment_letter":
        allotment_letter_html = generate_allotment_letter_html(customer)
        attachments_data.append({"filename": f"RRL_AllotmentLetter_{customer.get('name', 'Customer').replace(' ', '_')}.pdf", "html": allotment_letter_html, "doc_type": DocumentType.ALLOTMENT_LETTER})

    for att in attachments_data:
        doc = GeneratedDocument(customer_id=customer_id, doc_type=att['doc_type'], content=att['html'], generated_by=user['id'])
        doc_dict = doc.model_dump()
        doc_dict['generated_at'] = doc_dict['generated_at'].isoformat()
        await db.generated_documents.insert_one(doc_dict)

    email_status = "pending"
    sendgrid_response = None

    if RESEND_API_KEY:
        # Build attachment list for Resend (filename + base64 content)
        resend_attachments = []
        for att in attachments_data:
            try:
                pdf_bytes = HTML(string=att['html']).write_pdf()
                resend_attachments.append({
                    "filename": att['filename'],
                    "content": base64.b64encode(pdf_bytes).decode(),
                })
            except Exception as pdf_error:
                logger.error(f"Error generating PDF attachment {att['filename']}: {pdf_error}")
        result = await _resend_send(
            to_email=recipient_email,
            subject=data.subject,
            html_content=email_html,
            attachments=resend_attachments,
        )
        email_status = result["status"]
        sendgrid_response = {"provider": "resend", "id": result.get("id"), "error": result.get("error")}
    else:
        email_status = "simulated"

    comm_log = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "type": "email",
        "subject": data.subject,
        "message": data.body,
        "status": email_status,
        "email_type": data.email_type,
        "attachments": [att['filename'] for att in attachments_data],
        "resend_message_id": (sendgrid_response or {}).get("id") if isinstance(sendgrid_response, dict) else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": user['id']
    }
    await db.communications.insert_one(comm_log)
    await log_activity(user['id'], user['name'], "send", "email", customer_id, f"Sent {data.email_type} email to {recipient_email}")

    return {
        "message": f"{data.email_type.replace('_', ' ').title()} email sent successfully",
        "status": email_status,
        "recipient": recipient_email,
        "attachments": [att['filename'] for att in attachments_data]
    }


@router.post("/communication/send-welcome-email/{customer_id}")
async def send_welcome_email(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    welcome_html = generate_welcome_email_html(customer)
    price_breakup_html = generate_price_breakup_html(customer)
    form_preview_html = (
        customer.get('original_booking_form_html')
        or generate_booking_form_preview_html(customer)
    )
    terms_conditions_html = generate_terms_and_conditions_html(customer)

    welcome_doc = GeneratedDocument(customer_id=customer_id, doc_type=DocumentType.WELCOME_LETTER, content=welcome_html, generated_by=user['id'])
    welcome_doc_dict = welcome_doc.model_dump()
    welcome_doc_dict['generated_at'] = welcome_doc_dict['generated_at'].isoformat()
    await db.generated_documents.insert_one(welcome_doc_dict)

    price_doc = GeneratedDocument(customer_id=customer_id, doc_type=DocumentType.PRICE_BREAKUP, content=price_breakup_html, generated_by=user['id'])
    price_doc_dict = price_doc.model_dump()
    price_doc_dict['generated_at'] = price_doc_dict['generated_at'].isoformat()
    await db.generated_documents.insert_one(price_doc_dict)

    customer_name_safe = customer.get('name', 'Customer').replace(' ', '_')
    filename_form_preview = f"RRL_BookingFormPreview_{customer_name_safe}.pdf"
    filename_terms = f"RRL_TermsAndConditions_{customer_name_safe}.pdf"
    filename_price = f"RRL_PriceBreakup_{customer_name_safe}.pdf"

    recipient_email = customer.get('email')
    subject = f"Welcome to {customer.get('project', 'RRL Builders')} - Booking Confirmation & Documents"

    email_status = "pending"
    sendgrid_response = None
    attachments_added = []

    if RESEND_API_KEY:
        resend_attachments = []
        for html_str, fname in [(form_preview_html, filename_form_preview), (terms_conditions_html, filename_terms), (price_breakup_html, filename_price)]:
            try:
                pdf_bytes = HTML(string=html_str).write_pdf()
                resend_attachments.append({"filename": fname, "content": base64.b64encode(pdf_bytes).decode()})
                attachments_added.append(fname)
            except Exception as pdf_error:
                logger.error(f"Error generating PDF {fname}: {pdf_error}")
        # Append static welcome-email add-ons (e.g. Total Registration Charges)
        for static_att in get_welcome_email_static_attachments():
            resend_attachments.append(static_att)
            attachments_added.append(static_att["filename"])
        result = await _resend_send(
            to_email=recipient_email,
            subject=subject,
            html_content=welcome_html,
            attachments=resend_attachments,
        )
        email_status = result["status"]
        sendgrid_response = {
            "provider": "resend",
            "id": result.get("id"),
            "error": result.get("error"),
            "attachments": len(attachments_added),
        }
    else:
        email_status = "mocked (no API key)"
        attachments_added = [filename_form_preview, filename_terms, filename_price]

    log = CommunicationLog(
        customer_id=customer_id, channel="email", message_type="Welcome Email",
        content=f"To: {recipient_email}\nSubject: {subject}\nResend ID: {(sendgrid_response or {}).get('id') if isinstance(sendgrid_response, dict) else 'N/A'}\n\n[Welcome Email HTML Body]\n\nAttachments:\n1. {filename_form_preview}\n2. {filename_terms}\n3. {filename_price}",
        status=email_status, sent_by=user['id']
    )
    log_doc = log.model_dump()
    log_doc['sent_at'] = log_doc['sent_at'].isoformat()
    log_doc['resend_message_id'] = (sendgrid_response or {}).get("id") if isinstance(sendgrid_response, dict) else None
    await db.communication_logs.insert_one(log_doc)

    if customer.get('stage') == 'pending_approval':
        await db.customers.update_one({"id": customer_id}, {"$set": {"stage": "qualified", "updated_at": datetime.now(timezone.utc).isoformat()}})

    await log_activity(user['id'], user['name'], "send", "welcome_email", customer_id, f"Sent welcome email to {recipient_email} with 3 PDFs - Status: {email_status}")

    return {
        "message": f"Welcome email {email_status}",
        "welcome_doc_id": welcome_doc.id,
        "price_breakup_doc_id": price_doc.id,
        "email_to": recipient_email,
        "email_status": email_status,
        "attachments": attachments_added,
        "sendgrid_response": sendgrid_response
    }


@router.post("/communication/email")
async def send_email_notification(
    customer_id: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    attachment_doc_id: Optional[str] = Form(None),
    attachment_ids: Optional[str] = Form(None),
    local_file: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user),
):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    recipient_email = customer.get('email')
    if not recipient_email:
        raise HTTPException(status_code=400, detail="Customer has no email address on file")
    email_status = "pending"
    sendgrid_response = None
    attachments_info = []
    sg_attachments = []  # List of {filename, content (base64)} dicts for Resend

    # Parse attachment_ids (frontend sends JSON array string, legacy callers send CSV)
    doc_ids = []
    if attachment_ids:
        try:
            import json as _json
            parsed = _json.loads(attachment_ids)
            if isinstance(parsed, list):
                doc_ids = [str(x).strip() for x in parsed if str(x).strip()]
        except (ValueError, TypeError):
            doc_ids = [i.strip() for i in attachment_ids.split(",") if i.strip()]

    for doc_id in doc_ids:
        gen = await db.generated_documents.find_one({"id": doc_id}, {"_id": 0})
        if gen:
            doc_type = gen.get('doc_type', 'document')
            attachments_info.append(f"Generated: {doc_type}")
            try:
                pdf_bytes = HTML(string=gen.get('content', '')).write_pdf()
                customer_name_safe = customer.get('name', 'Customer').replace(' ', '_')
                fname = f"RRL_{doc_type.replace('_', ' ').title().replace(' ', '_')}_{customer_name_safe}.pdf"
                sg_attachments.append({
                    "filename": fname,
                    "content": base64.b64encode(pdf_bytes).decode(),
                })
            except Exception as e:
                logger.error(f"Failed to attach generated doc {doc_id}: {e}")
            continue
        uploaded = await db.customer_documents.find_one({"id": doc_id}, {"_id": 0})
        if uploaded:
            fname = uploaded.get('filename') or f"{uploaded.get('doc_type', 'document')}.bin"
            attachments_info.append(f"Uploaded: {fname}")
            content_b64 = uploaded.get('content_base64')
            if content_b64:
                sg_attachments.append({"filename": fname, "content": content_b64})

    # Handle local-file upload from the email composer
    if local_file is not None:
        try:
            file_bytes = await local_file.read()
            if file_bytes:
                attachments_info.append(f"Uploaded: {local_file.filename}")
                sg_attachments.append({
                    "filename": local_file.filename or "attachment.bin",
                    "content": base64.b64encode(file_bytes).decode(),
                })
        except Exception as e:
            logger.error(f"Failed to attach local_file: {e}")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: 'Roboto', Arial, sans-serif; line-height: 1.6; color: #1A1A1A; background: #f5f5f5; margin: 0; padding: 30px;">
        <div style="max-width: 650px; margin: 0 auto; background: #fff; border: 2px solid #D4AF37; border-radius: 8px; overflow: hidden;">
            <div style="background: #1A1A1A; padding: 20px; display: flex; align-items: center;">
                <div style="background: #D4AF37; color: #1A1A1A; padding: 10px 15px; border-radius: 6px; font-weight: bold; font-size: 18px; margin-right: 15px;">RRL</div>
                <div>
                    <div style="color: #D4AF37; font-size: 18px; font-weight: 700;">RRL Builders and Developers</div>
                    <div style="color: #999; font-size: 11px;">Beyond homes. A lifestyle</div>
                </div>
            </div>
            <div style="padding: 30px;">
                <p style="margin: 0 0 20px 0;">Dear {customer.get('name', 'Customer')},</p>
                <div style="white-space: pre-line; margin-bottom: 25px;">{message}</div>
                <div style="margin-top: 30px; padding: 20px; background: #fafafa; border-radius: 8px;">
                    <div style="font-size: 15px; font-weight: 600; color: #1A1A1A; margin-bottom: 3px;">John</div>
                    <div style="font-size: 12px; color: #D4AF37; font-weight: 500; margin-bottom: 12px;">CRM MANAGER</div>
                    <div style="font-size: 12px; color: #666; line-height: 1.6;">
                        <strong>P:</strong> 9606579135<br>
                        <strong>E:</strong> <a href="mailto:crm@rrlbuildersanddevelopers.com" style="color: #D4AF37;">crm@rrlbuildersanddevelopers.com</a><br>
                        <strong>A:</strong> 4TH Floor, RRL Tower, Sompura gate, Sarjapura Bengaluru - 562125<br><br>
                        <a href="https://www.rrlbuildersanddevelopers.com" style="color: #D4AF37;">www.rrlbuildersanddevelopers.com</a>
                    </div>
                </div>
            </div>
            <div style="background: #fafafa; padding: 15px; text-align: center; font-size: 11px; color: #888; border-top: 1px solid #e0e0e0;">
                <p style="margin: 0;">RRL Builders and Developers Pvt. Ltd. | <a href="https://www.rrlbuildersanddevelopers.com" style="color: #D4AF37;">www.rrlbuildersanddevelopers.com</a></p>
            </div>
        </div>
    </body>
    </html>"""

    if RESEND_API_KEY:
        result = await _resend_send(
            to_email=recipient_email,
            subject=subject,
            html_content=html_content,
            attachments=sg_attachments,
        )
        email_status = result["status"]
        sendgrid_response = {
            "provider": "resend",
            "id": result.get("id"),
            "error": result.get("error"),
            "attachments": len(sg_attachments),
        }
    else:
        email_status = "mocked (no API key)"

    log_content = f"To: {recipient_email}\nSubject: {subject}\n\n{message}"
    if attachments_info:
        log_content += "\n\nAttachments:\n- " + "\n- ".join(attachments_info)

    log = CommunicationLog(customer_id=customer_id, channel="email", message_type=subject, content=log_content, status=email_status, sent_by=user['id'])
    doc = log.model_dump()
    doc['sent_at'] = doc['sent_at'].isoformat()
    await db.communication_logs.insert_one(doc)

    await log_activity(user['id'], user['name'], "send", "email", customer_id, f"Email: {subject} - Status: {email_status}")
    return {"message": f"Email {email_status}", "log_id": log.id, "email_status": email_status, "sendgrid_response": sendgrid_response}


@router.post("/communication/whatsapp")
async def send_whatsapp_notification(customer_id: str, message: str, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    log = CommunicationLog(customer_id=customer_id, channel="whatsapp", message_type="notification", content=f"To: {customer['phone']}\n\n{message}", status="sent (MOCKED)", sent_by=user['id'])
    doc = log.model_dump()
    doc['sent_at'] = doc['sent_at'].isoformat()
    await db.communication_logs.insert_one(doc)

    await log_activity(user['id'], user['name'], "send", "whatsapp", customer_id, "WhatsApp notification")
    return {"message": "WhatsApp sent (MOCKED - Configure Twilio for production)", "log_id": log.id}


@router.get("/communication/{customer_id}")
async def get_communication_history(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    logs = await db.communication_logs.find({"customer_id": customer_id}, {"_id": 0}).sort("sent_at", -1).to_list(100)
    return logs


@router.get("/email-logs")
async def get_all_email_logs(
    page: int = 1,
    limit: int = 50,
    status: Optional[str] = None,
    search: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    db = get_database()
    query = {"channel": "email"}
    if status and status != "all":
        query["status"] = {"$regex": status, "$options": "i"}

    total = await db.communication_logs.count_documents(query)
    skip = (page - 1) * limit
    logs = await db.communication_logs.find(query, {"_id": 0}).sort("sent_at", -1).skip(skip).limit(limit).to_list(limit)

    customer_ids = list(set(log.get("customer_id", "") for log in logs))
    customers = {}
    if customer_ids:
        customer_docs = await db.customers.find(
            {"id": {"$in": customer_ids}}, {"_id": 0, "id": 1, "name": 1, "email": 1, "customer_id": 1}
        ).to_list(len(customer_ids))
        customers = {c["id"]: c for c in customer_docs}

    enriched_logs = []
    for log in logs:
        cust = customers.get(log.get("customer_id", ""), {})
        log["customer_name"] = cust.get("name", "Unknown")
        log["customer_email"] = cust.get("email", "")
        log["customer_display_id"] = cust.get("customer_id", "")
        if search:
            search_lower = search.lower()
            if (search_lower not in log.get("customer_name", "").lower() and
                search_lower not in log.get("message_type", "").lower() and
                search_lower not in log.get("content", "").lower() and
                search_lower not in log.get("customer_email", "").lower()):
                continue
        enriched_logs.append(log)

    return {"logs": enriched_logs, "total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit}
