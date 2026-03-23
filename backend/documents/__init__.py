"""
Documents module for RRL CRM.
"""
from documents.models import (
    DocumentTemplate, DocumentGenerate, GeneratedDocument,
    CommunicationLog, ActivityLog
)

__all__ = [
    "DocumentTemplate",
    "DocumentGenerate",
    "GeneratedDocument",
    "CommunicationLog",
    "ActivityLog",
]
