"""
Document models for RRL CRM.
"""
from typing import Optional, Dict
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
import uuid

from utils.enums import DocumentType, AgreementStatus


class DocumentTemplate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    doc_type: DocumentType
    content: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentGenerate(BaseModel):
    customer_id: str
    doc_type: DocumentType
    custom_fields: Dict[str, str] = {}


class GeneratedDocument(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    doc_type: DocumentType
    content: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_by: str
    signed_copy_url: Optional[str] = None
    status: AgreementStatus = AgreementStatus.DRAFT


class CommunicationLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    channel: str  # email, whatsapp
    message_type: str
    content: str
    status: str = "sent"
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sent_by: str


class ActivityLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    action: str
    entity_type: str
    entity_id: str
    details: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
