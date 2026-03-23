"""
Customer-related models for RRL CRM.
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from utils.enums import CustomerStage, AgreementStatus, FinanceType, PaymentStatus, TransactionStage


class CustomerBase(BaseModel):
    # Personal Information
    full_name: str
    email: Optional[str] = None
    phone: str
    father_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = "male"
    nationality: Optional[str] = "Indian"
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    profession: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    address: Optional[str] = None
    
    # Co-Applicant Details
    co_applicant_name: Optional[str] = None
    co_applicant_father_name: Optional[str] = None
    co_applicant_phone: Optional[str] = None
    co_applicant_email: Optional[str] = None
    co_applicant_pan: Optional[str] = None
    co_applicant_aadhar: Optional[str] = None
    co_applicant_profession: Optional[str] = None
    co_applicant_nationality: Optional[str] = None
    co_applicant_address: Optional[str] = None
    
    # Property Details
    project: Optional[str] = None
    tower: Optional[str] = None
    unit_number: Optional[str] = None
    bhk_type: Optional[str] = None
    floor: Optional[int] = None
    saleable_area: Optional[float] = None
    uds: Optional[float] = None
    
    # Pricing
    rate_per_sqft: Optional[float] = None
    floor_rise_cost: Optional[float] = 0
    base_price: Optional[float] = None
    floor_rise_total: Optional[float] = 0
    additional_parking: int = 0
    club_house_charges: float = 200000
    additional_charges: float = 0
    additional_parking_charges: float = 0
    labour_cess: Optional[float] = None
    gst: Optional[float] = None
    total_flat_value: Optional[float] = None
    
    # Finance
    finance_type: Optional[FinanceType] = FinanceType.SELF
    bank_name: Optional[str] = None
    loan_amount: Optional[float] = None
    
    # Booking
    booking_date: Optional[str] = None
    booking_amount: Optional[float] = None
    booking_reference: Optional[str] = None
    payment_method: Optional[str] = None
    
    # Status
    stage: CustomerStage = CustomerStage.LEAD
    agreement_status: AgreementStatus = AgreementStatus.PENDING
    
    # Documents
    pan_card_url: Optional[str] = None
    aadhar_card_url: Optional[str] = None
    co_applicant_pan_url: Optional[str] = None
    co_applicant_aadhar_url: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    id: str
    customer_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None


class PaymentScheduleItem(BaseModel):
    id: str
    milestone: str
    percentage: float
    amount: float
    due_date: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING
    paid_date: Optional[str] = None
    paid_amount: Optional[float] = 0
    notes: Optional[str] = None


class PaymentScheduleCreate(BaseModel):
    customer_id: str
    items: List[PaymentScheduleItem]


class PaymentSchedule(BaseModel):
    id: str
    customer_id: str
    items: List[PaymentScheduleItem]
    created_at: Optional[str] = None


class PaymentTransaction(BaseModel):
    id: str
    customer_id: str
    stage: TransactionStage = TransactionStage.BOOKING
    transaction_date: str
    bank_name: Optional[str] = None
    transaction_number: Optional[str] = None
    amount: float
    notes: Optional[str] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None


class PaymentTransactionCreate(BaseModel):
    stage: TransactionStage = TransactionStage.BOOKING
    transaction_date: str
    bank_name: Optional[str] = None
    transaction_number: Optional[str] = None
    amount: float
    notes: Optional[str] = None


class PriceCalculation(BaseModel):
    saleable_area: float
    rate_per_sqft: float
    floor: int = 0
    floor_rise_cost: float = 0
    include_club_house: bool = True
    club_house_charges: float = 200000
    additional_charges: float = 0
    additional_parking_count: int = 0
    additional_parking_rate: float = 300000
    labour_cess_rate: float = 0.007
    gst_rate: float = 0.05


class PriceResult(BaseModel):
    saleable_area: float
    rate_per_sqft: float
    base_price: float
    floor_rise_cost: float
    floor_rise_total: float
    club_house_charges: float
    additional_charges: float = 0
    additional_parking_charges: float = 0
    subtotal: float
    labour_cess: float
    gst: float
    total_flat_value: float
    amount_in_words: str


class DisbursementCalculation(BaseModel):
    total_flat_value: float
    booking_amount: float
    agreement_percentage: float = 15


class DisbursementResult(BaseModel):
    booking_amount: float
    agreement_amount: float
    disbursement_amount: float


class PaymentTrackingResult(BaseModel):
    total_flat_value: float
    total_received: float
    balance: float
    received_percentage: float
    balance_percentage: float
