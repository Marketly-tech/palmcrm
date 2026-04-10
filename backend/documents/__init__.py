"""
Documents module for RRL CRM.
"""
from documents.models import (
    DocumentTemplate, DocumentGenerate, GeneratedDocument,
    CommunicationLog, ActivityLog
)
from documents.routes import router as documents_router, checklist_router, upload_router

__all__ = [
    "DocumentTemplate",
    "DocumentGenerate",
    "GeneratedDocument",
    "CommunicationLog",
    "ActivityLog",
    "documents_router",
    "checklist_router",
    "upload_router",
]
