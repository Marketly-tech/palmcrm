"""
Booking and Leads routes for RRL CRM.
Handles public booking form, public document upload, leads management.
"""
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel, EmailStr
import asyncio
import uuid
import base64
import logging

import resend
from weasyprint import HTML

from database import get_database
from config import settings
from utils.enums import UserRole, AgreementStatus
from auth import get_current_user, log_activity, check_role
from customers.models import Customer, DocumentChecklist, GoogleFormWebhook
from documents.models import CommunicationLog
from customers import generate_customer_id
from utils.payment_helpers import auto_generate_booking_transaction
from documents.templates import generate_welcome_email_html, generate_price_breakup_html, generate_booking_form_preview_html, generate_terms_and_conditions_html
from documents.templates.common import get_welcome_email_static_attachments

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Booking & Leads"])

RESEND_API_KEY = settings.RESEND_API_KEY
RESEND_FROM_EMAIL = settings.RESEND_FROM_EMAIL
RESEND_FROM_NAME = settings.RESEND_FROM_NAME
RESEND_BCC_ARCHIVE = settings.RESEND_BCC_ARCHIVE
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


class BookingFormData(BaseModel):
    name: str
    phone: str
    email: EmailStr
    father_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    profession: Optional[str] = None
    nationality: str = "Indian"
    co_applicant_name: Optional[str] = None
    co_applicant_father_name: Optional[str] = None
    co_applicant_gender: Optional[str] = None  # male, female, spouse
    co_applicant_phone: Optional[str] = None
    co_applicant_email: Optional[str] = None
    co_applicant_pan: Optional[str] = None
    co_applicant_aadhar: Optional[str] = None
    co_applicant_address: Optional[str] = None
    co_applicant_date_of_birth: Optional[str] = None
    co_applicant_profession: Optional[str] = None
    co_applicant_nationality: Optional[str] = "Indian"
    project: str
    tower: str
    unit_number: str
    bhk_type: Optional[str] = ""
    floor: int = 0
    saleable_area: float = 0
    rate_per_sqft: float = 0
    floor_rise_cost: float = 0
    parking: Optional[str] = "1"
    additional_parking: int = 0  # Legacy — kept for backward compat, not used in pricing
    total_price: float = 0
    base_price: float = 0
    floor_rise_total: float = 0
    club_house_charges: float = 300000  # Fixed ₹3L on booking; editable in customer profile
    additional_parking_charges: float = 200000  # Fixed ₹2L car parking on booking; editable in customer profile
    additional_charges: float = 0
    bescom_rate: float = 0  # ₹ per saleable sqft; total = bescom_rate × saleable_area
    labour_cess: float = 0
    gst_amount: float = 0
    booking_amount: float = 0
    transaction_details: Optional[str] = None
    transaction_date: Optional[str] = None
    transaction_bank: Optional[str] = None
    finance_type: str = "self"
    finance_bank: Optional[str] = None
    remarks: Optional[str] = None


def _resolve_unit_fields(data, unit):
    """Resolve property fields from form data or unit database."""
    return {
        "rate_per_sqft": data.rate_per_sqft if data.rate_per_sqft > 0 else (unit.get('rate_per_sqft', 0) if unit else 0),
        "saleable_area": data.saleable_area if data.saleable_area > 0 else (unit.get('saleable_area', 0) if unit else 0),
        "floor": data.floor if data.floor > 0 else (unit.get('floor', 0) if unit else 0),
        "bhk_type": data.bhk_type if data.bhk_type else (unit.get('bhk_type', '') if unit else ''),
        "floor_rise_cost": data.floor_rise_cost if data.floor_rise_cost > 0 else 0,
    }


def _calculate_pricing(data, fields):
    """Calculate pricing from form data or auto-calculate from unit fields."""
    sa = fields["saleable_area"]
    frc = fields["floor_rise_cost"]
    bescom_amount = (data.bescom_rate or 0) * sa
    if data.total_price > 0:
        return {
            "base_price": data.base_price, "floor_rise_total": data.floor_rise_total,
            "club_house": data.club_house_charges, "parking_charges": data.additional_parking_charges,
            "additional_charges": data.additional_charges,
            "bescom_amount": bescom_amount,
            "labour_cess": data.labour_cess, "gst": data.gst_amount, "total_price": data.total_price,
        }
    base_price = fields["rate_per_sqft"] * sa
    floor_rise_total = frc * sa
    # Fixed charges on every new booking — editable later in customer profile.
    club_house = 300000     # ₹3L
    parking_charges = 200000  # ₹2L fixed car parking (was: additional_parking * 300000)
    additional_charges = data.additional_charges or 0
    subtotal = base_price + floor_rise_total + club_house + parking_charges + additional_charges + bescom_amount
    return {
        "base_price": base_price, "floor_rise_total": floor_rise_total,
        "club_house": club_house, "parking_charges": parking_charges,
        "additional_charges": additional_charges,
        "bescom_amount": bescom_amount,
        "labour_cess": subtotal * 0.007, "gst": subtotal * 0.05,
        "total_price": subtotal + subtotal * 0.007 + subtotal * 0.05,
    }


