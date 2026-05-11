"""
Email/Communication routes for RRL CRM.
Handles email previews, sending, communication history, and email logs.
"""
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
import uuid
import base64
import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from weasyprint import HTML

from database import get_database
from config import settings
from utils.enums import DocumentType
from auth import get_current_user, log_activity
from documents.models import GeneratedDocument, CommunicationLog
from dashboard.models import EmailSendRequest
from documents.templates import (
    generate_price_breakup_html, generate_booking_form_preview_html,
    generate_terms_and_conditions_html, generate_welcome_email_html,
    generate_document_email_html, generate_sales_agreement_html,
    generate_allotment_letter_html, generate_demand_letter_html
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Communication"])

SENDGRID_API_KEY = settings.SENDGRID_API_KEY
SENDGRID_FROM_EMAIL = settings.SENDGRID_FROM_EMAIL
SENDGRID_FROM_NAME = settings.SENDGRID_FROM_NAME


# ==================== EMAIL PREVIEWS ====================
@router.get("/communication/preview-welcome-email/{customer_id}")
async def preview_welcome_email(customer_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    welcome_html = generate_welcome_email_html(customer)
    form_preview_html = generate_booking_form_preview_html(customer)
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
        "has_sendgrid": bool(SENDGRID_API_KEY)
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
        "has_sendgrid": bool(SENDGRID_API_KEY)
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
        "has_sendgrid": bool(SENDGRID_API_KEY)
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
        form_preview_html = generate_booking_form_preview_html(customer)
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

    if SENDGRID_API_KEY:
        try:
            message = Mail(from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME), to_emails=recipient_email, subject=data.subject, html_content=email_html)
            if hasattr(data, 'cc') and data.cc:
                message.add_cc(data.cc)
            for att in attachments_data:
                try:
                    pdf_bytes = HTML(string=att['html']).write_pdf()
                    encoded_pdf = base64.b64encode(pdf_bytes).decode()
                    attachment = Attachment(FileContent(encoded_pdf), FileName(att['filename']), FileType('application/pdf'), Disposition('attachment'))
                    message.add_attachment(attachment)
                except Exception as pdf_error:
                    logger.error(f"Error generating PDF attachment {att['filename']}: {str(pdf_error)}")
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            if response.status_code in [200, 201, 202]:
                email_status = "sent"
            else:
                email_status = "failed"
        except Exception as e:
            email_status = "error"
            logger.error(f"SendGrid error: {str(e)}")
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
    form_preview_html = generate_booking_form_preview_html(customer)
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

    if SENDGRID_API_KEY:
        try:
            message = Mail(from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME), to_emails=recipient_email, subject=subject, html_content=welcome_html)
            for html_str, fname in [(form_preview_html, filename_form_preview), (terms_conditions_html, filename_terms), (price_breakup_html, filename_price)]:
                try:
                    pdf_bytes = HTML(string=html_str).write_pdf()
                    encoded_pdf = base64.b64encode(pdf_bytes).decode()
                    attachment = Attachment(FileContent(encoded_pdf), FileName(fname), FileType('application/pdf'), Disposition('attachment'))
                    message.add_attachment(attachment)
                    attachments_added.append(fname)
                except Exception as pdf_error:
                    logger.error(f"Error generating PDF {fname}: {str(pdf_error)}")
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            if response.status_code in [200, 201, 202]:
                email_status = "sent"
                sendgrid_response = {"status_code": response.status_code, "body": f"Email sent successfully with {len(attachments_added)} attachments"}
            else:
                email_status = "failed"
                sendgrid_response = {"status_code": response.status_code, "error": "Unexpected status code"}
        except Exception as e:
            email_status = "failed"
            sendgrid_response = {"error": str(e)}
            logger.error(f"SendGrid error: {str(e)}")
    else:
        email_status = "mocked (no API key)"
        attachments_added = [filename_form_preview, filename_terms, filename_price]

    log = CommunicationLog(
        customer_id=customer_id, channel="email", message_type="Welcome Email",
        content=f"To: {recipient_email}\nSubject: {subject}\n\n[Welcome Email HTML Body]\n\nAttachments:\n1. {filename_form_preview}\n2. {filename_terms}\n3. {filename_price}",
        status=email_status, sent_by=user['id']
    )
    log_doc = log.model_dump()
    log_doc['sent_at'] = log_doc['sent_at'].isoformat()
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
    customer_id: str,
    subject: str,
    message: str,
    attachment_doc_id: Optional[str] = None,
    attachment_ids: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    recipient_email = customer.get('email')
    email_status = "pending"
    sendgrid_response = None
    attachments_info = []

    if attachment_ids:
        doc_ids = [id.strip() for id in attachment_ids.split(",") if id.strip()]
        for doc_id in doc_ids:
            doc = await db.generated_documents.find_one({"id": doc_id}, {"_id": 0})
            if doc:
                attachments_info.append(f"Generated: {doc.get('doc_type', 'document')}")
            else:
                doc = await db.customer_documents.find_one({"id": doc_id}, {"_id": 0})
                if doc:
                    attachments_info.append(f"Uploaded: {doc.get('filename', doc.get('doc_type', 'document'))}")

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

    if SENDGRID_API_KEY:
        try:
            sg_message = Mail(from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME), to_emails=recipient_email, subject=subject, html_content=html_content)
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(sg_message)
            if response.status_code in [200, 201, 202]:
                email_status = "sent"
                sendgrid_response = {"status_code": response.status_code}
            else:
                email_status = "failed"
                sendgrid_response = {"status_code": response.status_code}
        except Exception as e:
            email_status = "failed"
            sendgrid_response = {"error": str(e)}
            logger.error(f"SendGrid error: {str(e)}")
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
