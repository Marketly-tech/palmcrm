"""
Customer models for RRL CRM.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, EmailStr, ConfigDict
import uuid


class CustomerBase(BaseModel):
    # Primary Applicant
    name: str
    phone: str
    email: EmailStr
    father_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None  # male, female, or spouse (for W/o)
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    nationality: str = "Indian"
    
    # Co-Applicant Details
    co_applicant_name: Optional[str] = None
    co_applicant_father_name: Optional[str] = None
    co_applicant_phone: Optional[str] = None
    co_applicant_email: Optional[str] = None
    co_applicant_pan: Optional[str] = None
    co_applicant_aadhar: Optional[str] = None
    co_applicant_address: Optional[str] = None
    co_applicant_date_of_birth: Optional[str] = None
    co_applicant_gender: Optional[str] = None  # male, female, spouse
    
    # Property Details
    project: str
    tower: str
    unit_number: str
    booking_number: Optional[str] = None
    floor: int = 0
    bhk_type: str = ""
    saleable_area: float = 0
    uds: float = 0  # Undivided Share
    parking: Optional[str] = None
    additional_parking: int = 0  # Number of additional parking (legacy)
    
    # Pricing
    rate_per_sqft: float = 0
    base_price: float = 0  # rate * saleable_area
    club_house_charges: float = 300000  # Fixed ₹3L default; editable in customer profile
    infrastructure_charges: float = 0
    additional_charges: float = 0  # Manual additional charges
    additional_charges_description: str = ""  # Optional label shown in PDF row when amount > 0
    additional_parking_charges: float = 200000  # Fixed ₹2L car parking; editable in customer profile
    bescom_rate: float = 0  # ₹ per saleable sqft. BESCOM total = bescom_rate × saleable_area. Goes into subtotal (before GST + labour cess).
    labour_cess: float = 0  # 0.70% of subtotal by default. Admin can override for negotiated / legacy records; see labour_cess_manual flag.
    labour_cess_manual: bool = False  # When true, ``labour_cess`` is honoured verbatim (no auto-recalc). Toggled from the Property & Pricing card.
    gst_percentage: float = 5
    gst_amount: float = 0
    interest_amount: float = 0  # Manual entry, added after GST (non GST-taxable)
    total_price: float = 0  # Total including GST + Interest
    
    # Payment Tracking
    booking_amount: float = 0
    booking_date: Optional[str] = None
    agreement_date: Optional[str] = None
    total_received: float = 0
    balance_amount: float = 0
    payment_received_percentage: float = 0
    payment_pending_percentage: float = 100
    
    # Finance Details
    finance_type: str = "self"  # self, loan, mixed
    finance_bank: Optional[str] = None
    loan_amount: float = 0
    self_contribution: float = 0
    first_disbursement_amount: float = 0
    first_disbursement_date: Optional[str] = None
    
    # Status
    stage: str = "pending_approval"  # pending_approval, qualified, agreement_pending, agreement_done, registration_done
    agreement_status: str = "draft"
    ownership: str = "builder"  # builder, customer
    registration_date: Optional[str] = None
    handover_date: Optional[str] = None
    
    # Transaction Details
    transaction_details: Optional[str] = None
    transaction_date: Optional[str] = None
    transaction_bank: Optional[str] = None
    
    # Notes
    remarks: Optional[str] = None
    custom_fields: Dict[str, Any] = {}
    
    # Document Uploads (store file paths/urls)
    uploaded_documents: Dict[str, str] = {}  # {doc_type: file_url}
    
    # IMMUTABLE snapshot — captured once at booking submission and never overwritten.
    # Used to render the original Booking Form Preview that was auto-emailed to the
    # customer on the day they booked, even after admin edits the live profile.
    # See /app/memory/DEPLOYMENT_INVARIANTS.md § Booking Form Snapshot.
    original_booking_form_html: Optional[str] = None
    original_booking_form_snapshot_at: Optional[str] = None
    # IMMUTABLE recovered PDF binary (base64). Set ONLY by the Resend recovery
    # script for customers whose welcome email is still in Resend's retention
    # window. Customers with this field present have the *true* originally-sent
    # PDF; those without fall back to ``original_booking_form_html`` snapshot.
    original_booking_form_pdf_b64: Optional[str] = None
    original_booking_form_pdf_recovered_from: Optional[str] = None  # e.g. "resend:<email_id>"


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None


class DocumentChecklist(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    items: Dict[str, bool] = {
        "kyc_documents": False,
        "pan_card": False,
        "aadhar": False,
        "agreement_copy": False,
        "bank_documents": False,
        "passport_photo": False,
        "address_proof": False
    }
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GoogleFormWebhook(BaseModel):
    customer_name: str
    phone: str
    email: EmailStr
    project: str
    tower: str
    unit_number: str
    father_name: Optional[str] = None
    pan_number: Optional[str] = None
    booking_amount: Optional[float] = 0
    booking_date: Optional[str] = None