async def _send_booking_welcome_email(customer, doc):
    """Send auto welcome email on booking submission.

    Attaches the full welcome-email document pack so the auto-sent email has
    parity with the manual "Send Welcome Email" composer:
      1. Booking Form Preview (snapshot of just-submitted form)
      2. Terms & Conditions
      3. Price Breakup
      4. Static Total Registration Charges (asset)
    """
    if not customer.email or not RESEND_API_KEY:
        return "not_sent"
    try:
        welcome_html = generate_welcome_email_html(doc)
        customer_name_safe = customer.name.replace(' ', '_')
        # Use the immutable snapshot captured at submission if present,
        # otherwise fall back to live render (first-time booking path).
        form_preview_html = (
            doc.get('original_booking_form_html')
            or generate_booking_form_preview_html(doc)
        )
        terms_conditions_html = generate_terms_and_conditions_html(doc)
        price_breakup_html = generate_price_breakup_html(doc)

        subject = f"Welcome to {customer.project} - Booking Confirmation & Terms"
        attachments = []
        # Generate PDFs for each rendered HTML attachment. Individual failures
        # are logged but don't block the email going out (e.g. if WeasyPrint
        # chokes on one template, the others still ship).
        rendered_pack = [
            (f"RRL_BookingFormPreview_{customer_name_safe}.pdf", form_preview_html),
            (f"RRL_TermsAndConditions_{customer_name_safe}.pdf", terms_conditions_html),
            (f"RRL_PriceBreakup_{customer_name_safe}.pdf", price_breakup_html),
        ]
        for filename, html_str in rendered_pack:
            try:
                pdf_bytes = HTML(string=html_str).write_pdf()
                attachments.append({
                    "filename": filename,
                    "content": base64.b64encode(pdf_bytes).decode(),
                })
            except Exception as pdf_error:
                logger.error(f"Error generating PDF {filename} for auto-email: {pdf_error}")
        # Append static welcome-email add-ons (e.g. Total Registration Charges)
        attachments.extend(get_welcome_email_static_attachments())
        params = {
            "from": f"{RESEND_FROM_NAME} <{RESEND_FROM_EMAIL}>",
            "to": [customer.email],
            "subject": subject,
            "html": welcome_html,
        }
        if RESEND_BCC_ARCHIVE and RESEND_BCC_ARCHIVE.strip():
            params["bcc"] = [RESEND_BCC_ARCHIVE.strip()]
        if attachments:
            params["attachments"] = attachments
        result = await asyncio.to_thread(resend.Emails.send, params)
        if result.get("id"):
            db = get_database()
            attachment_list = ", ".join(a["filename"] for a in attachments)
            log = CommunicationLog(customer_id=customer.id, channel="email", message_type="Auto Welcome Email",
                content=f"To: {customer.email}\nSubject: {subject}\nResend ID: {result.get('id')}\nAttachments: {attachment_list}\n\n[Auto-sent on booking submission]",
                status="sent", sent_by="system")
            log_doc = log.model_dump()
            log_doc['sent_at'] = log_doc['sent_at'].isoformat()
            log_doc['resend_message_id'] = result.get("id")
            await db.communication_logs.insert_one(log_doc)
            return "sent"
        return "failed"
    except Exception as e:
        logger.error(f"Error auto-sending welcome email: {str(e)}")
        return "error"


