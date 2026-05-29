"""
Enums used across the RRL CRM application.
These enums match the definitions in server.py for consistency.
"""
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ACCOUNTS = "accounts"
    SALES = "sales"
    SUPPORT = "support"


class CustomerStage(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    QUALIFIED = "qualified"
    AGREEMENT_PENDING = "agreement_pending"
    AGREEMENT_DONE = "agreement_done"
    REGISTRATION_DONE = "registration_done"


class AgreementStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    COMPLETED = "completed"
    DISBURSEMENT = "disbursement"


class FinanceType(str, Enum):
    SELF = "self"
    LOAN = "loan"
    MIXED = "mixed"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIAL = "partial"


class DocumentType(str, Enum):
    SALES_AGREEMENT = "sales_agreement"
    ALLOTMENT_LETTER = "allotment_letter"
    PRICE_BREAKUP = "price_breakup"
    COST_BREAKUP = "cost_breakup"
    WELCOME_LETTER = "welcome_letter"
    DEMAND_LETTER = "demand_letter"
    PAYMENT_SCHEDULE = "payment_schedule"
    NOC_HDFC = "noc_hdfc"
    NOC_BOB = "noc_bob"
    NOC_TATA = "noc_tata"
    PAYMENT_RECEIPT = "payment_receipt"


class TransactionStage(str, Enum):
    BOOKING = "booking"
    AGREEMENT = "agreement"
    SCHEDULED_DISBURSEMENT = "scheduled_disbursement"
    TDS = "tds"
