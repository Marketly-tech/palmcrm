"""Documents module initialization."""
from documents.models import (
    DocumentTemplate, DocumentGenerate, GeneratedDocument,
    DocumentChecklist, CommunicationLog, ActivityLog, EmailSendRequest
)

__all__ = [
    'DocumentTemplate', 'DocumentGenerate', 'GeneratedDocument',
    'DocumentChecklist', 'CommunicationLog', 'ActivityLog', 'EmailSendRequest'
]