@router.post("/public/booking-form")
async def submit_booking_form(data: BookingFormData):
    db = get_database()
    unit = await db.units.find_one({"project": data.project, "tower": data.tower, "unit_number": data.unit_number}, {"_id": 0})

    fields = _resolve_unit_fields(data, unit)
    pricing = _calculate_pricing(data, fields)
    uds = round(fields["saleable_area"] * 0.495046, 2) if fields["saleable_area"] > 0 else 0
    total_price = round(pricing["total_price"], 2)

    customer = Customer(
        name=data.name, phone=data.phone, email=data.email,
        father_name=data.father_name or "", date_of_birth=data.date_of_birth,
        gender=data.gender or "male", pan_number=data.pan_number or "",
        aadhar_number=data.aadhar_number or "", address=data.address or "",
        company=data.company, designation=data.designation, nationality=data.nationality,
        co_applicant_name=data.co_applicant_name, co_applicant_father_name=data.co_applicant_father_name,
        co_applicant_gender=data.co_applicant_gender,
        co_applicant_date_of_birth=data.co_applicant_date_of_birth,
        co_applicant_phone=data.co_applicant_phone, co_applicant_email=data.co_applicant_email,
        co_applicant_pan=data.co_applicant_pan, co_applicant_aadhar=data.co_applicant_aadhar,
        co_applicant_address=data.co_applicant_address,
        project=data.project, tower=data.tower, unit_number=data.unit_number,
        floor=fields["floor"], bhk_type=fields["bhk_type"], saleable_area=fields["saleable_area"], uds=uds,
        parking=data.parking, additional_parking=data.additional_parking,
        rate_per_sqft=fields["rate_per_sqft"], base_price=round(pricing["base_price"], 2),
        club_house_charges=round(pricing["club_house"], 2), additional_parking_charges=round(pricing["parking_charges"], 2),
        additional_charges=round(pricing.get("additional_charges", 0), 2),
        bescom_rate=data.bescom_rate or 0,
        labour_cess=round(pricing["labour_cess"], 2), gst_percentage=5, gst_amount=round(pricing["gst"], 2),
        total_price=total_price, booking_amount=data.booking_amount,
        booking_date=data.transaction_date or datetime.now().strftime("%Y-%m-%d"),
        total_received=data.booking_amount,
        balance_amount=round(total_price - data.booking_amount, 2),
        payment_received_percentage=round((data.booking_amount / total_price * 100) if total_price > 0 else 0, 2),
        payment_pending_percentage=round(100 - ((data.booking_amount / total_price * 100) if total_price > 0 else 0), 2),
        finance_type=data.finance_type, finance_bank=data.finance_bank,
        stage="pending_approval", agreement_status="draft",
        transaction_details=data.transaction_details, transaction_date=data.transaction_date,
        transaction_bank=data.transaction_bank, remarks=data.remarks,
        custom_fields={
            "profession": data.profession or "",
            "floor_rise_cost": fields["floor_rise_cost"],
            "floor_rise_total": round(pricing["floor_rise_total"], 2),
            "co_applicant_profession": data.co_applicant_profession or "",
            "co_applicant_nationality": data.co_applicant_nationality or "Indian",
        }
    )
    customer.customer_id = await generate_customer_id()

    doc = customer.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    # IMMUTABLE booking-form snapshot — captured once, never overwritten.
    # This is the *original* booking form preview that goes out in the auto
    # welcome email; the customer profile may later be edited but this stays
    # frozen. See /app/memory/DEPLOYMENT_INVARIANTS.md § Booking Form Snapshot.
    try:
        snapshot_html = generate_booking_form_preview_html(doc)
        doc['original_booking_form_html'] = snapshot_html
        doc['original_booking_form_snapshot_at'] = datetime.now(timezone.utc).isoformat()
        # Also persist the rendered PDF binary so View/Download always serves
        # the exact-fidelity file (no on-the-fly re-render needed).
        try:
            snapshot_pdf_bytes = HTML(string=snapshot_html).write_pdf()
            doc['original_booking_form_pdf_b64'] = base64.b64encode(snapshot_pdf_bytes).decode()
            doc['original_booking_form_pdf_recovered_from'] = "booking_submit"
        except Exception as pdf_err:
            logger.error(f"Booking-form PDF snapshot failed for {customer.id}: {pdf_err}")
    except Exception as snap_err:
        logger.error(f"Booking-form snapshot failed for {customer.id}: {snap_err}")
    await db.customers.insert_one(doc)

    checklist = DocumentChecklist(customer_id=customer.id)
    checklist_doc = checklist.model_dump()
    checklist_doc['updated_at'] = checklist_doc['updated_at'].isoformat()
    await db.document_checklists.insert_one(checklist_doc)

    if unit:
        await db.units.update_one({"id": unit['id']}, {"$set": {"is_available": False}})

    await log_activity("system", "Booking Form", "create", "customer", customer.id, f"New booking: {customer.name} for {data.project} - {data.unit_number}")

    email_status = await _send_booking_welcome_email(customer, doc)

    return {
        "message": "Booking submitted successfully! Our team will contact you shortly.",
        "customer_id": customer.customer_id,
        "reference_id": customer.id,
        "welcome_email_status": email_status
    }


