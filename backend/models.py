"""
Shared models and constants used across multiple modules.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, EmailStr, ConfigDict
import uuid

# Payment stages - construction milestones for disbursement tracking
PAYMENT_STAGES = [
    {"key": "podium", "name": "On Completion of Podium Slab", "percentage": 40, "cumulative": 40},
    {"key": "2nd_floor", "name": "Upon Completion of 2nd Floor Roof Slab", "percentage": 5, "cumulative": 45},
    {"key": "6th_floor", "name": "Upon Completion of 6th Floor Roof Slab", "percentage": 5, "cumulative": 50},
    {"key": "10th_floor", "name": "Upon Completion of 10th Floor Roof Slab", "percentage": 5, "cumulative": 55},
    {"key": "14th_floor", "name": "Upon Completion of 14th Floor Roof Slab", "percentage": 5, "cumulative": 60},
    {"key": "18th_floor", "name": "Upon Completion of 18th Floor Roof Slab", "percentage": 5, "cumulative": 65},
    {"key": "22nd_floor", "name": "Upon Completion of 22nd Floor Roof Slab", "percentage": 5, "cumulative": 70},
    {"key": "top_roof", "name": "Upon Completion of Top Roof Slab", "percentage": 10, "cumulative": 80},
    {"key": "flooring", "name": "Upon Completion of Flooring of Particular Property", "percentage": 10, "cumulative": 90},
    {"key": "handover", "name": "Upon Handover / Possession / Registration", "percentage": 10, "cumulative": 100},
]


class UnitPricing(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project: str
    tower: str
    unit_number: str
    floor: int
    bhk_type: str
    saleable_area: float
    rate_per_sqft: float
    uds: float = 0
    is_available: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UnitPricingCreate(BaseModel):
    project: str
    tower: str
    unit_number: str
    floor: int
    bhk_type: str
    saleable_area: float
    rate_per_sqft: float


class EmailSendRequest(BaseModel):
    email_type: str
    subject: str
    body: str
    recipient_email: Optional[str] = None
    cc: Optional[str] = None


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
    additional_parking: int = 0
    total_price: float = 0
    base_price: float = 0
    floor_rise_total: float = 0
    club_house_charges: float = 200000
    additional_parking_charges: float = 0
    labour_cess: float = 0
    gst_amount: float = 0
    booking_amount: float = 0
    transaction_details: Optional[str] = None
    transaction_date: Optional[str] = None
    transaction_bank: Optional[str] = None
    finance_type: str = "self"
    finance_bank: Optional[str] = None
    remarks: Optional[str] = None
