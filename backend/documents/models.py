"""
Document-related models for RRL CRM.
"""
from typing import Optional, List, Dict
from pydantic import BaseModel
from utils.enums import DocumentType, AgreementStatus


class DocumentTemplate(BaseModel):
    name: str
    type: DocumentType
    content: str
    variables: List[str] = []
    is_active: bool = True


class DocumentGenerate(BaseModel):
    customer_id: str
    template_type: DocumentType
    custom_data: Optional[Dict] = None


class GeneratedDocument(BaseModel):
    id: str
    customer_id: str
    template_type: DocumentType
    generated_at: str
    html_content: str
    pdf_url: Optional[str] = None
    status: AgreementStatus = AgreementStatus.PENDING
    signed_at: Optional[str] = None


class DocumentChecklist(BaseModel):
    customer_id: str
    pan_card: bool = False
    aadhar_card: bool = False
    photo: bool = False
    address_proof: bool = False
    bank_statement: bool = False
    income_proof: bool = False
    co_applicant_pan: bool = False
    co_applicant_aadhar: bool = False
    co_applicant_photo: bool = False


class CommunicationLog(BaseModel):
    id: str
    customer_id: str
    type: str  # email, whatsapp, call
    subject: Optional[str] = None
    content: str
    sent_at: str
    sent_by: str
    status: str = "sent"


class ActivityLog(BaseModel):
    id: str
    user_id: str
    user_name: str
    action: str
    entity_type: str
    entity_id: str
    details: str
    timestamp: str


class EmailSendRequest(BaseModel):
    subject: str
    body: str
    to_email: Optional[str] = None
    cc_emails: Optional[List[str]] = None
    doc_type: Optional[str] = None
    include_price_breakup: bool = False