@router.post("/public/upload-document/{customer_id}")
async def public_upload_document(customer_id: str, doc_type: str = Form(...), file: UploadFile = File(...)):
    db = get_database()
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    content = await file.read()
    base64_content = base64.b64encode(content).decode('utf-8')

    doc_record = {
        "id": str(uuid.uuid4()), "customer_id": customer_id, "doc_type": doc_type,
        "filename": file.filename, "content_type": file.content_type,
        "content_base64": base64_content, "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "uploaded_by": "public_booking"
    }
    await db.customer_documents.insert_one(doc_record)

    uploaded_docs = customer.get('uploaded_documents', {})
    uploaded_docs[doc_type] = doc_record['id']
    await db.customers.update_one({"id": customer_id}, {"$set": {"uploaded_documents": uploaded_docs}})

    await log_activity("system", "Booking Form", "upload", "document", customer_id, f"Uploaded {doc_type}")
    return {"message": "Document uploaded", "doc_id": doc_record['id']}


@router.post("/webhook/google-form")
async def google_form_webhook(data: GoogleFormWebhook, background_tasks: BackgroundTasks):
    db = get_database()
    customer = Customer(
        name=data.customer_name, phone=data.phone, email=data.email,
        project=data.project, tower=data.tower, unit_number=data.unit_number,
        father_name=data.father_name or "", pan_number=data.pan_number or "",
        booking_amount=data.booking_amount or 0,
        booking_date=data.booking_date or datetime.now().strftime("%Y-%m-%d"),
        agreement_status=AgreementStatus.DRAFT
    )
    customer.customer_id = await generate_customer_id()

    doc = customer.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.customers.insert_one(doc)

    checklist = DocumentChecklist(customer_id=customer.id)
    checklist_doc = checklist.model_dump()
    checklist_doc['updated_at'] = checklist_doc['updated_at'].isoformat()
    await db.document_checklists.insert_one(checklist_doc)

    welcome_log = CommunicationLog(
        customer_id=customer.id, channel="email", message_type="welcome",
        content=f"Welcome to RRL Builders! Your booking for {data.project} - {data.unit_number} has been received.",
        status="sent (MOCKED)", sent_by="system"
    )
    log_doc = welcome_log.model_dump()
    log_doc['sent_at'] = log_doc['sent_at'].isoformat()
    await db.communication_logs.insert_one(log_doc)

    await log_activity("system", "System", "create", "customer", customer.id, f"Customer created via Google Form: {customer.name}")
    await auto_generate_booking_transaction(customer.id, doc, created_by="system")

    return {"message": "Customer created successfully", "customer_id": customer.customer_id}


# ==================== LEADS MANAGEMENT ====================
@router.get("/leads/pending")
async def get_pending_leads(user: dict = Depends(get_current_user)):
    db = get_database()
    leads = await db.customers.find({"stage": "pending_approval"}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return leads


@router.put("/leads/{customer_id}/approve")
async def approve_lead(customer_id: str, user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.SALES]))):
    db = get_database()
    result = await db.customers.update_one(
        {"id": customer_id, "stage": "pending_approval"},
        {"$set": {"stage": "qualified", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found or already approved")
    await log_activity(user['id'], user['name'], "approve", "lead", customer_id, "Lead approved and qualified")
    return {"message": "Lead approved successfully"}


@router.put("/leads/{customer_id}/reject")
async def reject_lead(customer_id: str, reason: str = "", user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.SALES]))):
    db = get_database()
    if not reason or not reason.strip():
        raise HTTPException(status_code=400, detail="Rejection reason is required")
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.units.update_one(
        {"project": customer['project'], "tower": customer['tower'], "unit_number": customer['unit_number']},
        {"$set": {"is_available": True}}
    )
    await db.customers.delete_one({"id": customer_id})
    await db.document_checklists.delete_one({"customer_id": customer_id})
    await log_activity(user['id'], user['name'], "reject", "lead", customer_id, f"Lead rejected: {reason}")
    return {"message": "Lead rejected and removed"}


@router.put("/leads/{customer_id}/stage")
async def update_lead_stage(customer_id: str, stage: str, user: dict = Depends(get_current_user)):
    db = get_database()
    valid_stages = ["pending_approval", "qualified", "agreement_pending", "agreement_done", "registration_done"]
    if stage not in valid_stages:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {valid_stages}")
    result = await db.customers.update_one(
        {"id": customer_id},
        {"$set": {"stage": stage, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    await log_activity(user['id'], user['name'], "update", "customer_stage", customer_id, f"Stage changed to {stage}")
    return {"message": f"Stage updated to {stage}"}
