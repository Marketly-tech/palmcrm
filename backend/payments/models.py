"""
Payment models for RRL CRM.
"""
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
import uuid

from utils.enums import PaymentStatus, TransactionStage


class PaymentScheduleItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    installment_name: str
    milestone: str
    amount: float
    due_date: str
    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_date: Optional[str] = None
    bank_disbursement_status: Optional[str] = None


class PaymentScheduleCreate(BaseModel):
    customer_id: str
    items: List[PaymentScheduleItem]


class PaymentSchedule(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    items: List[PaymentScheduleItem] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaymentTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    transaction_stage: TransactionStage
    transaction_date: str
    bank_name: str
    transaction_number: str
    amount: Optional[float] = 0
    notes: Optional[str] = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaymentTransactionCreate(BaseModel):
    transaction_stage: TransactionStage
    transaction_date: str
    bank_name: str
    transaction_number: str
    amount: Optional[float] = 0
    notes: Optional[str] = ""


class PriceCalculation(BaseModel):
    """Enhanced price calculation matching the Excel formula"""
    unit_number: Optional[str] = None
    unit_type: Optional[str] = None  # 2BHK, 3BHK
    floor_number: int = 0
    saleable_area: float  # sq.ft
    rate_per_sqft: float
    include_club_house: bool = True  # Rs. 2,00,000 if true
    club_house_charges: float = 200000  # Editable
    additional_charges: float = 0  # Manual additional charges
    additional_parking_count: int = 0  # Legacy field
    additional_parking_rate: float = 300000
    gst_percentage: float = 5
    labour_cess_percentage: float = 0.70


class PriceResult(BaseModel):
    # Input echo
    unit_number: Optional[str] = None
    unit_type: Optional[str] = None
    floor_number: int = 0
    saleable_area: float = 0
    rate_per_sqft: float = 0
    
    # Calculations
    base_price: float  # rate * saleable_area
    club_house_charges: float
    additional_charges: float = 0  # Manual additional charges
    additional_parking_charges: float = 0  # Legacy
    subtotal_before_taxes: float  # base + club + charges
    labour_cess: float  # 0.70% of subtotal
    gst_amount: float  # 5% of subtotal
    total_flat_value: float  # subtotal + taxes
    
    # UDS calculation
    uds: float  # saleable_area * 0.495046


class DisbursementCalculation(BaseModel):
    """For calculating disbursement amounts"""
    total_flat_value: float
    disbursement_percentage: float = 30  # Default 30%


class DisbursementResult(BaseModel):
    total_flat_value: float
    disbursement_percentage: float
    disbursement_amount: float


class PaymentTrackingResult(BaseModel):
    """Calculate payment tracking metrics"""
    total_flat_value: float
    total_received: float
    balance_amount: float
    payment_received_percentage: float
    payment_pending_percentage: float


class PaymentScheduleTemplate(BaseModel):
    """Payment schedule template from Excel"""
    installment_name: str
    percentage: float
    milestone: str


# Default payment schedule template (from Excel)
DEFAULT_PAYMENT_SCHEDULE = [
    {"installment_name": "Initial Booking Amount", "percentage": 10, "milestone": "booking", "description": "Balance booking amount (To be paid within 10 days of Booking)"},
    {"installment_name": "Post Excavation of Agreement", "percentage": 10, "milestone": "agreement", "description": "To be paid within 10 days of Booking"},
    {"installment_name": "On Completion of Foundation", "percentage": 10, "milestone": "foundation", "description": ""},
    {"installment_name": "On Completion of Podium Slab", "percentage": 10, "milestone": "podium", "description": ""},
    {"installment_name": "Upon Completion of 2nd Floor Roof Slab", "percentage": 5, "milestone": "2nd_floor", "description": ""},
    {"installment_name": "Upon Completion of 6th Floor Roof Slab", "percentage": 5, "milestone": "6th_floor", "description": ""},
    {"installment_name": "Upon Completion of 10th Floor Roof Slab", "percentage": 5, "milestone": "10th_floor", "description": ""},
    {"installment_name": "Upon Completion of 14th Floor Roof Slab", "percentage": 5, "milestone": "14th_floor", "description": ""},
    {"installment_name": "Upon Completion of 18th Floor Roof Slab", "percentage": 5, "milestone": "18th_floor", "description": ""},
    {"installment_name": "Upon Completion of 22nd Floor Roof Slab", "percentage": 5, "milestone": "22nd_floor", "description": ""},
    {"installment_name": "Upon Completion of Top Roof Slab", "percentage": 10, "milestone": "top_roof", "description": ""},
    {"installment_name": "Upon Completion of Flooring of Particular Property", "percentage": 10, "milestone": "flooring", "description": ""},
    {"installment_name": "Upon Handover or Possession of Particular Property or Registration of Absolute Sale for Particular Property, whichever is Earlier", "percentage": 10, "milestone": "handover", "description": ""},
]
