from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi import status as http_status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from enum import Enum
from io import BytesIO
from fastapi.responses import StreamingResponse, Response
import base64
import json

# SendGrid imports
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

# WeasyPrint for PDF generation
from weasyprint import HTML

# ==================== MODULAR IMPORTS ====================
# Importing from new modular structure
from config import settings
from database import get_database, db as module_db
from utils import number_to_indian_words as utils_number_to_indian_words
from utils import format_indian_currency as utils_format_indian_currency
from utils.enums import (
    UserRole as EnumUserRole, CustomerStage as EnumCustomerStage,
    AgreementStatus as EnumAgreementStatus, FinanceType as EnumFinanceType,
    PaymentStatus as EnumPaymentStatus, DocumentType as EnumDocumentType,
    TransactionStage as EnumTransactionStage
)

# Import modular routers
from auth import router as auth_router, admin_router as auth_admin_router, users_router
from auth import get_current_user as module_get_current_user, log_activity as module_log_activity
from auth import hash_password as module_hash_password, verify_password as module_verify_password
from auth import create_token as module_create_token, check_role as module_check_role
from customers import router as customers_router
from payments import schedule_router, transactions_router, calculator_router
from dashboard import router as dashboard_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Settings (using config.settings)
JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_EXPIRATION_HOURS = settings.JWT_EXPIRATION_HOURS

# SendGrid Settings (using config.settings)
SENDGRID_API_KEY = settings.SENDGRID_API_KEY
SENDGRID_FROM_EMAIL = settings.SENDGRID_FROM_EMAIL
SENDGRID_FROM_NAME = settings.SENDGRID_FROM_NAME

# Create the main app
app = FastAPI(title="RRL Builders CRM API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Utility function to convert number to Indian words
def number_to_indian_words(num):
    """Convert number to words in Indian format (Lakhs, Crores)"""
    if num == 0:
        return "Zero"
    
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def convert_less_than_thousand(n):
        if n == 0:
            return ""
        elif n < 20:
            return ones[n]
        elif n < 100:
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
        else:
            return ones[n // 100] + " Hundred" + (" " + convert_less_than_thousand(n % 100) if n % 100 != 0 else "")
    
    num = int(num)
    if num < 0:
        return "Minus " + number_to_indian_words(-num)
    
    crore = num // 10000000
    lakh = (num % 10000000) // 100000
    thousand = (num % 100000) // 1000
    remainder = num % 1000
    
    result = ""
    if crore > 0:
        result += convert_less_than_thousand(crore) + " Crore "
    if lakh > 0:
        result += convert_less_than_thousand(lakh) + " Lakh "
    if thousand > 0:
        result += convert_less_than_thousand(thousand) + " Thousand "
    if remainder > 0:
        result += convert_less_than_thousand(remainder)
    
    return result.strip() + " Rupees"

def format_indian_currency(amount, decimals=True):
    """Format amount in Indian currency style (e.g., 12,34,567.00 or 12,34,567)"""
    amount = float(amount) if amount else 0
    int_part = int(amount)
    
    # Format integer part with Indian comma system
    s = str(int_part)
    if len(s) > 3:
        # First group of 3, then groups of 2
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + ',' + result
            s = s[:-2]
    else:
        result = s
    
    if decimals:
        decimal_part = f"{amount:.2f}".split('.')[1]
        return f"{result}.{decimal_part}"
    return result

# Security
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== ENUMS ====================
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
    DISBURSEMENT_LETTER = "disbursement_letter"
    PRICE_BREAKUP = "price_breakup"
    WELCOME_LETTER = "welcome_letter"
    DEMAND_LETTER = "demand_letter"
    PAYMENT_SCHEDULE = "payment_schedule"

# ==================== UNIT PRICING MODEL ====================
class UnitPricing(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project: str
    tower: str
    unit_number: str
    floor: int
    bhk_type: str  # 2BHK, 3BHK
    saleable_area: float
    rate_per_sqft: float
    uds: float = 0  # Undivided Share - calculated as saleable_area * 0.495046
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

# ==================== MODELS ====================
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.SALES
    phone: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    phone: Optional[str] = None
    is_active: bool
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

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
    
    # Property Details
    project: str
    tower: str
    unit_number: str
    floor: int = 0
    bhk_type: str = ""
    saleable_area: float = 0
    uds: float = 0  # Undivided Share
    parking: Optional[str] = None
    additional_parking: int = 0  # Number of additional parking (legacy)
    
    # Pricing
    rate_per_sqft: float = 0
    base_price: float = 0  # rate * saleable_area
    club_house_charges: float = 200000  # Default 200000, editable
    infrastructure_charges: float = 0
    additional_charges: float = 0  # Manual additional charges
    additional_parking_charges: float = 0  # Legacy field
    labour_cess: float = 0  # 0.70%
    gst_percentage: float = 5
    gst_amount: float = 0
    total_price: float = 0  # Total including GST
    
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

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None

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

class DocumentTemplate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    doc_type: DocumentType
    content: str
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

class TransactionStage(str, Enum):
    BOOKING = "booking"
    AGREEMENT = "agreement"
    SCHEDULED_DISBURSEMENT = "scheduled_disbursement"

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

class DashboardStats(BaseModel):
    total_customers: int
    pending_agreements: int
    payments_due_this_week: int
    overdue_payments: int
    total_revenue: float
    total_pending: float
    total_flat_value: float
    total_balance: float
    pending_percentage: float
    monthly_revenue: List[Dict[str, Any]]
    payment_status_breakdown: Dict[str, int]

# ==================== HELPER FUNCTIONS ====================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def check_role(required_roles: List[UserRole]):
    async def role_checker(user: dict = Depends(get_current_user)):
        if UserRole(user["role"]) not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

async def log_activity(user_id: str, user_name: str, action: str, entity_type: str, entity_id: str, details: str):
    log = ActivityLog(
        user_id=user_id,
        user_name=user_name,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    doc = log.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.activity_logs.insert_one(doc)

async def generate_customer_id():
    """Generate unique customer ID using atomic counter"""
    # Use findOneAndUpdate with upsert for atomic counter increment
    result = await db.counters.find_one_and_update(
        {"_id": "customer_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return f"RRL-{str(result['seq']).zfill(5)}"

# ==================== AUTH ROUTES ====================
@api_router.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(**user_data.model_dump(exclude={"password"}))
    doc = user.model_dump()
    doc['password_hash'] = hash_password(user_data.password)
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.users.insert_one(doc)
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        phone=user.phone,
        is_active=user.is_active,
        created_at=doc['created_at']
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user.get('password_hash', '')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.get('is_active', True):
        raise HTTPException(status_code=401, detail="Account disabled")
    
    token = create_token(user['id'], user['email'], user['role'])
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user['id'],
            email=user['email'],
            name=user['name'],
            role=user['role'],
            phone=user.get('phone'),
            is_active=user.get('is_active', True),
            created_at=user['created_at']
        )
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=user['id'],
        email=user['email'],
        name=user['name'],
        role=user['role'],
        phone=user.get('phone'),
        is_active=user.get('is_active', True),
        created_at=user['created_at']
    )

# Password Reset Models
class VerifyEmailRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

@api_router.post("/auth/verify-email")
async def verify_email(data: VerifyEmailRequest):
    """Verify if email exists in the system for password reset"""
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found in our system")
    return {"exists": True, "message": "Email verified"}

@api_router.post("/auth/reset-password")
async def reset_password(data: ResetPasswordRequest):
    """Reset user password"""
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found in our system")
    
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    new_hash = hash_password(data.new_password)
    result = await db.users.update_one(
        {"email": data.email},
        {"$set": {"password_hash": new_hash}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update password")
    
    return {"message": "Password reset successfully"}

# Admin Reset User Password
class AdminResetPasswordRequest(BaseModel):
    user_id: str
    new_password: str

@api_router.post("/admin/reset-user-password")
async def admin_reset_user_password(data: AdminResetPasswordRequest, current_user: dict = Depends(get_current_user)):
    """Admin can reset any user's password"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can reset user passwords")
    
    user = await db.users.find_one({"id": data.user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    new_hash = hash_password(data.new_password)
    result = await db.users.update_one(
        {"id": data.user_id},
        {"$set": {"password_hash": new_hash}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update password")
    
    return {"message": f"Password reset successfully for {user['name']}"}

# ==================== USER MANAGEMENT ROUTES ====================
@api_router.get("/users", response_model=List[UserResponse])
async def get_users(user: dict = Depends(check_role([UserRole.ADMIN]))):
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return [UserResponse(**u) for u in users]

@api_router.put("/users/{user_id}")
async def update_user(user_id: str, updates: Dict[str, Any], user: dict = Depends(check_role([UserRole.ADMIN]))):
    if 'password' in updates:
        updates['password_hash'] = hash_password(updates.pop('password'))
    
    result = await db.users.update_one({"id": user_id}, {"$set": updates})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    await log_activity(user['id'], user['name'], "update", "user", user_id, "Updated user")
    return {"message": "User updated"}

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, user: dict = Depends(check_role([UserRole.ADMIN]))):
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    await log_activity(user['id'], user['name'], "delete", "user", user_id, "Deleted user")
    return {"message": "User deleted"}

# ==================== CUSTOMER ROUTES ====================
@api_router.post("/customers", response_model=Dict[str, Any])
async def create_customer(customer_data: CustomerCreate, user: dict = Depends(get_current_user)):
    customer = Customer(**customer_data.model_dump())
    customer.customer_id = await generate_customer_id()
    customer.created_by = user['id']
    
    doc = customer.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.customers.insert_one(doc)
    
    # Create default document checklist
    checklist = DocumentChecklist(customer_id=customer.id)
    checklist_doc = checklist.model_dump()
    checklist_doc['updated_at'] = checklist_doc['updated_at'].isoformat()
    await db.document_checklists.insert_one(checklist_doc)
    
    await log_activity(user['id'], user['name'], "create", "customer", customer.id, f"Created customer {customer.name}")
    
    return {**doc, "_id": None}

@api_router.get("/customers")
async def get_customers(
    search: Optional[str] = None,
    project: Optional[str] = None,
    agreement_status: Optional[str] = None,
    agreement_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"customer_id": {"$regex": search, "$options": "i"}},
            {"unit_number": {"$regex": search, "$options": "i"}}
        ]
    if project:
        query["project"] = project
    if agreement_status:
        query["agreement_status"] = agreement_status
    
    # Apply agreement filters
    if agreement_filter:
        today = datetime.now(timezone.utc).date()
        
        if agreement_filter == "upcoming_due":
            # Customers with due date in next 5 days (10 days from booking)
            # We'll filter in Python since we need date calculation
            pass
        elif agreement_filter == "pending_agreement":
            # Customers with draft or sent agreement status
            query["agreement_status"] = {"$in": ["draft", "sent"]}
        elif agreement_filter == "agreement_due":
            # Customers whose agreement needs signing (sent but not signed)
            query["agreement_status"] = "sent"
    
    customers = await db.customers.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit * 2 if agreement_filter == "upcoming_due" else limit)
    
    # Post-filter for upcoming_due
    if agreement_filter == "upcoming_due":
        today = datetime.now(timezone.utc).date()
        filtered_customers = []
        
        for customer in customers:
            booking_date_str = customer.get('booking_date')
            if not booking_date_str:
                continue
            try:
                if isinstance(booking_date_str, str):
                    booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
                else:
                    booking_date = booking_date_str
                
                # Due date is 10 days from booking
                due_date = booking_date + timedelta(days=10)
                days_until_due = (due_date - today).days
                
                # Include if due within next 5 days (including recently overdue up to 3 days)
                if -3 <= days_until_due <= 5:
                    customer['_due_date'] = due_date.isoformat()
                    customer['_days_until_due'] = days_until_due
                    filtered_customers.append(customer)
            except Exception:
                continue
        
        # Sort by due date (closest first)
        filtered_customers.sort(key=lambda x: x.get('_days_until_due', 999))
        customers = filtered_customers[:limit]
    
    total = await db.customers.count_documents(query) if agreement_filter != "upcoming_due" else len(customers)
    
    return {"customers": customers, "total": total}

@api_router.get("/customers/{customer_id}")
async def get_customer(customer_id: str, user: dict = Depends(get_current_user)):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@api_router.put("/customers/{customer_id}")
async def update_customer(customer_id: str, updates: Dict[str, Any], user: dict = Depends(get_current_user)):
    # Accounts role can only update agreement_status, not other customer details
    if user['role'] == 'accounts':
        allowed_fields = {'agreement_status'}
        if not set(updates.keys()).issubset(allowed_fields):
            raise HTTPException(status_code=403, detail="Accounts role can only update agreement status")
    
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    result = await db.customers.update_one({"id": customer_id}, {"$set": updates})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    await log_activity(user['id'], user['name'], "update", "customer", customer_id, "Updated customer")
    return {"message": "Customer updated"}

@api_router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str, user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Clean up related data
    await db.payment_schedules.delete_many({"customer_id": customer_id})
    await db.document_checklists.delete_one({"customer_id": customer_id})
    await db.generated_documents.delete_many({"customer_id": customer_id})
    await db.communication_logs.delete_many({"customer_id": customer_id})
    
    await log_activity(user['id'], user['name'], "delete", "customer", customer_id, "Deleted customer")
    return {"message": "Customer deleted"}

# ==================== PAYMENT SCHEDULE ROUTES ====================
@api_router.post("/payments/schedule")
async def create_payment_schedule(data: PaymentScheduleCreate, user: dict = Depends(get_current_user)):
    existing = await db.payment_schedules.find_one({"customer_id": data.customer_id}, {"_id": 0})
    
    schedule_doc = {
        "id": existing['id'] if existing else str(uuid.uuid4()),
        "customer_id": data.customer_id,
        "items": [item.model_dump() for item in data.items],
        "created_at": existing['created_at'] if existing else datetime.now(timezone.utc).isoformat()
    }
    
    if existing:
        await db.payment_schedules.update_one({"customer_id": data.customer_id}, {"$set": schedule_doc})
    else:
        await db.payment_schedules.insert_one(schedule_doc)
    
    await log_activity(user['id'], user['name'], "update", "payment_schedule", data.customer_id, "Updated payment schedule")
    return {"message": "Payment schedule saved", "schedule": schedule_doc}

@api_router.get("/payments/schedule/{customer_id}")
async def get_payment_schedule(customer_id: str, user: dict = Depends(get_current_user)):
    schedule = await db.payment_schedules.find_one({"customer_id": customer_id}, {"_id": 0})
    if not schedule:
        return {"customer_id": customer_id, "items": []}
    return schedule

@api_router.put("/payments/item/{customer_id}/{item_id}")
async def update_payment_item(customer_id: str, item_id: str, updates: Dict[str, Any], user: dict = Depends(get_current_user)):
    schedule = await db.payment_schedules.find_one({"customer_id": customer_id}, {"_id": 0})
    if not schedule:
        raise HTTPException(status_code=404, detail="Payment schedule not found")
    
    for item in schedule['items']:
        if item['id'] == item_id:
            item.update(updates)
            break
    
    await db.payment_schedules.update_one({"customer_id": customer_id}, {"$set": {"items": schedule['items']}})
    
    # Auto-calculate total_received based on paid items
    total_received = 0
    for item in schedule['items']:
        if item.get('payment_status') == 'paid':
            total_received += item.get('amount', 0)
        elif item.get('payment_status') == 'partial':
            # For partial payments, count 50% of the amount (or you can add a partial_amount field later)
            total_received += item.get('amount', 0) * 0.5
    
    # Get customer's total price to calculate percentages
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0, "total_price": 1})
    total_price = customer.get('total_price', 0) if customer else 0
    
    # Calculate payment percentages
    payment_received_percentage = round((total_received / total_price * 100), 2) if total_price > 0 else 0
    payment_pending_percentage = round(100 - payment_received_percentage, 2)
    balance_amount = round(total_price - total_received, 2)
    
    # Update customer's payment tracking fields
    await db.customers.update_one(
        {"id": customer_id},
        {"$set": {
            "total_received": round(total_received, 2),
            "balance_amount": balance_amount,
            "payment_received_percentage": payment_received_percentage,
            "payment_pending_percentage": payment_pending_percentage,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    await log_activity(user['id'], user['name'], "update", "payment_item", item_id, f"Updated payment status - Total Received: {total_received}")
    
    # Return updated payment tracking info
    return {
        "message": "Payment item updated",
        "total_received": round(total_received, 2),
        "balance_amount": balance_amount,
        "payment_received_percentage": payment_received_percentage,
        "payment_pending_percentage": payment_pending_percentage
    }

@api_router.get("/payments/overview")
async def get_payments_overview(user: dict = Depends(get_current_user)):
    today = datetime.now(timezone.utc).date()
    week_end = today + timedelta(days=7)
    
    schedules = await db.payment_schedules.find({}, {"_id": 0}).to_list(1000)
    
    # Fix N+1 query: Fetch all relevant customers in one query
    customer_ids = list(set(s.get('customer_id') for s in schedules if s.get('customer_id')))
    customers_list = await db.customers.find(
        {"id": {"$in": customer_ids}}, 
        {"_id": 0, "id": 1, "name": 1, "customer_id": 1, "unit_number": 1}
    ).to_list(1000)
    customers_dict = {c['id']: c for c in customers_list}
    
    pending = []
    overdue = []
    upcoming = []
    
    for schedule in schedules:
        customer = customers_dict.get(schedule.get('customer_id'))
        for item in schedule.get('items', []):
            if item['payment_status'] == 'paid':
                continue
            
            try:
                due_date = datetime.strptime(item['due_date'], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue
            
            item_data = {**item, "customer_name": customer.get('name', 'N/A') if customer else 'N/A', 
                        "customer_ref": customer.get('customer_id', '') if customer else '',
                        "unit_number": customer.get('unit_number', '') if customer else ''}
            
            if due_date < today:
                overdue.append(item_data)
            elif due_date <= week_end:
                upcoming.append(item_data)
            else:
                pending.append(item_data)
    
    return {"pending": pending, "overdue": overdue, "upcoming": upcoming}

# ==================== PAYMENT TRANSACTIONS ====================
@api_router.get("/transactions/{customer_id}")
async def get_transactions(customer_id: str, user: dict = Depends(get_current_user)):
    """Get all transactions for a customer"""
    transactions = await db.payment_transactions.find(
        {"customer_id": customer_id}, {"_id": 0}
    ).sort("transaction_date", -1).to_list(1000)
    return transactions

@api_router.post("/transactions/{customer_id}")
async def create_transaction(customer_id: str, transaction: PaymentTransactionCreate, user: dict = Depends(get_current_user)):
    """Create a new transaction"""
    # Verify customer exists - check both id and customer_id fields
    customer = await db.customers.find_one({"$or": [{"id": customer_id}, {"customer_id": customer_id}]})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    new_transaction = PaymentTransaction(
        customer_id=customer_id,
        transaction_stage=transaction.transaction_stage,
        transaction_date=transaction.transaction_date,
        bank_name=transaction.bank_name,
        transaction_number=transaction.transaction_number,
        amount=transaction.amount,
        notes=transaction.notes
    )
    
    await db.payment_transactions.insert_one(new_transaction.model_dump())
    
    # Update customer's total_received and balance_amount
    all_transactions = await db.payment_transactions.find({"customer_id": customer_id}, {"_id": 0, "amount": 1}).to_list(1000)
    total_received = sum(t.get('amount', 0) or 0 for t in all_transactions)
    total_price = customer.get('total_price', 0) or 0
    balance_amount = total_price - total_received
    
    await db.customers.update_one(
        {"$or": [{"id": customer_id}, {"customer_id": customer_id}]},
        {"$set": {
            "total_received": total_received,
            "balance_amount": balance_amount,
            "payment_received_percentage": round((total_received / total_price) * 100, 2) if total_price > 0 else 0,
            "payment_pending_percentage": round((balance_amount / total_price) * 100, 2) if total_price > 0 else 100
        }}
    )
    
    await log_activity(user['id'], user['name'], "create", "transaction", new_transaction.id, f"Created transaction for customer {customer_id}")
    
    return {"message": "Transaction created", "transaction": new_transaction.model_dump()}

@api_router.put("/transactions/{customer_id}/{transaction_id}")
async def update_transaction(customer_id: str, transaction_id: str, transaction: PaymentTransactionCreate, user: dict = Depends(get_current_user)):
    """Update an existing transaction"""
    existing = await db.payment_transactions.find_one({"id": transaction_id, "customer_id": customer_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    update_data = {
        "transaction_stage": transaction.transaction_stage.value if hasattr(transaction.transaction_stage, 'value') else transaction.transaction_stage,
        "transaction_date": transaction.transaction_date,
        "bank_name": transaction.bank_name,
        "transaction_number": transaction.transaction_number,
        "amount": transaction.amount,
        "notes": transaction.notes,
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.payment_transactions.update_one(
        {"id": transaction_id},
        {"$set": update_data}
    )
    
    # Update customer's total_received and balance_amount
    customer = await db.customers.find_one({"$or": [{"id": customer_id}, {"customer_id": customer_id}]})
    if customer:
        all_transactions = await db.payment_transactions.find({"customer_id": customer_id}, {"_id": 0, "amount": 1}).to_list(1000)
        total_received = sum(t.get('amount', 0) or 0 for t in all_transactions)
        total_price = customer.get('total_price', 0) or 0
        balance_amount = total_price - total_received
        
        await db.customers.update_one(
            {"$or": [{"id": customer_id}, {"customer_id": customer_id}]},
            {"$set": {
                "total_received": total_received,
                "balance_amount": balance_amount,
                "payment_received_percentage": round((total_received / total_price) * 100, 2) if total_price > 0 else 0,
                "payment_pending_percentage": round((balance_amount / total_price) * 100, 2) if total_price > 0 else 100
            }}
        )
    
    await log_activity(user['id'], user['name'], "update", "transaction", transaction_id, f"Updated transaction for customer {customer_id}")
    
    return {"message": "Transaction updated"}

@api_router.delete("/transactions/{customer_id}/{transaction_id}")
async def delete_transaction(customer_id: str, transaction_id: str, user: dict = Depends(get_current_user)):
    """Delete a transaction - restricted for accounts role"""
    # Accounts role cannot delete transactions
    if user['role'] == 'accounts':
        raise HTTPException(status_code=403, detail="Accounts role cannot delete transactions")
    
    result = await db.payment_transactions.delete_one({"id": transaction_id, "customer_id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update customer's total_received and balance_amount
    customer = await db.customers.find_one({"$or": [{"id": customer_id}, {"customer_id": customer_id}]})
    if customer:
        all_transactions = await db.payment_transactions.find({"customer_id": customer_id}, {"_id": 0, "amount": 1}).to_list(1000)
        total_received = sum(t.get('amount', 0) or 0 for t in all_transactions)
        total_price = customer.get('total_price', 0) or 0
        balance_amount = total_price - total_received
        
        await db.customers.update_one(
            {"$or": [{"id": customer_id}, {"customer_id": customer_id}]},
            {"$set": {
                "total_received": total_received,
                "balance_amount": balance_amount,
                "payment_received_percentage": round((total_received / total_price) * 100, 2) if total_price > 0 else 0,
                "payment_pending_percentage": round((balance_amount / total_price) * 100, 2) if total_price > 0 else 100
            }}
        )
    
    await log_activity(user['id'], user['name'], "delete", "transaction", transaction_id, f"Deleted transaction for customer {customer_id}")
    
    return {"message": "Transaction deleted"}

# ==================== PRICE CALCULATOR ====================
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

@api_router.post("/calculator/price", response_model=PriceResult)
async def calculate_price(data: PriceCalculation):
    """
    Calculate total flat value with all charges
    Formula: (Rate/sqft × Saleable Area) + Club House + Additional Charges + Labour Cess + GST
    """
    # Base price = Rate × Saleable Area
    base_price = data.rate_per_sqft * data.saleable_area
    
    # Club house charges (editable, default Rs. 2,00,000)
    club_house = data.club_house_charges if data.include_club_house else 0
    
    # Additional manual charges
    additional_charges = data.additional_charges or 0
    
    # Subtotal before taxes
    subtotal = base_price + club_house + additional_charges
    
    # Labour cess (0.70% of subtotal)
    labour_cess = subtotal * (data.labour_cess_percentage / 100)
    
    # GST (5% of subtotal)
    gst_amount = subtotal * (data.gst_percentage / 100)
    
    # Total flat value
    total_flat_value = subtotal + labour_cess + gst_amount
    
    # UDS calculation
    uds = data.saleable_area * 0.495046
    
    return PriceResult(
        unit_number=data.unit_number,
        unit_type=data.unit_type,
        floor_number=data.floor_number,
        saleable_area=data.saleable_area,
        rate_per_sqft=data.rate_per_sqft,
        base_price=round(base_price, 2),
        club_house_charges=round(club_house, 2),
        additional_charges=round(additional_charges, 2),
        subtotal_before_taxes=round(subtotal, 2),
        labour_cess=round(labour_cess, 2),
        gst_amount=round(gst_amount, 2),
        total_flat_value=round(total_flat_value, 2),
        uds=round(uds, 2)
    )

@api_router.post("/calculator/disbursement", response_model=DisbursementResult)
async def calculate_disbursement(data: DisbursementCalculation):
    """
    Calculate disbursement amount
    Formula: Total Flat Value × Disbursement Percentage
    """
    disbursement_amount = data.total_flat_value * (data.disbursement_percentage / 100)
    
    return DisbursementResult(
        total_flat_value=round(data.total_flat_value, 2),
        disbursement_percentage=data.disbursement_percentage,
        disbursement_amount=round(disbursement_amount, 2)
    )

@api_router.post("/calculator/payment-tracking", response_model=PaymentTrackingResult)
async def calculate_payment_tracking(total_flat_value: float, total_received: float):
    """
    Calculate payment tracking metrics
    - Balance = Total - Received
    - Received % = (Received / Total) × 100
    - Pending % = 100 - Received %
    """
    balance = total_flat_value - total_received
    received_percentage = (total_received / total_flat_value * 100) if total_flat_value > 0 else 0
    pending_percentage = 100 - received_percentage
    
    return PaymentTrackingResult(
        total_flat_value=round(total_flat_value, 2),
        total_received=round(total_received, 2),
        balance_amount=round(balance, 2),
        payment_received_percentage=round(received_percentage, 2),
        payment_pending_percentage=round(pending_percentage, 2)
    )

@api_router.get("/calculator/payment-schedule-template")
async def get_payment_schedule_template(total_amount: float = 0):
    """Get the default payment schedule template with calculated amounts"""
    schedule = []
    cumulative = 0
    for item in DEFAULT_PAYMENT_SCHEDULE:
        amount = total_amount * (item["percentage"] / 100) if total_amount > 0 else 0
        cumulative += amount
        schedule.append({
            **item,
            "amount": round(amount, 2),
            "cumulative": round(cumulative, 2)
        })
    return schedule

@api_router.post("/calculator/generate-schedule/{customer_id}")
async def generate_payment_schedule_for_customer(customer_id: str, user: dict = Depends(get_current_user)):
    """Auto-generate payment schedule based on customer's total price"""
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    total_amount = customer.get("total_price", 0)
    if total_amount <= 0:
        raise HTTPException(status_code=400, detail="Customer has no total price set")
    
    items = []
    cumulative = 0
    for item in DEFAULT_PAYMENT_SCHEDULE:
        amount = total_amount * (item["percentage"] / 100)
        cumulative += amount
        items.append({
            "id": str(uuid.uuid4()),
            "installment_name": item["installment_name"],
            "milestone": item["milestone"],
            "description": item.get("description", ""),
            "percentage": item["percentage"],
            "amount": round(amount, 2),
            "cumulative": round(cumulative, 2),
            "due_date": "",
            "payment_status": "pending",
            "payment_date": None
        })
    
    schedule_doc = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "items": items,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Upsert the schedule
    await db.payment_schedules.update_one(
        {"customer_id": customer_id},
        {"$set": schedule_doc},
        upsert=True
    )
    
    await log_activity(user['id'], user['name'], "generate", "payment_schedule", customer_id, "Auto-generated payment schedule")
    
    return {"message": "Payment schedule generated", "schedule": schedule_doc}

# ==================== DOCUMENT TEMPLATES ====================
@api_router.get("/templates")
async def get_templates(user: dict = Depends(get_current_user)):
    templates = await db.document_templates.find({}, {"_id": 0}).to_list(100)
    return templates

@api_router.post("/templates")
async def create_template(template: DocumentTemplate, user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    doc = template.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.document_templates.insert_one(doc)
    await log_activity(user['id'], user['name'], "create", "template", template.id, f"Created template {template.name}")
    return {"message": "Template created", "id": template.id}

@api_router.put("/templates/{template_id}")
async def update_template(template_id: str, updates: Dict[str, Any], user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    updates['updated_at'] = datetime.now(timezone.utc).isoformat()
    result = await db.document_templates.update_one({"id": template_id}, {"$set": updates})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await log_activity(user['id'], user['name'], "update", "template", template_id, "Updated template")
    return {"message": "Template updated"}

# ==================== DOCUMENT GENERATION ====================
@api_router.post("/documents/generate")
async def generate_document(data: DocumentGenerate, user: dict = Depends(get_current_user)):
    customer = await db.customers.find_one({"id": data.customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # For Sales Agreement, use the dedicated generator function
    if data.doc_type == DocumentType.SALES_AGREEMENT:
        # Get payment schedule
        schedule = await db.payment_schedules.find_one({"customer_id": data.customer_id}, {"_id": 0})
        schedule_items = schedule.get('items', []) if schedule else []
        
        # Get transaction records
        transactions = await db.payment_transactions.find(
            {"customer_id": data.customer_id}, {"_id": 0}
        ).sort("transaction_date", 1).to_list(1000)
        
        content = generate_sales_agreement_html(customer, schedule_items, transactions)
    elif data.doc_type == DocumentType.PRICE_BREAKUP:
        content = generate_price_breakup_html(customer)
    elif data.doc_type == DocumentType.ALLOTMENT_LETTER:
        content = generate_allotment_letter_html(customer)
    elif data.doc_type == DocumentType.PAYMENT_SCHEDULE:
        # Get transaction records for payment schedule
        transactions = await db.payment_transactions.find(
            {"customer_id": data.customer_id}, {"_id": 0}
        ).sort("transaction_date", 1).to_list(1000)
        content = generate_payment_schedule_pdf_html(customer, transactions)
    else:
        # For other document types, use template-based generation
        template = await db.document_templates.find_one({"doc_type": data.doc_type.value}, {"_id": 0})
        if not template:
            template = {"content": get_default_template(data.doc_type)}
        
        content = template['content']
        
        # Format total price with Indian currency format
        total_price = customer.get('total_price', 0)
        total_price_formatted = format_indian_currency(total_price, decimals=False) if total_price else "0"
        
        # Calculate UDS if not present
        uds = customer.get('uds', 0)
        if not uds and customer.get('saleable_area'):
            uds = round(customer.get('saleable_area', 0) * 0.495046, 2)
        
        placeholders = {
            "{customer_name}": customer.get('name', ''),
            "{customer_id}": customer.get('customer_id', ''),
            "{unit_number}": customer.get('unit_number', ''),
            "{tower}": customer.get('tower', ''),
            "{project}": customer.get('project', ''),
            "{total_price}": str(total_price),
            "{total_price_formatted}": total_price_formatted,
            "{saleable_area}": str(customer.get('saleable_area', 0)),
            "{uds}": str(uds),
            "{booking_amount}": str(customer.get('booking_amount', 0)),
            "{booking_date}": customer.get('booking_date', ''),
            "{date}": datetime.now().strftime("%d-%m-%Y"),
            "{father_name}": customer.get('father_name', ''),
            "{pan_number}": customer.get('pan_number', ''),
            "{phone}": customer.get('phone', ''),
            "{email}": customer.get('email', ''),
            "{address}": customer.get('address', ''),
            "{bhk_type}": customer.get('bhk_type', ''),
            "{floor}": str(customer.get('floor', '')),
            "{rate_per_sqft}": str(customer.get('rate_per_sqft', 0)),
            "{base_price}": str(customer.get('base_price', 0)),
            "{gst_amount}": str(customer.get('gst_amount', 0)),
            "{labour_cess}": str(customer.get('labour_cess', 0)),
            "{club_house_charges}": str(customer.get('club_house_charges', 0)),
        }
        
        # Add custom fields
        for key, value in data.custom_fields.items():
            placeholders[f"{{{key}}}"] = value
        
        for placeholder, value in placeholders.items():
            content = content.replace(placeholder, str(value))
    
    # Save generated document
    gen_doc = GeneratedDocument(
        customer_id=data.customer_id,
        doc_type=data.doc_type,
        content=content,
        generated_by=user['id']
    )
    
    doc = gen_doc.model_dump()
    doc['generated_at'] = doc['generated_at'].isoformat()
    await db.generated_documents.insert_one(doc)
    
    await log_activity(user['id'], user['name'], "generate", "document", gen_doc.id, f"Generated {data.doc_type.value}")
    
    return {"message": "Document generated", "document": {**doc, "_id": None}}

def generate_sales_agreement_template():
    """Generate Sales Agreement HTML template with black and gold theme - Full 23 Page Version"""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        @page {
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
        }
        
        body {
            font-family: 'Roboto', serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1A1A1A;
            background: #fff;
            padding: 15px 25px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #D4AF37;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo {
            width: 50px;
            height: 50px;
            background: #1A1A1A;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #D4AF37;
            font-weight: bold;
            font-size: 18px;
        }
        
        .company-name {
            font-size: 16px;
            font-weight: 700;
            color: #1A1A1A;
        }
        
        .company-tagline {
            font-size: 9px;
            color: #666;
        }
        
        h1.main-title {
            text-align: center;
            font-size: 18px;
            font-weight: 700;
            color: #1A1A1A;
            margin: 25px 0;
            text-decoration: underline;
            text-transform: uppercase;
        }
        
        .section-title {
            font-weight: 700;
            color: #1A1A1A;
            font-size: 12pt;
            margin: 20px 0 12px 0;
            padding: 8px 12px;
            background: #f5f5f5;
            border-left: 4px solid #D4AF37;
            text-transform: uppercase;
        }
        
        .sub-section-title {
            font-weight: 600;
            color: #1A1A1A;
            font-size: 11pt;
            margin: 15px 0 10px 0;
            text-decoration: underline;
        }
        
        .highlight {
            color: #D4AF37;
            font-weight: 600;
        }
        
        .content p {
            margin: 10px 0;
            text-align: justify;
        }
        
        .party-section {
            margin: 15px 0;
            padding: 15px;
            background: #fafafa;
            border-left: 4px solid #D4AF37;
        }
        
        .party-section p {
            margin: 5px 0;
        }
        
        .party-title {
            font-weight: 700;
            color: #1A1A1A;
            margin-bottom: 10px;
        }
        
        table.details {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        table.details th, table.details td {
            border: 1px solid #D4AF37;
            padding: 8px 10px;
            text-align: left;
            font-size: 10pt;
        }
        
        table.details th {
            background: #1A1A1A;
            color: #D4AF37;
            font-weight: 500;
            width: 40%;
        }
        
        table.details td {
            background: #fafafa;
        }
        
        table.schedule {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 9pt;
        }
        
        table.schedule th, table.schedule td {
            border: 1px solid #D4AF37;
            padding: 6px 8px;
            text-align: left;
        }
        
        table.schedule th {
            background: #1A1A1A;
            color: #D4AF37;
            font-weight: 500;
        }
        
        table.schedule tr:nth-child(even) {
            background: #fafafa;
        }
        
        table.schedule .amount {
            text-align: right;
            font-family: 'Roboto Mono', monospace;
        }
        
        .clause {
            margin: 12px 0;
            text-align: justify;
        }
        
        .clause-number {
            font-weight: 700;
            color: #D4AF37;
        }
        
        .sub-clause {
            margin: 8px 0 8px 25px;
            text-align: justify;
        }
        
        .roman-list {
            margin-left: 25px;
        }
        
        .roman-list li {
            margin: 8px 0;
            text-align: justify;
        }
        
        .signature-section {
            margin-top: 40px;
            page-break-inside: avoid;
        }
        
        .signature-row {
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
        }
        
        .signature-box {
            width: 45%;
            text-align: center;
        }
        
        .signature-line {
            border-top: 1px solid #1A1A1A;
            margin-top: 80px;
            padding-top: 10px;
        }
        
        .schedule-section {
            page-break-before: always;
            margin-top: 20px;
        }
        
        .schedule-header {
            background: #1A1A1A;
            color: #D4AF37;
            padding: 12px 15px;
            font-weight: 700;
            font-size: 14pt;
            text-align: center;
            margin-bottom: 15px;
        }
        
        .boundary-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        .boundary-table th, .boundary-table td {
            border: 1px solid #D4AF37;
            padding: 10px;
            font-size: 10pt;
        }
        
        .boundary-table th {
            background: #f5f5f5;
            width: 30%;
            text-align: left;
        }
        
        .specs-list {
            margin: 10px 0 10px 25px;
        }
        
        .specs-list li {
            margin: 6px 0;
        }
        
        .amenities-list {
            margin: 10px 0 10px 25px;
            columns: 2;
        }
        
        .amenities-list li {
            margin: 5px 0;
        }
        
        .witness-section {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #D4AF37;
        }
        
        .footer {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 2px solid #D4AF37;
            text-align: center;
            font-size: 9pt;
            color: #666;
        }
        
        .page-break {
            page-break-after: always;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-section">
            <div class="logo">RRL</div>
            <div>
                <div class="company-name">RRL Builders and Developers</div>
                <div class="company-tagline">Beyond homes. A lifestyle</div>
            </div>
        </div>
    </div>
    
    <h1 class="main-title">Agreement for Sale</h1>
    
    <div class="content">
        <p>This <strong>Agreement For Sale</strong> is made and entered into on this <span class="highlight">{agreement_date_text}</span> at Bengaluru.</p>
        
        <p style="text-align: center; font-weight: 700; margin: 20px 0;">BETWEEN:</p>
        
        <!-- OWNER PARTIES -->
        <div class="party-section">
            <p class="party-title">1. MRS. MUNITHAYAMMA</p>
            <p>Aged about 60 years, W/o Late Narayana Reddy</p>
            <p>Residing at: Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District - 560087</p>
            <p>AADHAAR No: 504904154718 | PAN No.: CFDPM2534P</p>
        </div>
        
        <div class="party-section">
            <p class="party-title">2. MRS. YESHASWINI N</p>
            <p>Aged about 36 years, D/o Late Narayana Reddy</p>
            <p>Residing at: Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District - 560087</p>
            <p>AADHAAR No: 661099599743 | PAN No.: AUCPY4059M</p>
        </div>
        
        <div class="party-section">
            <p class="party-title">3. MAST. HRUTHVIK REDDY S</p>
            <p>Aged about 4 years, S/o Yeshaswini N</p>
            <p>Residing at: Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District - 560087</p>
            <p>AADHAAR No: 318812583405 | PAN No.: NA</p>
            <p>Represented by his natural guardian, mother MRS. YESHASWINI N</p>
        </div>
        
        <div class="party-section">
            <p class="party-title">4. MS. TEJASWINI N</p>
            <p>Aged about 27 years, D/o Late Narayana Reddy</p>
            <p>Residing at: Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District - 560087</p>
            <p>AADHAAR No: 358161939490 | PAN No.: BIOPT0038E</p>
        </div>
        
        <p style="margin: 15px 0;"><strong>All are represented by the General Power of Attorney Holder:</strong></p>
        
        <div class="party-section">
            <p class="party-title">M/s. RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</p>
            <p>A Private Limited Company having its registered office at:</p>
            <p>4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru – 562125</p>
            <p>PAN No. AAKCR4125J</p>
            <p style="margin-top: 10px;"><strong>Represented by its Managing Director,</strong></p>
            <p style="margin-left: 20px;"><strong>MR. RAM R</strong></p>
            <p style="margin-left: 20px;">Aged about 36 years</p>
            <p style="margin-left: 20px;">S/o C Rajareddy</p>
            <p style="margin-left: 20px;">Residing at: #23/1, Sarjapura Road, Sompura Gate, Vinayaka Nagar, Sompura, Bengaluru, Karnataka - 562125</p>
            <p style="margin-left: 20px;">AADHAAR No: 457278356452</p>
            <p style="margin-left: 20px;">PAN No.: BELPR1909B</p>
        </div>
        
        <p>Hereinafter referred to as the <strong>'OWNER'</strong> (which expression unless repugnant to the context shall mean and include his heirs, legal representatives, administrators, executors, successors and assigns); and</p>
        
        <div class="party-section">
            <p class="party-title">5. M/s. RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</p>
            <p>A Private Limited Company having its registered office at:</p>
            <p>4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru – 562125</p>
            <p>PAN No. AAKCR4125J</p>
            <p style="margin-top: 10px;"><strong>Represented by its Managing Director,</strong></p>
            <p style="margin-left: 20px;"><strong>MR. RAM R</strong></p>
            <p style="margin-left: 20px;">Aged about 36 years</p>
            <p style="margin-left: 20px;">S/o C. Rajareddy</p>
            <p style="margin-left: 20px;">Residing at: #23/1, Sarjapura Road, Sompura Gate, Vinayaka Nagar, Sompura, Bengaluru, Karnataka - 562125</p>
            <p style="margin-left: 20px;">AADHAAR No: 457278356452</p>
            <p style="margin-left: 20px;">PAN No.: BELPR1909B</p>
        </div>
        
        <p>Hereinafter referred to as the <strong>'BUILDER'</strong> (which expression unless repugnant to the context shall mean and include his successors in office and assigns)</p>
        
        <p style="margin: 15px 0;">Both 'Owner' and 'Builder' are collectively hereinafter referred to as the <strong>'VENDORS'</strong> and together forming ONE Part.</p>
        
        <p style="text-align: center; font-weight: 700; margin: 20px 0;">AND</p>
        
        <!-- PURCHASER SECTION -->
        <div class="party-section">
            <p class="party-title">PURCHASER:</p>
            <p><strong><span class="highlight">{customer_name}</span></strong></p>
            <p>Aged about <span class="highlight">{age}</span> years, {salutation} <span class="highlight">{father_name}</span></p>
            <p>Residing at: <span class="highlight">{address}</span></p>
            <p>AADHAAR No.: <span class="highlight">{aadhaar_number}</span> | PAN No.: <span class="highlight">{pan_number}</span> | Mobile: <span class="highlight">{phone}</span></p>
        </div>
        
        <p>Hereinafter referred to as the <strong>PURCHASER/S / ALLOTTEE/S</strong> (which expression unless repugnant to the context shall mean and include his/her/their legal heirs, representatives, administrators, executors, successors and assigns) of the OTHER Part.</p>
        
        <p style="margin: 15px 0;">As the context may require the PURCHASER/S and VENDORS are sometimes hereinafter collectively referred to as the "Parties" and severally as a "Party".</p>
        
        <p style="text-align: center; font-weight: 700; margin: 25px 0; font-size: 12pt;">NOW THIS AGREEMENT FOR SALE WITNESSETH AS FOLLOWS:</p>
        
        <!-- SECTION I: FLOW OF TITLE -->
        <div class="section-title">I. FLOW OF TITLE</div>
        
        <p class="clause">WHEREAS the OWNERS represent that they are the absolute owners of agricultural land bearing Sy. No. 73/6 (Old Sy. No. 73/5 and Old Old Sy. No. 73) to an extent of 1 Acre 38 Guntas, situated at Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, morefully described in the schedule hereunder mentioned and herein after referred to as the "Schedule Property".</p>
        
        <p class="clause">Whereas the larger extent of agricultural land measuring 03 – 36 (Acres – Guntas), situated at Sy. No. 73, Jantagondanahalli Village, Sarjapura Hobli, Anekal taluk, Bengaluru Urban District, originally belonged to one Mr. Late Gurappa S/o Nanjappa. Thereafter, one Mr. Late Narayana Reddy @ Narayana @ Narayanappa S/o Mr. Late Gurappa and Nanjappa @ Nanja Reddy S/o Late Gurappa has been in joint possession and enjoyment of larger extent of agricultural land measuring 03 – 36 (Acres – Guntas), in Sy. No. 73, situated at Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District.</p>
        
        <p class="clause">Thereafter, Mr. Late Narayana Reddy @ Narayana @ Narayanappa, S/o Mr. Late Gurappa, more specifically has been in enjoyment and possession of 02 – 1 ½ (Acres – Guntas) in Sy. No. 73, situated at Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, by way of family arrangement.</p>
        
        <p class="clause">Thereafter, on demise of Mr. Late Narayana Reddy @ Narayana @ Narayanappa, S/o Mr. Late Gurappa, his wife Mrs. T. Munithayamma is in enjoyment and possession of agricultural land to the extent of 02 – 1 ½ (Acres – Guntas) in Sy. No. 73, situated at Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District.</p>
        
        <p class="clause">Thereafter, a suit for partition bearing OS No. 82/2004 on file of Hon'ble Principal Civil Judge (Sr. Div.), Bengaluru Rural District, Bengaluru was filed by one of the ancestors of Mr. Late Gurappa S/o Nanjappa. Thereafter, upon arrival of compromise amongst parties, the aforesaid suit was decreed on 02-06-2004 in accordance with the compromise petition filed before the court aforesaid.</p>
        
        <p class="clause">In view of the same, the Schedule Property was allotted to the share of Mrs. Munithayamma, Baby Yashaswini and Baby Thejaswini, by virtue of a Decree drawn and registered in the Office of Sub-Registrar, Anekal, Bengaluru, vide Document No. ANK-1-08680-2004-05 dated 05-08-2004. Thereafter, the records were mutated in the name of Mrs. T. Munithayamma.</p>
        
        <p class="clause">Thereafter, Mrs. T. Munithayamma, Mrs. Yeshaswini N, Master Hruthvik Reddy and Ms. Tejaswini N, have entered into a Memorandum of Understanding with M/s. RRL Builders and Developers Private Limited for development of Schedule Property herein below mentioned, registered in the office of the Sub-Registrar, Sarjapura, Bengaluru, vide Document No. SRJ-1-03312-2023-24 dated 26-07-2023.</p>
        
        <p class="clause">Thereafter, Mrs. T. Munithayamma, Mrs. Yeshaswini N, Master Hruthvik Reddy S represented by his natural guardian mother, and Ms. Tejaswini N have executed a Joint Development Agreement with M/s. RRL Builders and Developers Private Limited, represented by its Managing Director, Mr. Ram R, for development of the Schedule Property into a Residential Apartment Building and has agreed to the share of saleable development area in the ratio of 33:67, and the same is registered as Document No. SRJ-1-07944-2024-25 dated 29-11-2024, registered in the office of the Sub-Registrar, Sarjapura, Bengaluru.</p>
        
        <p class="clause">Thereafter, Mrs. T. Munithayamma, Mrs. Yeshaswini N, Master Hruthvik Reddy S represented by his natural guardian mother, and Ms. Tejaswini N have also executed a Power of Attorney (pursuant to the Joint Development Agreement dated 27-11-2025) in favour of M/s. RRL Builders and Developers Private Limited, represented by its Managing Director, Mr. Ram R, to do such acts, including to sell the flats falling into the share of M/s. RRL Builders and Developers Private Limited, amongst others, and the same is registered as Document No. SRJ-4-00669-2024-25 dated 29-11-2024, registered in the office of the Sub-Registrar, Sarjapura, Bengaluru.</p>
        
        <p class="clause">Thereafter, Mrs. T. Munithayamma has applied for 'Change of Land Use' from 'agricultural' to 'residential' purpose. On 02-01-2025, the Member-Secretary and Joint Director of City and Town Planning Authority, Anekal Planning Authority, vide its letter bearing No. APA/L.C/10/2023-24, has permitted for 'Change of Land Use' as above.</p>
        
        <p class="clause">Thereafter, Mrs. T. Munithayamma has applied for a deemed conversion of land from agricultural to residential purpose and the Office of the Deputy Commissioner, Bengaluru, has issued an official memorandum bearing No. 741998 dated 12-02-2025 by approving conversion of agricultural land in Sy. No. 73/6 (Old Sy. No. 73/5 and Old Old Sy. No. 73) measuring 1 Acre 38 Guntas, situated at Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, as above.</p>
        
        <p class="clause">Thereafter, E-Katha bearing No. 73/6, PID No. 150200101600120805, has been issued by Neriga Gram Panchayat, w.r.t. land measuring a total extent of 7,891.37 Sq. Mts., situated on Sy. 73/6 Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, and the same stands in the name of Mrs. T. Munithayamma and she has paid property tax for the period.</p>
        
        <p class="clause">Office of the Neriga Gram Panchayat, Sarjapura Hobli, Anekal taluk, Bengaluru Urban District, vide its letter bearing No. GP/CR/73/24-25 has issued 'No Objection Certificate' for development of Schedule Property.</p>
        
        <p class="clause">Office of the Tehsildar, Anekal Taluk vide Certificate No. RD1218028021831, dated 03-10-2024 has issued 'nil tenancy' certificate, confirming that there are no 'tenancy' applications pending in relation to the Schedule Property.</p>
        
        <p class="clause">Office of the Assistant Commissioner, Bangalore South Sub-Division, vide Endorsement bearing No. L.R.F.(A) C.R:35/2025 dated 27-02-2025 has stated that since Sections 79(a)(b) of Land Reforms Act, 1961 has been omitted by Land Reforms (Second Amendment) Act, 2020, there is no provision to issue any endorsement regarding any pendency of any case in relation to the Schedule Property.</p>
        
        <p class="clause">Office of the Assistant Commissioner, Bangalore South Sub-Division, vide Endorsement bearing No. P.T.C.L(A)/C.R:955/2024-25 dated 01-03-2025 has stated that, there are no cases registered under the Karnataka Scheduled Castes and Scheduled Tribes (Prohibition of Transfer of Certain Lands) Act, 1978 and since the Schedule Property has been converted for residential purpose, the same shall not apply.</p>
        
        <p class="clause">WHEREAS, the OWNER herein, in order to develop the Schedule A Property into a multistoried residential apartment, have entered into a Joint Development Agreement dated 27-11-2024 with M/s. RRL Builders and Developers Private Limited, represented by its Managing Director, Mr. Ram R S/o. Mr. C. Raja Reddy, the BUILDER herein and registered as document No. SRJ-1-07944-2024-25, the same have registered on 29-11-2024 and stored in Central Cloud, in the office of the Senior Sub-Registrar, Basavanagudi (Sarjapura) (hereinafter referred to as "JDA").</p>
        
        <p class="clause">WHEREAS, in accordance with JDA, the BUILDER has agreed to build and construct a residential apartment building, which is later named as <strong>"RRL PALM ALTEZZE"</strong> on the Schedule A Property and to deliver to the OWNER free from any encumbrances and liabilities 33% of the super built-up area (including 33% of open/covered car parking space) in the aforesaid residential apartment, which is earmarked as 'Owner's Constructed Area'.</p>
        
        <p class="clause">In consideration whereof, the OWNER herein has conveyed 67% of undivided, title and interest in favour of the BUILDER in the Schedule A Property and similarly, the BUILDER shall be entitled to retain free from any encumbrances and liabilities 67% of the super built-up area (including 67% of open/covered car parking space) in the Schedule A Property, which is earmarked as 'Developer's Constructed Area'.</p>
        
        <p class="clause">WHEREAS, the OWNER herein, pursuant to execution of JDA have executed a General Power of Attorney dated 27-11-2024 in favour of the BUILDER, registered as document No. SRJ-4-00669-2024-25, same as registered on 29-11-2024 & and stored in Central Cloud, in the office of the Senior Sub-Registrar, Basavanagudi (Sarjapura).</p>
        
        <p class="clause">WHEREAS, the OWNER, pursuant to GPA, has authorised the BUILDER to execute such documents and indenture in relation to development and building of residential apartment building on the Schedule A Property and to convey, absolute right title and interest by way of sale, mortgage, lease to anybody, on behalf of the OWNER w.r.t. 67% of the super built-up area (including 67% of open/covered car parking space) in the Schedule 'A' Property, which is earmarked as 'Developer's Constructed Area' and to receive such consideration w.r.t. the same.</p>
        
        <p class="clause">WHEREAS, the BUILDER, has formulated a plan for development of the Schedule A Property into a multi storied residential Apartment and has obtained Single Plan Approval for construction of Residential Apartment, vide the order of the Member Secretary and Joint Director of Urban and Rural Planning, Anekal Planning Authority, Anekal, vide their letter bearing No. APA/LAO/119/2024-25 dated 13-05-2025.</p>
        
        <p class="clause">WHEREAS, the BUILDER, thereafter has received Commencement Certificate bearing No. CC/241/2025-26 dated 18-08-2025 from the Member Secretary and Joint Director, Town and Country Planning, Satellite Ring Road Planning Authority, Bengaluru for construction of Basement + Ground + 23 Upper Floors in Tower 1 & Tower 2 on the Schedule A Property.</p>
        
        <p class="clause">WHEREAS, the BUILDER, thereafter has received necessary permissions from various authorities and has received construction license dated 07-10-2025 from Jantagondanahalli Gram Panchayat in the name of the OWNER.</p>
        
        <p class="clause">WHEREAS, the BUILDER, thereafter has registered the aforesaid project in the name and style of <strong>'RRL PALM ALTEZZE'</strong> ("Project") and has obtained registration from Real Estate Regulatory Authority vide <strong>RERA Reg. No. PRM/KA/RERA/1251/308/PR/141025/008167</strong>.</p>
        
        <p class="clause">WHEREAS, the BUILDER and the VENDOR has executed a Sharing Agreement dated 29-11-2024, as document No. SRJ-1-04868-2025-26 and stored in Central Cloud, in the office of the Senior Sub-Registrar, Basavanagudi (Sarjapura) wherein the OWNER and the BUILDER has earmarked their respective share in the aforesaid building 'RRL PALM ALTEZZE' in the ratio of 33 : 67 ('Owner's Constructed Area' : 'Developer's Constructed Area').</p>
        
        <p class="clause">WHEREAS, in pursuance of the above a residential <span class="highlight">{bhk_type}</span> flat bearing Flat No. <span class="highlight">{unit_number}</span>, to be built on the <span class="highlight">{floor_ordinal}</span> Floor measuring about <span class="highlight">{saleable_area}</span> Sq. Ft. of Super Built-up Area, to be built on the Schedule 'A' Property along with one covered Car Parking Space (more fully described herein and hereinafter referred to as the "Schedule 'C' Property") along with <span class="highlight">{uds}</span> Sq. Ft. of Undivided Share, title and interest in the Schedule 'A' Property (morefully described herein and hereinafter referred to as the "Schedule 'B' Property") has fallen into the share of the BUILDER herein.</p>
        
        <p class="clause">WHEREAS, the ALLOTTEE/S has applied to the BUILDER to purchase the Schedule 'B' Property and Schedule 'C' Property along with proportionate share in the common areas of the building built on Schedule 'A' Property along with one covered car parking space.</p>
        
        <p class="clause">WHEREAS, the VENDORS have allotted Schedule 'B' Property and Schedule 'C' Property in favour of the PURCHASER/S and has intended to sell the same for valuable consideration herein below mentioned.</p>
        
        <p class="clause">WHEREAS the VENDORS have agreed to sell the Schedule 'B' Property and Schedule 'C' Property to the ALLOTTEE/S and the ALLOTTEE/S has/have agreed to purchase the Schedule 'B' Property and Schedule 'C' Property for consideration mentioned herein below and upon such other terms and conditions agreed to between them as detailed herein below.</p>
        
        <p class="clause">The Parties have gone through all the terms and conditions set out in this Agreement and understood the mutual rights and obligations detailed herein.</p>
        
        <p class="clause">The Parties hereby confirm that they are signing this Agreement with full knowledge of all the laws, rules, regulations, notifications, etc., applicable to the Project.</p>
        
        <p class="clause">The Parties, relying on the confirmations, representations and assurances of each other to faithfully abide by all the terms, conditions and stipulations contained in this Agreement and all applicable laws, are now willing to enter into this Agreement on the terms and conditions appearing hereinafter.</p>
        
        <!-- SECTION II: TERMS AND CONDITIONS -->
        <div class="section-title">II. IT IS HEREBY AGREED BY AND BETWEEN THE PARTIES AS FOLLOWS:</div>
        
        <div class="sub-section-title">SALE PRICE AND TERMS OF PAYMENT:</div>
        
        <p class="clause"><span class="clause-number">(i)</span> The VENDORS agrees to sell, and the PURCHASER/S agrees to buy the Schedule 'B' Property and Schedule 'C' Property, for a total sale consideration of <strong>Rs. <span class="highlight">{total_price_formatted}</span>/- (<span class="highlight">{total_price_words}</span> Only)</strong> as given.</p>
        
        <p class="clause"><strong>Note:</strong> Stamp Duty, Registration Fee & Other Expenses to be incurred towards the same shall have to be borne by the PURCHASER/S at the time of Registration. All payments to be made in the name of BUILDER (i.e. M/s. RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED) in the following ESCROW Account.</p>
        
        <table class="details">
            <tr><th>Account Holder Name</th><td>RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</td></tr>
            <tr><th>Bank</th><td>HDFC BANK</td></tr>
            <tr><th>Branch</th><td>SOMPURA</td></tr>
            <tr><th>Account Number</th><td>57500001802063</td></tr>
            <tr><th>IFSC Number</th><td>HDFC0009590</td></tr>
        </table>
        
        <p class="clause">Bajaj Housing Finance Limited ("Lender" or "BHFL") is the Lender of the Project and the properties of the Project have been charged/mortgaged in favour of the Lender and any sale consideration in respect of the units of the Project shall be deposited by the PURCHASER/S directly in the aforesaid Escrow Account. Also the Borrower(s) hereby undertakes that existing and proposed unit buyers of the Project and mortgage financing institution wherever unit buyers availed/are availing Residential Purchase loans shall be informed to deposit balance consideration in the Escrow Account as provided herein.</p>
        
        <p class="clause"><span class="clause-number">(ii)</span> Accordingly, the PURCHASER/S as a token of acceptance, has paid a sum of <strong>Rs. <span class="highlight">{booking_amount_formatted}</span>/- (<span class="highlight">{booking_amount_words}</span> Only)</strong> vide payment details recorded separately. The receipt of which the VENDORS hereby accepts and acknowledges in the presence of the witnesses attesting hereunder.</p>
        
        <p class="clause"><span class="clause-number">(iii)</span> The payment of sale consideration being the essence of this Agreement, the PURCHASER/S will pay the balance consideration and all amounts payable under this Agreement without any default in accordance with the payment schedule and timelines mentioned hereunder. All such payments shall be made after deduction of applicable TDS (if any).</p>
        
        <div class="sub-section-title">Payment Schedule:</div>
        
        <table class="schedule">
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 55%;">Milestone / Particulars</th>
                    <th style="width: 12%;">%</th>
                    <th style="width: 28%;">Amount (Rs.)</th>
                </tr>
            </thead>
            <tbody>
                {payment_schedule_rows}
            </tbody>
            <tfoot>
                <tr style="background: #1A1A1A;">
                    <td colspan="2" style="color: #D4AF37; font-weight: bold;">TOTAL</td>
                    <td style="color: #D4AF37; font-weight: bold;">100%</td>
                    <td class="amount" style="color: #D4AF37; font-weight: bold;">{total_price_formatted}</td>
                </tr>
            </tfoot>
        </table>
        
        <div class="sub-section-title">Transaction Details (Payments Received):</div>
        
        <table class="schedule">
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 20%;">Date</th>
                    <th style="width: 20%;">Stage</th>
                    <th style="width: 25%;">Bank / Reference</th>
                    <th style="width: 30%;">Amount (Rs.)</th>
                </tr>
            </thead>
            <tbody>
                {transaction_rows}
            </tbody>
            <tfoot>
                <tr style="background: #1A1A1A;">
                    <td colspan="4" style="color: #D4AF37; font-weight: bold;">TOTAL RECEIVED</td>
                    <td class="amount" style="color: #D4AF37; font-weight: bold;">{total_received_formatted}</td>
                </tr>
            </tfoot>
        </table>
        
        <p class="clause"><strong>Note:</strong></p>
        <p class="sub-clause">a. All the payments shall have to be made within 7 days from the date of completion of the milestone above mentioned. The PURCHASER/S shall pay the installments as mentioned above regularly in favour of BUILDER as above mentioned either by way of DD/Cheque/RTGS/NEFT on or before the due dates. The BUILDER shall be entitled to claim simple interest calculated at the rate of 1.5% per month on all delayed payments of installments from the PURCHASER/S from the date due till the date of payment. However, if the PURCHASER/S fails to make payment beyond 60 days from the date due, the BUILDER shall be entitled to terminate this Agreement on the account of 'non-payment'.</p>
        
        <p class="sub-clause">b. The PURCHASER/S may choose to avail housing loan from any Banks/Financial Institutions. Builder under any circumstances shall not be responsible or liable for non-sanction of loans or as per timelines aforesaid.</p>
        
        <p class="sub-clause">c. The ALLOTTEE/S, if resident outside India, shall be solely responsible for complying with the necessary formalities as laid down in Foreign Exchange Management Act, 1999, Reserve Bank of India Act, 1934 and the Rules and Regulations made thereunder or any statutory amendment(s) modification(s) made thereof and all other applicable laws including that of remittance of payment acquisition/sale/transfer of immovable properties in India etc. and provide the BUILDER with such permission, approvals which would enable the BUILDER to fulfill its obligations under this Agreement.</p>
        
        <p class="sub-clause">d. Any refund, transfer of security, if provided in terms of the Agreement shall be made in accordance with the provisions of Foreign Exchange Management Act, 1999 or the statutory enactments or amendments thereof and the Rules and Regulations of the Reserve Bank of India or any other applicable law. The ALLOTTEE/S understands and agrees that in the event of any failure on his/her part to comply with the applicable guidelines issued by the Reserve Bank of India, he/she may be liable for any action under the Foreign Exchange Management Act, 1999 or other laws as applicable, as amended from time to time. The BUILDER accepts no responsibility in regard to matters specified in para above. The ALLOTTEE/S shall keep the BUILDER fully indemnified and harmless in this regard.</p>
        
        <p class="sub-clause">e. Whenever there is any change in the residential status of the ALLOTTEE/S subsequent to the signing of this Agreement, it shall be the sole responsibility of the ALLOTTEE/S to intimate the same in writing to the BUILDER immediately and comply with necessary formalities if any under the applicable laws.</p>
        
        <p class="sub-clause">f. The BUILDER shall not be responsible towards any third-party making payment/remittances on behalf of any ALLOTTEE/S and such third party shall not have any right in the application/allotment of the said apartment applied for herein in any way and the BUILDER shall be issuing the payment receipts in favour of the ALLOTTEE/S only.</p>
        
        <div class="sub-section-title">CONSTRUCTION OF THE PROJECT:</div>
        <p class="clause">The ALLOTTEE/S has seen the proposed layout plan, specifications, amenities and facilities of Apartment and accepted the floor plan, payment plan and the specifications, amenities and facilities which has been approved by the competent authority, as represented by the BUILDER. The BUILDER shall develop the Project in accordance with the said layout plans, floor plans and specifications, amenities and facilities. Subject to the terms in this Agreement and permissible deviations.</p>
        
        <div class="sub-section-title">POSSESSION OF THE APARTMENT:</div>
        <p class="clause">The BUILDER understands that timely delivery of possession of the Apartment to the ALLOTTEE/S and the common areas to the association of ALLOTTEE/S or the competent authority, as the case may be, is the essence of the Agreement. The BUILDER assures to hand over possession of the Apartment along with ready and complete common areas with all specifications, amenities and facilities of the project in place on or before <strong><span class="highlight">{possession_date}</span></strong>, unless there is delay or failure due to war, flood, drought, fire, cyclone, earthquake, non-availability of manpower, non-availability of materials, court orders, regulatory orders, change in policy, or any other calamity, epidemic, lockdowns, strikes, etc. affecting the regular development of the real estate project ("Force Majeure").</p>
        
        <p class="clause">If, however, the completion of the Project is delayed due to the Force Majeure conditions then the ALLOTTEE/S agrees that the BUILDER shall be entitled to such extension of time for delivery of possession of the Apartment.</p>
        
        <p class="clause">The ALLOTTEE/S agrees and confirms that, in the event it becomes impossible for the BUILDER to implement the project due to Force Majeure conditions, then this allotment shall stand terminated and the BUILDER shall refund to the ALLOTTEE/S the entire amount received by the BUILDER from the allotment within 90 days from the date of such communication. If the client has opted for Pre EMI, then interest amount paid by the builder (if any) will be kept on hold. Along with that, 5% GST amount will also be kept on hold and the balance amount will be refunded to the client. The BUILDER shall intimate the allottee about such termination. After refund of the money paid by the ALLOTTEE/S, the ALLOTTEE/S agrees that he/she shall not have any rights, claims etc. against the BUILDER and that the BUILDER shall be released and discharged from all its obligations and liabilities under this Agreement.</p>
        
        <p class="clause">The BUILDER, upon obtaining the occupancy certificate from the competent authority shall offer in writing the possession of the Apartment, to the ALLOTTEE/S in terms of this Agreement to be taken within three months from the date of issue of occupancy certificate.</p>
        
        <p class="clause">The BUILDER agrees and undertakes to indemnify the ALLOTTEE/S in case of failure of fulfillment of any of the provisions, formalities, documentation on part of the BUILDER.</p>
        
        <p class="clause">The ALLOTTEE/S, after taking the possession, agree(s) to pay the maintenance charges as determined by the BUILDER/association of ALLOTTEE/S, as the case may be after the issuance of the completion certificate for the project. Failure of ALLOTTEE/S to take Possession of Apartment upon receiving a written intimation from the BUILDER, the ALLOTTEE/S shall take possession of the Apartment from the BUILDER by executing such deed of conveyance or 'Deed of Absolute Sale' as envisaged in this Agreement and after making all payments, and the BUILDER shall give possession of the Apartment to the ALLOTTEE/S.</p>
        
        <p class="clause">In case the ALLOTTEE/S fails to take possession or make payments as stipulated under this Agreement, within the time provided, in such event, this Agreement, at the option of the BUILDER shall stand terminated and the BUILDER shall be entitled to sell the Apartment to any such prospective buyer. In the event, the ALLOTTEE/S has made payment and fails to take handover of the Apartment for any other reason, then such ALLOTTEE/S shall continue to be liable to pay maintenance charges.</p>
        
        <p class="clause">After handing over physical possession of the Apartment to the ALLOTTEE/S, it shall be the responsibility of the BUILDER to hand over the necessary documents and plans, including common areas, to the association of ALLOTTEE/S or the competent authority, as the case may be, as per applicable laws.</p>
        
        <p class="clause">In the event the ALLOTTEE/S proposes to cancel/withdraw from the project without any fault of the BUILDER, the BUILDER herein is entitled to forfeit the booking amount paid for the allotment by the ALLOTTEE/S and return the balance amount of money paid by the ALLOTTEE/S within 90 days of such cancellation.</p>
        
        <p class="clause">In the event BUILDER fails to deliver the possession of the Apartment to the ALLOTTE/S for any reason other than reason of occurrence of Force Majeure event within the aforesaid stipulated time, the BUILDER shall be liable to pay on demand to the ALLOTTEE/S the amount received under this Agreement along with interest as stipulated under law within 90 days from the date of such demand, in the event of termination of this Agreement by the ALLOTTEE/S.</p>
        
        <p class="clause">In the event ALLOTTEE/S does not intend to terminate this Agreement, then the BUILDER agrees to pay such delay penalty prescribed under law by the competent authority until the date of handover of possession.</p>
        
        <div class="sub-section-title">REPRESENTATIONS AND WARRANTIES OF THE VENDORS:</div>
        <p class="clause"><span class="clause-number">(i)</span> The VENDORS hereby represents and warrants to the ALLOTTEE/S as follows:</p>
        
        <ol class="roman-list" type="a">
            <li>The VENDORS has absolute, clear and marketable title with respect to the Schedule 'A' Property, including the requisite rights to carry out development upon the said land and absolute, actual, physical and legal possession of the said land for the Project;</li>
            <li>The VENDORS has lawful rights and requisite approvals from the competent authorities to carry out development of the Project;</li>
            <li>There are no encumbrances upon the Schedule 'A' Property or the Project;</li>
            <li>There are no litigations pending before any court of law or authority with respect to Schedule 'A' Property, Project or the Apartment;</li>
            <li>All approvals, licenses and permits issued by the competent authorities with respect to the Project, said Land and Apartment are valid and subsisting and have been obtained by following due process of law;</li>
            <li>The VENDORS have the right to enter into this Agreement and has not committed or omitted to perform any act or thing, whereby the right, title and interest of the ALLOTTEE/S created herein, may prejudicially be affected;</li>
            <li>The VENDORS have not entered into any agreement for sale/arrangement with any person or party with respect to the said land, including the Project and the Schedule 'C' Property, which will, in any manner, affect the rights of ALLOTTEE/S under this Agreement;</li>
            <li>The VENDORS confirms that the VENDORS are not restricted in any manner whatsoever from selling the Schedule 'C' Property to the ALLOTTEE/S in the manner contemplated in this Agreement;</li>
            <li>At the time of execution of the conveyance deed the VENDORS shall handover lawful, vacant, peaceful, physical possession of the Schedule 'C' Property and constructive possession of the Schedule 'B' Property to the ALLOTEE/S and the common areas to the Association of the allottees or the competent authority, as the case may be;</li>
            <li>The Schedule 'A' Property is not the subject matter of any HUF and that no part thereof is owned by any minor and/or no minor has any right, title and claim over the Schedule 'A' Property;</li>
            <li>The VENDORS have duly paid and shall continue to pay and discharge all governmental dues, rates, charges and taxes and other monies, levies, impositions, premiums, damages and/or penalties and other outgoings, whatsoever, payable with respect to the Project to the competent authorities till the completion certificate has been issued and possession of apartment, plot or buildings, as the case may be, along with common areas (equipped with all the specifications, amenities and facilities) has been handed over to the ALLOTTEE/S and the association of allottees or the competent authority, as the case may be;</li>
            <li>No notice from the Government or any other local body or authority or any legislative enactment, government ordinance, order, notification (including any notice for acquisition or requisition of the said property) has been received by or served upon the BUILDER in respect of the said Land and/or the Project.</li>
        </ol>
        
        <div class="sub-section-title">CONVEYANCE OF THE SCHEDULE 'B' PROPERTY AND SCHEDULE 'C' PROPERTY:</div>
        <p class="clause">The BUILDER, on receipt of total consideration towards Schedule 'B' Property and Schedule 'C' Property as envisaged under this Agreement from the ALLOTTEE/S, shall execute a conveyance deed in favour of the ALLOTTEE/S and convey the title of the Schedule 'C' Property together with proportionate indivisible share in the Schedule 'A' Property within 3 months from the date of issuance of the occupancy certificate / completion certificate, as the case may be, provided the ALLOTTEE/S pays the stamp duty, registration fees and charges.</p>
        
        <div class="sub-section-title">MAINTENANCE OF THE PROJECT:</div>
        <p class="clause">The BUILDER shall be responsible to provide and maintain essential services in the Project till the taking over of the maintenance of the Project by the association of the allottees or for a period of one year from the date of receipt of completion certificate /occupancy certificate, whichever is earlier. The ALLOTEE/S agrees to deposit one year's maintenance and corpus amount in advance on the date of conveyance of the Schedule 'C' Property or such date stipulated by the BUILDER.</p>
        
        <div class="sub-section-title">DEFECT LIABILITY:</div>
        <p class="clause">It is agreed that in case any structural defect in workmanship, quality or provision of services or any other obligations of the BUILDER as per this Agreement is brought to the notice of the BUILDER within a period of 5 (five) years by the ALLOTTEE/S from the date of handing over possession, it shall be the duty of the BUILDER to rectify such defects.</p>
        
        <div class="sub-section-title">RIGHT TO ENTER THE PROJECT FOR REPAIRS:</div>
        <p class="clause">The BUILDER /maintenance agency /association of allottees shall have rights of unrestricted access to all common areas, garages/covered parking and parking spaces for providing necessary maintenance services and the ALLOTTEE/S agrees to permit the association of allottees and/or maintenance agency to enter into the Apartment or any part thereof, after due notice and during the normal working hours, unless the circumstances warrant otherwise, with a view to set right any defect/issues.</p>
        
        <div class="sub-section-title">USAGE:</div>
        <p class="clause">The basement and service areas, if any, as located within the Project, shall be earmarked for purposes such as parking spaces and services including but not limited to electric sub-station, transformer, DG set rooms, underground water tanks, pump rooms, maintenance and service rooms, fire-fighting pumps and equipment etc. and other permitted uses as per sanctioned plans. The ALLOTTEE/S shall not be permitted to use the services areas and the basements in any manner whatsoever, other than those earmarked as parking spaces, and the same shall be reserved for use by the association of allottees formed by the allottees for rendering maintenance services.</p>
        
        <div class="sub-section-title">10. COVENANTS OF ALLOTTEE/S / PURCHASER/S:</div>
        <p class="clause">ALLOTTEE/S agrees that after taking possession and handover of the Apartment from the BUILDER, he/her/they shall be solely responsible to maintain the Apartment at his/her/their own cost, in good repair and condition and shall not do or suffer to be done anything in or to the Building, or the Apartment or the staircases, lifts, common passages, corridors, circulation areas, atrium or the compound which may be in violation of any laws or rules of any authority or change or alter or make additions to the Apartment and keep the Apartment, its walls and partitions, sewers, drains, pipe and appurtenances thereto or belonging thereto, in good and tenantable repair and maintain the same in a fit and proper condition and ensure that the support, shelter etc. of the Building is not in any way damaged or jeopardized.</p>
        
        <p class="clause">The ALLOTTEE/S further undertakes, assures and guarantees that he/she would not put any sign-board / name-plate, neon light, publicity material or advertisement material etc. on the face/facade of the building or anywhere on the exterior of the Project, buildings therein or Common Areas. The ALLOTTEE/S shall also not change the colour scheme of the outer walls or painting of the exterior side of the windows or carry out any change in the exterior elevation or design. Further the ALLOTTEE/S shall not store any hazardous or combustible goods in the Apartment/Building or place any heavy material in the common passages or staircase of the Building/Common Areas. The ALLOTTEE/S shall also not remove any wall, including the outer and load bearing wall of the Apartment.</p>
        
        <p class="clause">iii. The ALLOTTEE/S shall plan and distribute its electrical load in conformity with the electrical systems installed by the BUILDER and thereafter the association of ALLOTTEE/S and/or maintenance agency appointed by association of allottees. The ALLOTTEE/S shall be responsible for any loss or damages arising out of breach of any of the aforesaid conditions.</p>
        
        <p class="clause">iv. The ALLOTTEE/S shall not cause any obstruction for the free passage and movement in driveways, pathways, passages and other common areas.</p>
        
        <p class="clause">v. The ALLOTTEE/S in the event intends to sell the Schedule 'C' Property, shall take NOC from the association formed by the ALLOTTEE/S.</p>
        
        <p class="clause">vi. The ALLOTTEE/S shall mandatorily be required to be a member of the Apartment Owners Association to be formed for maintaining and management of common amenities and facilities with other allotees of the building under appropriate and applicable laws. The ALLOTTEE/S shall pay maintenance from time to time to the constituted Apartment Owners Association post-handover from BUILDER, to access common amenities and towards maintenance of the BUILDING and shall be bound by such bye-laws adopted and rules and regulations applicable.</p>
        
        <p class="clause">vii. The ALLOTTEE/S shall have no right, title or interest in the areas earmarked as 'common areas' other than 'right to use' the same in common in a prudent manner. The ALLOTTEE/S shall live in harmony with other allottees of the BUILDING and shall not disturb anybody's peaceful enjoyment of the BUILDING.</p>
        
        <p class="clause">viii. The ALLOTTEE/S shall pay the pro-rata or stipulated property taxes and cess and outgoing expenses for maintenance of common areas and common facilities including common water charges, street lights, security, repair and maintenance determined by constituted Apartment Owners Association from time to time.</p>
        
        <p class="clause">ix. The ALLOTTEE/S shall maintain surroundings of Schedule 'C' Property and the BUILDING clean and tidy and shall not cause any nuisance to other occupants. The ALLOTTEE/S shall keep no other animal except pet dog/cat in the Apartment and shall ensure that the same shall not cause any disturbance to other occupants of the BUILDING.</p>
        
        <p class="clause">x. The ALLOTTEE/S in the event of leasing the Schedule 'C' Property, shall keep informed the Apartment Owners Association about the same and shall furnish the details of such lessee and it shall be the primary responsibility of the ALLOTTEE/S to ensure compliance of the terms in this Agreement and applicable bye laws by such lessee.</p>
        
        <p class="clause">xi. The ALLOTTEE/S shall not change the name of the building "RRL PALM ALTEZZE". The ALLOTTEE/S shall use treated STP water for gardening and other secondary purpose.</p>
        
        <p class="clause">xii. The ALLOTTEE/S shall not be entitled to assign the terms of this Agreement, without prior approval of the BUILDER and payment of transfer fees, and if flat is booked through CP and purchase wants to cancel the flat after the agreement 3% of the flat value will be holding by the builder.</p>
        
        <p class="clause">xiii. The ALLOTTEE/S understands that they along with all other allottees shall be responsible for routine maintenance including:</p>
        <ul class="specs-list">
            <li>painting, white washing, cleaning of the Apartment;</li>
            <li>maintenance of the pumped, sanitary and electrical lines common to the BUILDING;</li>
            <li>replacement of lights/bulbs in the common areas;</li>
            <li>maintenance of gardens, parks, plants in the common areas;</li>
            <li>maintenance of common amenities, swimming pool, play area, lifts, etc.;</li>
            <li>deployment of security, maintenance and housekeeping staff.</li>
        </ul>
        
        <p class="clause">xiv. ALLOTTEE/S understands that in the event of default of payment due for any common expenses, benefits or amenities, a majority of the owners while carrying out the services as contemplated above, shall have the right to remove such common benefits, or amenities from his/her/their enjoyment, until payment of all dues.</p>
        
        <div class="sub-section-title">11. RIGHTS OF THE PURCHASER/S / ALLOTTEE/S:</div>
        <p class="clause">The right to own an apartment described in Schedule 'C' Property for residential purpose. The right and liberty to the PURCHASER/S and all persons entitled, authorized or permitted by the PURCHASER/S (in common with all other persons entitled, permitted or authorized to a similar right) at all times and for all purposes, to use the staircases, passages and common areas in the building for ingress and egress and use in common. The right to subjacent, lateral, vertical and horizontal support for the Schedule 'C' Property from the other parts of the building.</p>
        
        <p class="clause">The right to free and uninterrupted passage of water, reticulated gas, electricity, sewage, etc., from and to the Schedule 'C' Property through the pipes, wires, sewer lines, drain and water courses and cables which are or may at any time hereafter be, in, under or passing through the building or any part thereof.</p>
        
        <p class="clause">The right to lay cables or wires for television, telephone, internet, gas, cable, etc. and such other installations through the common walls is subject to the bye-laws of the 'Apartment Owners Association', thereby recognizing and reciprocating such rights of the other residents of the apartment.</p>
        
        <p class="clause">Right of entry and passage for the PURCHASER/S with or without workmen to other parts of the Building at all reasonable time to enter into and upon other parts of the building for the purpose of repairs to or maintenance of the Schedule 'C' Property or for repairing, cleaning, maintaining or removing the sewer, drains and water courses, cables, pipes and wires causing as little disturbance as possible to the other residents of the apartment and making good any damage caused.</p>
        
        <p class="clause">Right to use along with other owners and residents of the apartments, all the common facilities provided therein on payment of such sums as may be prescribed from time to time by 'Apartment Owners Association' / BUILDER, as the case may be.</p>
        
        <p class="clause">Right to use and enjoy the common roads, common areas and parks and open space and common facilities in Schedule 'A' Property in accordance with the purpose for which they are provided without endangering or encroaching the lawful rights of other owners/users.</p>
        
        <p class="clause">The PURCHASER/S shall be entitled in common with the owners and residents of the other apartments in the BUILDING, to use and enjoy the common areas and facilities listed here under:</p>
        <ul class="specs-list">
            <li>Entrance lobbies, passages and corridors;</li>
            <li>Lifts/pumps/generators, generator room;</li>
            <li>Staircase, driveways in the basements, roads and pavements;</li>
            <li>Common facilities, subject to compliance of rules, regulations of the Maintenance Agency and byelaws of the 'Apartment Owners Association'.</li>
        </ul>
        
        <div class="sub-section-title">12. ENTIRE AGREEMENT:</div>
        <p class="clause">This Agreement, along with its schedules, constitutes the entire Agreement between the Parties with respect to the subject matter hereof and supersedes any and all understandings, any other agreements, allotment letter, correspondences, arrangements whether written or oral, if any, between the Parties in regard to the said apartment/plot/building, as the case may be.</p>
        
        <div class="sub-section-title">13. RIGHT TO AMEND:</div>
        <p class="clause">This Agreement may only be amended through written consent of the Parties.</p>
        
        <div class="sub-section-title">14. PROVISIONS OF THIS AGREEMENT APPLICABLE ON ALLOTTEE/S OR SUBSEQUENT ALLOTTEE/S:</div>
        <p class="clause">It is clearly understood and so agreed by and between the Parties hereto that all the provisions contained herein and the obligations arising hereunder in respect of the Apartment and the Project shall equally be applicable to and enforceable against and by any subsequent ALLOTTEE/S of the Apartment, in case of a transfer, as the said obligations go along with the Apartment for all intents and purposes.</p>
        
        <div class="sub-section-title">15. WAIVER NOT A LIMITATION TO ENFORCE:</div>
        <p class="clause">The BUILDER may, at its sole option and discretion, without prejudice to its rights as set out in this Agreement, waive the breach by the ALLOTTEE/S in not making payments as per the payment schedule including waiving the payment of interest for delayed payment. It is made clear and so agreed by the ALLOTTEE/S that exercise of discretion by the BUILDER in the case of one ALLOTTEE/S shall not be construed to be a precedent and /or binding on the BUILDING to exercise such discretion in the case of other ALLOTTEE/S.</p>
        
        <div class="sub-section-title">16. SEVERABILITY:</div>
        <p class="clause">If any provision of this Agreement shall be determined to be void or unenforceable under the applicable acts or rules and regulations made thereunder or under other applicable laws, such provisions of the Agreement shall be deemed amended or deleted in so far as reasonably inconsistent with the purpose of this Agreement and to the extent necessary, and the remaining provisions of this Agreement shall remain valid and enforceable as applicable at the time of execution of this Agreement.</p>
        
        <div class="sub-section-title">17. NOTICES:</div>
        <p class="clause">That all notices to be served on the ALLOTTEE/S and the VENDORS as contemplated by this Agreement shall be deemed to have been duly served if sent to the respective parties by Registered Email / Post at the addresses aforesaid.</p>
        
        <div class="sub-section-title">18. JOINT ALLOTTEES:</div>
        <p class="clause">That in case there are joint allottees all communications shall be sent by the BUILDER to the ALLOTTEE/S whose name appears first and at the address given by him/her which shall for all intents and purposes to consider as properly served on all the ALLOTTEE/S.</p>
        
        <div class="sub-section-title">19. GOVERNING LAW & JURISDICTION:</div>
        <p class="clause">That the rights and obligations of the parties under or arising out of this Agreement shall be construed and enforced in accordance with Indian Laws and the parties shall submit to exclusive jurisdiction of courts at Anekal / Bengaluru Rural.</p>
        
        <!-- SCHEDULE A -->
        <div class="schedule-section">
            <div class="schedule-header">SCHEDULE 'A' PROPERTY</div>
            <p style="text-align: center; font-weight: 600; margin-bottom: 15px;">(DESCRIPTION OF THE LAND ON WHICH PROJECT IS DEVELOPED)</p>
            
            <p class="clause">All that piece and parcel of the undeveloped converted land bearing Sy. No.73/6 (Old Sy. No. 73/5 and Old Old Sy. No. 73) (bearing PID No.150200101600120805), measuring 1-0 (One) Acre 0-38 (Thirty Eight) Guntas, converted from agricultural to non-agricultural residential purpose vide conversion order bearing No. APL/L.U/10/2023-24 dated 22/11/2024, issued by the Member Secretary & Joint Director, Anekal Planning Authority, situated at Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bangalore Urban District, bounded on the:</p>
            
            <table class="boundary-table">
                <tr><th>East by:</th><td>Chikka Muniswamy's Land</td></tr>
                <tr><th>West by:</th><td>C Schedule Land / Nanjappa's Land</td></tr>
                <tr><th>North by:</th><td>Road</td></tr>
                <tr><th>South by:</th><td>Chikka Obareddy's Land</td></tr>
            </table>
        </div>
        
        <!-- SCHEDULE B -->
        <div class="schedule-section">
            <div class="schedule-header">SCHEDULE 'B' PROPERTY</div>
            <p style="text-align: center; font-weight: 600; margin-bottom: 15px;">(UNDIVIDED INTEREST HEREBY CONVEYED)</p>
            
            <p class="clause"><span class="highlight">{uds}</span> Sq. Ft. of undivided share, right, title, interest and ownership in the Schedule 'A' Property.</p>
        </div>
        
        <!-- SCHEDULE C -->
        <div class="schedule-section">
            <div class="schedule-header">SCHEDULE 'C' PROPERTY</div>
            <p style="text-align: center; font-weight: 600; margin-bottom: 15px;">(DESCRIPTION OF THE APARTMENT HEREBY CONVEYED)</p>
            
            <p class="clause">All that <span class="highlight">{bhk_type}</span> Residential Flat bearing Flat No. <span class="highlight">{unit_number}</span> on the <span class="highlight">{floor_ordinal}</span> Floor, measuring about <span class="highlight">{saleable_area}</span> Sq.Ft., of super built-up area, to be developed and constructed on Schedule 'A' Property, along with one covered car parking space{additional_parking_text}, in the project/building known as <strong>RRL PALM ALTEZZE</strong>.</p>
            
            <div class="sub-section-title">Specifications of the Building:</div>
            <ul class="specs-list">
                <li>R.C.C. Framed Structure;</li>
                <li>2.5 Track Fabricated Windows for living and bedroom with mosquito mesh;</li>
                <li>Main Door Frame and all other doors with Pre hung doors shutters;</li>
                <li>Client can select Tile Flooring / Wooden flooring for master bedroom, Wooden flooring will not have any warranty or guaranty;</li>
                <li>Concealed copper wiring with Anchor/Roma Switches, Socket and Slides;</li>
                <li>Individual TV & Telephone points in Living and Master Bedroom;</li>
                <li>Emulsion Paint for internal walls and exterior with Apex paints;</li>
                <li>Vitrified tiles for flooring and anti-skid tiles for balcony;</li>
                <li>Kerovit Sanitary fittings by Kajaria;</li>
                <li>Anti-Skid ceramic tiled flooring and glazed dado tiles up to 7" for toilets;</li>
            </ul>
            
            <div class="sub-section-title">Amenities:</div>
            <ul class="amenities-list">
                <li>Club House (gym, multipurpose hall, steam bath, sauna bath, indoor games, kids play area, sit out, mini theater)</li>
                <li>STP, Gas Bank</li>
                <li>Swimming Pool</li>
                <li>Lifts by OTIS</li>
                <li>Indoor/Outdoor Games</li>
                <li>Power Back-up for common area and flat</li>
            </ul>
        </div>
        
        <!-- SIGNATURE SECTION -->
        <div class="signature-section">
            <p style="font-weight: 700; margin-bottom: 20px;">IN WITNESS WHEREOF the Parties hereto have set and subscribed their respective hands and seals on the day, month and year first above-written.</p>
            
            <div class="party-section" style="margin-bottom: 20px;">
                <p><strong>OWNERS:</strong></p>
                <p>MRS. MUNITHAYAMMA</p>
                <p>MRS. YESHASWINI N</p>
                <p>MASTER HRUTHVIK REDDY S, Represented by his natural guardian mother, Mrs. Yeshaswini N.</p>
                <p>MS. TEJASWINI N</p>
                <p style="margin-top: 10px;"><strong>All are Represented by the General Power of Attorney Holder:</strong></p>
                <p>M/s. RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</p>
                <p>Represented by its Managing Director, <strong>MR. RAM R</strong></p>
            </div>
            
            <div class="signature-row">
                <div class="signature-box">
                    <p><strong>VENDORS</strong></p>
                    <div class="signature-line">
                        <p>For RRL Builders & Developers Pvt. Ltd.</p>
                        <p>Authorized Signatory</p>
                    </div>
                </div>
                <div class="signature-box">
                    <p><strong>PURCHASER/S</strong></p>
                    <div class="signature-line">
                        <p>{customer_name}</p>
                    </div>
                </div>
            </div>
            
            <div class="witness-section">
                <p><strong>WITNESSES:</strong></p>
                <div class="signature-row" style="margin-top: 20px;">
                    <div class="signature-box">
                        <div class="signature-line">
                            <p>1. ____________________</p>
                        </div>
                    </div>
                    <div class="signature-box">
                        <div class="signature-line">
                            <p>2. ____________________</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p><strong>RRL Builders and Developers Pvt. Ltd.</strong></p>
        <p>4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru – 562125</p>
        <p>www.rrlbuildersanddevelopers.com | RERA: PRM/KA/RERA/1251/308/PR/141025/008167</p>
        <p style="margin-top: 10px;">Document Generated: {date} | Ref: {customer_id}</p>
    </div>
</body>
</html>
"""

def get_default_template(doc_type: DocumentType) -> str:
    templates = {
        DocumentType.SALES_AGREEMENT: generate_sales_agreement_template(),
        DocumentType.ALLOTMENT_LETTER: """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Roboto', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1A1A1A;
            background: #fff;
            padding: 25px 40px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #D4AF37;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo {
            width: 50px;
            height: 50px;
            background: #1A1A1A;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #D4AF37;
            font-weight: bold;
            font-size: 18px;
        }
        
        .company-name {
            font-size: 16px;
            font-weight: 700;
            color: #1A1A1A;
        }
        
        .company-tagline {
            font-size: 10px;
            color: #666;
        }
        
        .document-title {
            background: #1A1A1A;
            color: #D4AF37;
            padding: 8px 18px;
            border-radius: 4px;
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
        }
        
        .recipient {
            margin-bottom: 15px;
            padding: 15px;
            background: #fafafa;
            border-left: 4px solid #D4AF37;
        }
        
        .recipient p {
            margin: 3px 0;
            font-size: 11px;
        }
        
        .highlight {
            color: #D4AF37;
            font-weight: 600;
        }
        
        .subject {
            margin: 15px 0;
            font-weight: 600;
            color: #1A1A1A;
        }
        
        .greeting {
            margin: 10px 0;
        }
        
        .content {
            text-align: justify;
            margin: 12px 0;
            font-size: 10.5pt;
        }
        
        .section-title {
            font-weight: 600;
            color: #D4AF37;
            margin: 18px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 2px solid #D4AF37;
            font-size: 11pt;
        }
        
        .terms {
            margin-left: 15px;
        }
        
        .terms p {
            margin: 10px 0;
            text-align: justify;
            font-size: 10pt;
        }
        
        .terms-number {
            font-weight: 600;
            color: #D4AF37;
        }
        
        table.details {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        table.details th, table.details td {
            border: 1px solid #D4AF37;
            padding: 8px 12px;
            text-align: left;
            font-size: 10.5pt;
        }
        
        table.details th {
            background: #1A1A1A;
            color: #D4AF37;
            font-weight: 500;
            width: 40%;
        }
        
        table.details td {
            background: #fafafa;
        }
        
        .signature-section {
            margin-top: 35px;
            display: flex;
            justify-content: space-between;
        }
        
        .signature-box {
            width: 45%;
        }
        
        .signature-line {
            border-top: 1px solid #1A1A1A;
            margin-top: 50px;
            padding-top: 5px;
        }
        
        .declaration {
            margin-top: 25px;
            padding: 15px;
            border: 2px solid #D4AF37;
            background: #fafafa;
            font-size: 10pt;
        }
        
        .bank-details {
            margin: 12px 0;
            padding: 12px;
            background: #1A1A1A;
            color: #fff;
            border-radius: 4px;
        }
        
        .bank-details p {
            margin: 3px 0;
            font-size: 10pt;
        }
        
        .bank-details strong {
            color: #D4AF37;
        }
        
        .footer {
            margin-top: 25px;
            padding-top: 15px;
            border-top: 2px solid #D4AF37;
            text-align: center;
            font-size: 9pt;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-section">
            <div class="logo">RRL</div>
            <div>
                <div class="company-name">RRL Builders and Developers</div>
                <div class="company-tagline">Beyond homes. A lifestyle</div>
            </div>
        </div>
        <div class="document-title">Allotment Letter</div>
    </div>
    
    <div class="recipient">
        <p><strong>To,</strong></p>
        <p><strong>Dear Mr./Mrs. <span class="highlight">{customer_name}</span></strong></p>
        <p>Phone No: <span class="highlight">{phone}</span></p>
        <p>Email: <span class="highlight">{email}</span></p>
        <p>PAN: <span class="highlight">{pan_number}</span></p>
    </div>
    
    <div class="subject">
        <p>Subject: Confirmation of Allotment</p>
    </div>
    
    <div class="greeting">
        <p>Dear Sir/Madam,</p>
    </div>
    
    <div class="content">
        <p>We are issuing this allotment letter pursuant to your submission of an expression of interest dated <span class="highlight">{booking_date}</span>, requesting unit No. <span class="highlight">{unit_number}</span> in our project being developed under the name of "<strong>{project}</strong>" RERA No. PRM/KA/RERA/1251/308/PR/141025/008167. Upon due consideration of your EOI, we are pleased to confirm your booking and allot Flat No. <span class="highlight">{unit_number}</span> in "{project}" subject to the Terms and conditions set out herein. We take this opportunity to welcome you to "RRL BUILDERS AND DEVELOPERS PVT LTD" family and are pleased that you have chosen to purchase your home from us.</p>
        
        <p style="margin-top: 12px;">You hereby acknowledge and confirm that the copies of title documents have been handed over to you and that you have scrutinized and are satisfied with the title of the Developer to the project being good and marketable.</p>
    </div>
    
    <div class="section-title">A. ALLOTMENT DETAILS</div>
    
    <table class="details">
        <tr>
            <th>Heading</th>
            <th>Particulars</th>
        </tr>
        <tr>
            <td>Name of the Project</td>
            <td><span class="highlight">{project}</span></td>
        </tr>
        <tr>
            <td>RERA No.</td>
            <td>PRM/KA/RERA/1251/308/PR/141025/008167</td>
        </tr>
        <tr>
            <td>Flat Number</td>
            <td><span class="highlight">{tower} - {unit_number}</span></td>
        </tr>
        <tr>
            <td>UDS (in Sqft)</td>
            <td><span class="highlight">{uds}</span></td>
        </tr>
        <tr>
            <td>Super Built-up Area (in Sq ft)</td>
            <td><span class="highlight">{saleable_area}</span></td>
        </tr>
        <tr>
            <td>Total Cost of the Flat including GST</td>
            <td><span class="highlight">Rs. {total_price_formatted}/-</span></td>
        </tr>
    </table>
    
    <div class="section-title">TERMS & CONDITIONS</div>
    
    <div class="terms">
        <p><span class="terms-number">1.</span> In consideration of and subject to the Allottee(s) complying with the terms and conditions of this letter, executing and registering necessary documents and agreements under applicable law, and agreeing to make and making timely payment of amounts due, the developer allots the Flat in the project "{project}" in the favour of <span class="highlight">Mr./Mrs. {customer_name}</span>.</p>
        
        <p><span class="terms-number">2.</span> All payments to be made by A/c Payee Cheque/Banker Cheque/Pay order/Demand Draft at Bangalore only or through Electronic Fund Transfer (EFT) mode drawn in favor of/to the account of "RRL BUILDERS AND DEVELOPERS PVT LTD"</p>
        
        <div class="bank-details">
            <p><strong>Account Holder Name:</strong> RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</p>
            <p><strong>Bank:</strong> HDFC BANK</p>
            <p><strong>Branch:</strong> SOMPURA</p>
            <p><strong>Account Number:</strong> 57500001802063</p>
            <p><strong>IFSC Number:</strong> HDFC0009590</p>
        </div>
        
        <p><span class="terms-number">3.</span> The Allottee shall be liable to pay the total sale consideration (more fully described in the cost sheet) and other charges as specified herein together with the applicable government taxes and levies as per the payment plan annexed herewith, time being of the essence.</p>
        
        <p><span class="terms-number">4.</span> The Allottee has applied for booking and allotment of Flat being fully aware of the cost of the Flat, and also of the tax regime of GST. The Applicant also confirms that he/she shall not claim any GST credit and/or claim any reduction in price of the Flat due to application of GST.</p>
        
        <p><span class="terms-number">5.</span> To avoid penal consequences under the Income Tax Act 1961, the Allottee is required to comply with provisions of section 194IA of the Income Tax Act, 1961, by deduction Tax at Source (TDS) at the prevailing rate from installment/payment. The Allottee shall be required to submit TDS Certificate and challan showing proof of deposition of the same within 7 (Seven) days from the date of tax so deposited to the Developer so that the appropriate credit may be allowed to the account of the Allottee.</p>
        
        <p><span class="terms-number">6.</span> Taxation particulars of Developer is as follows:</p>
        <p style="margin-left: 20px;">PAN No: AAKCR4125J</p>
        <p style="margin-left: 20px;">GST No: 29AAKCR4125J1Z2</p>
        
        <p><span class="terms-number">7.</span> If the upfront advance is paid by cheque, the confirmation of allotment is conditional upon realization of the cheque and funds being credited to the developer's account within 7 (Seven) days of submission of the EOI. In the event the cheque is dishonored for the first time, a sum of Rs.10,000/- (Rupees Ten Thousand Only) will be debited from the Allottee's account in addition to bank charges. In the event such default repeats for the second time, a sum of Rs.20,000/- (Rupees Twenty Thousand Only) will be debited from the Allottee's account in addition to bank charges. In the event such default repeats for the third time, the developer reserves the right to terminate this letter, at sole discretion.</p>
        
        <p><span class="terms-number">8.</span> In the event of cancellation and/or termination of documents and agreements executed and registered pursuant to this Letter, the Allottee agrees to forfeit, in the Developer's favor, the application amount paid by the Allottee plus an amount equal to 5% (Five percent) of the Total Sale Consideration for the allotted Flat and amounts paid by the Allottee on account of applicable GST. The balance amount, if any, shall be refunded to the Allottee, without interest, within 60 (sixty) days from the resale of the unit to a third party.</p>
        
        <p><span class="terms-number">9.</span> Stamp duty and registration charges on actuals and as per prevailing rates shall be payable by the Allottee over and above the Total Sale Consideration.</p>
        
        <p><span class="terms-number">10.</span> In the event any amount by the Allottee is prepaid, the Developer is entitled to retain and adjust the balance/excess amounts received against the next installment due, without paying any interest on such additional amounts.</p>
        
        <p><span class="terms-number">11.</span> For this Project, the schedule of payments is linked to stage-wise completion of the Flat, which schedule has been communicated to and accepted by the Allottee at the time of submitting the EOI. The payment schedule will also be included as an annexure to the agreement of sale.</p>
        
        <p><span class="terms-number">12.</span> Any delay or default in payment by the Allottee will attract penal interest as per the Rules on the Outstanding amount calculated from the applicable due dates till the date of actual receipt.</p>
        
        <p><span class="terms-number">13.</span> This Letter is neither transferable nor assignable, without the Developer's prior written consent and upon payment of including but not limited to such administrative charges as may be specified by the Developer in this regard.</p>
        
        <p><span class="terms-number">14.</span> Pre EMI (Interest Only) will be paid by the builder till the completion of the flat or ready for interior. Rate of interest will be calculated considering 30-year tenure irrespective of client's tenure period.</p>
        
        <p><span class="terms-number">15.</span> <strong>Guidelines for External Vendors:</strong> Should you choose to engage a service provider other than the In-House Team, please be advised that the following security protocols will strictly apply to safeguard the property: Security Deposit of Rs.2,00,000 (Two Lakhs) must be maintained. The flat owner remains fully liable for any damages caused by their vendor to the premises.</p>
        
        <p><span class="terms-number">16.</span> Maintenance will be collected for 12 months, Rs. 3 Per sqft per month, should be paid before registration along with GST 18% on above maintenance. Corpus fund collected for 12 months at Rs. 2.5 Per sqft per month. Car parking will be allotted based on sequential basis.</p>
        
        <p><span class="terms-number">17.</span> These terms and conditions shall be deemed to be an integral part of the duly executed agreement for sale. Any and all disputes in relation to this Letter shall be referred exclusively to the jurisdictional Real Estate Regulatory Authority, for resolution in accordance with applicable procedure.</p>
    </div>
    
    <div class="declaration">
        <p>I/We, <span class="highlight">Mr./Mrs. {customer_name}</span> have fully read and understood the terms and conditions as set out in this Letter and Schedules hereto. I/We undertake to abide by such terms and conditions including any amendment therein from time to time. I/We further declare that the details/information provided in the Letter are true and correct.</p>
    </div>
    
    <div class="signature-section">
        <div class="signature-box">
            <p><strong>FOR RRL BUILDERS AND DEVELOPERS PVT LTD</strong></p>
            <div class="signature-line">
                <p>Authorized Signatory</p>
            </div>
        </div>
        <div class="signature-box">
            <p><strong>ALLOTTEE SIGNATURES</strong></p>
            <div class="signature-line">
                <p>{customer_name}</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p><strong>RRL Builders and Developers Pvt. Ltd.</strong></p>
        <p>www.rrlbuildersanddevelopers.com</p>
        <p>Date: {date} | Ref: {customer_id}</p>
    </div>
</body>
</html>
""",
        DocumentType.DISBURSEMENT_LETTER: """
BANK DISBURSEMENT REQUEST LETTER

Date: {date}
To,
The Manager
[Bank Name]
[Branch Address]

Subject: Request for Disbursement of Home Loan for {customer_name}

Dear Sir/Madam,

We hereby request the disbursement of the following amount towards the purchase of property by the below mentioned applicant:

APPLICANT DETAILS:
Name: {customer_name}
PAN: {pan_number}
Phone: {phone}

PROPERTY DETAILS:
Project: {project}
Tower: {tower}
Unit Number: {unit_number}
Agreement Value: Rs. {total_price}/-

The construction has reached the required stage and we request you to process the disbursement.

For RRL Builders and Developers

_______________________
Authorized Signatory
"""
    }
    return templates.get(doc_type, "Template not found")

# ==================== PDF GENERATION ====================
def generate_price_breakup_html(customer: dict) -> str:
    """Generate HTML for Price Breakup PDF with black and gold theme"""
    
    # Format currency in Indian format
    def format_inr(amount):
        """Format amount in Indian Rupee style without L/Cr abbreviations"""
        amount = float(amount) if amount else 0
        int_part = int(amount)
        decimal_part = f"{amount:.2f}".split('.')[1]
        
        # Format with Indian comma system
        s = str(int_part)
        if len(s) > 3:
            result = s[-3:]
            s = s[:-3]
            while s:
                result = s[-2:] + ',' + result
                s = s[:-2]
        else:
            result = s
        
        return f"₹{result}.{decimal_part}"
    
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #f5f5f5;
                padding: 30px;
                color: #1A1A1A;
            }}
            
            .container {{
                background: #fff;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                padding: 35px;
                max-width: 800px;
                margin: 0 auto;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #D4AF37;
                padding-bottom: 20px;
                margin-bottom: 25px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logo {{
                width: 55px;
                height: 55px;
                background: #1A1A1A;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #D4AF37;
                font-weight: bold;
                font-size: 20px;
            }}
            
            .company-name {{
                font-size: 20px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 11px;
                color: #666;
            }}
            
            .document-title {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 13px;
                text-transform: uppercase;
            }}
            
            .section {{
                margin-bottom: 20px;
            }}
            
            .section-title {{
                font-size: 14px;
                color: #1A1A1A;
                font-weight: 600;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 2px solid #D4AF37;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }}
            
            .info-item {{
                display: flex;
                justify-content: space-between;
                padding: 8px 10px;
                background: #fafafa;
                border-left: 3px solid #D4AF37;
            }}
            
            .info-label {{
                color: #666;
                font-size: 12px;
            }}
            
            .info-value {{
                color: #1A1A1A;
                font-weight: 500;
                font-size: 12px;
            }}
            
            .price-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            
            .price-table th, .price-table td {{
                padding: 12px;
                text-align: left;
                font-size: 12px;
            }}
            
            .price-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                font-weight: 500;
            }}
            
            .price-table td {{
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .price-table tr:nth-child(even) {{
                background: #fafafa;
            }}
            
            .price-table .total-row {{
                background: #1A1A1A !important;
                color: #D4AF37;
                font-weight: 700;
                font-size: 14px;
            }}
            
            .price-table .amount {{
                text-align: right;
                font-family: 'Roboto Mono', monospace;
            }}
            
            .footer {{
                margin-top: 25px;
                padding-top: 15px;
                border-top: 2px solid #D4AF37;
                font-size: 11px;
                color: #666;
            }}
            
            .footer-note {{
                margin-bottom: 8px;
            }}
            
            .footer-company {{
                margin-top: 15px;
                text-align: center;
                color: #1A1A1A;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-section">
                    <div class="logo">RRL</div>
                    <div>
                        <div class="company-name">RRL Builders and Developers</div>
                        <div class="company-tagline">Beyond homes. A lifestyle</div>
                    </div>
                </div>
                <div class="document-title">Price Break-Up</div>
            </div>
            
            <div class="section">
                <div class="section-title">Customer Details</div>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Name:</span>
                        <span class="info-value">{customer.get('name', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Contact:</span>
                        <span class="info-value">{customer.get('phone', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email:</span>
                        <span class="info-value">{customer.get('email', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Booking Date:</span>
                        <span class="info-value">{booking_date}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Unit Details</div>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Unit No.:</span>
                        <span class="info-value">{customer.get('unit_number', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Tower:</span>
                        <span class="info-value">{customer.get('tower', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Unit Type:</span>
                        <span class="info-value">{customer.get('bhk_type', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Floor:</span>
                        <span class="info-value">{customer.get('floor', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Saleable Area:</span>
                        <span class="info-value">{customer.get('saleable_area', 0)} sq.ft</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">UDS:</span>
                        <span class="info-value">{customer.get('uds', 0)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Rate/Sq.ft:</span>
                        <span class="info-value">₹{customer.get('rate_per_sqft', 0):,.0f}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Price Breakdown</div>
                <table class="price-table">
                    <thead>
                        <tr>
                            <th>Particulars</th>
                            <th class="amount">Amount (₹)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Base Price ({customer.get('saleable_area', 0)} sq.ft × ₹{customer.get('rate_per_sqft', 0):,.0f})</td>
                            <td class="amount">{format_inr(customer.get('base_price', 0))}</td>
                        </tr>
                        <tr>
                            <td>Club House, Infrastructure & One Covered Car Parking</td>
                            <td class="amount">{format_inr(customer.get('club_house_charges', 200000))}</td>
                        </tr>
                        <tr>
                            <td>Additional Car Parking ({customer.get('additional_parking', 0)} nos.)</td>
                            <td class="amount">{format_inr(customer.get('additional_parking_charges', 0))}</td>
                        </tr>
                        <tr>
                            <td>Labour Cess (0.70%)</td>
                            <td class="amount">{format_inr(customer.get('labour_cess', 0))}</td>
                        </tr>
                        <tr>
                            <td>GST (5%)</td>
                            <td class="amount">{format_inr(customer.get('gst_amount', 0))}</td>
                        </tr>
                        <tr class="total-row">
                            <td><strong>GRAND TOTAL</strong></td>
                            <td class="amount"><strong>{format_inr(customer.get('total_price', 0))}</strong></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p class="footer-note">* Maintenance charges will attract GST as applicable</p>
                <p class="footer-note">* Registration as per government norms</p>
                <p class="footer-company">
                    <strong>RRL Builders and Developers Pvt. Ltd.</strong><br>
                    www.rrlbuildersanddevelopers.com<br>
                    Thank you for choosing RRL Palm Altezze
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html



def generate_booking_form_preview_html(customer: dict) -> str:
    """Generate a PDF preview of the submitted booking form with all customer data"""
    
    # Format dates
    booking_date = customer.get('booking_date', '')
    if booking_date and '-' in str(booking_date):
        try:
            dt = datetime.strptime(str(booking_date), "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    dob = customer.get('date_of_birth', '')
    if dob and '-' in str(dob):
        try:
            dt = datetime.strptime(str(dob), "%Y-%m-%d")
            dob = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    # Format amounts
    def format_currency(amount):
        try:
            return f"₹ {float(amount or 0):,.2f}"
        except (ValueError, TypeError):
            return "₹ 0.00"
    
    # Get gender display
    gender = customer.get('gender', '')
    if gender == 'male':
        gender_display = 'Male (S/o)'
    elif gender == 'female':
        gender_display = 'Female (D/o)'
    elif gender == 'spouse':
        gender_display = 'Spouse (W/o)'
    else:
        gender_display = gender or '-'
    
    # Finance type display
    finance_type = customer.get('finance_type', 'self')
    finance_display = {
        'self': 'Self Funded',
        'loan': 'Bank Loan',
        'mixed': 'Mixed (Self + Loan)'
    }.get(finance_type, finance_type)
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #fff;
                padding: 20px 30px;
                margin: 0;
                color: #1A1A1A;
                font-size: 11px;
                line-height: 1.4;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 15px;
                border-bottom: 3px solid #D4AF37;
                margin-bottom: 20px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .logo {{
                width: 45px;
                height: 45px;
                background: linear-gradient(135deg, #1A1A1A 0%, #333 100%);
                color: #D4AF37;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 16px;
                border-radius: 6px;
            }}
            
            .company-name {{
                font-size: 16px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 9px;
                color: #D4AF37;
                font-style: italic;
            }}
            
            .document-title {{
                font-size: 18px;
                font-weight: 700;
                color: #1A1A1A;
                text-align: right;
            }}
            
            .document-subtitle {{
                font-size: 10px;
                color: #666;
                text-align: right;
            }}
            
            .section {{
                margin-bottom: 15px;
                background: #fafafa;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #eee;
            }}
            
            .section-title {{
                font-size: 12px;
                font-weight: 700;
                color: #1A1A1A;
                border-bottom: 2px solid #D4AF37;
                padding-bottom: 6px;
                margin-bottom: 10px;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 8px;
            }}
            
            .info-grid-2 {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }}
            
            .info-item {{
                padding: 4px 0;
            }}
            
            .info-label {{
                color: #666;
                font-size: 9px;
                display: block;
                margin-bottom: 2px;
            }}
            
            .info-value {{
                font-weight: 500;
                color: #1A1A1A;
                font-size: 11px;
            }}
            
            .highlight {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .price-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 8px;
            }}
            
            .price-table th, .price-table td {{
                padding: 8px;
                text-align: left;
                font-size: 10px;
            }}
            
            .price-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                font-weight: 500;
            }}
            
            .price-table td {{
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .price-table .total-row {{
                background: #1A1A1A !important;
                color: #D4AF37;
                font-weight: 700;
            }}
            
            .price-table .amount {{
                text-align: right;
            }}
            
            .footer {{
                margin-top: 20px;
                padding-top: 10px;
                border-top: 2px solid #D4AF37;
                font-size: 9px;
                color: #666;
            }}
            
            .signature-section {{
                margin-top: 30px;
                display: flex;
                justify-content: space-between;
            }}
            
            .signature-box {{
                text-align: center;
                width: 200px;
            }}
            
            .signature-line {{
                border-top: 1px solid #333;
                margin-top: 40px;
                padding-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-section">
                <div class="logo">RRL</div>
                <div>
                    <div class="company-name">RRL Builders and Developers</div>
                    <div class="company-tagline">Beyond homes. A lifestyle</div>
                </div>
            </div>
            <div>
                <div class="document-title">Booking Form Preview</div>
                <div class="document-subtitle">Customer ID: {customer.get('customer_id', '-')}</div>
            </div>
        </div>
        
        <!-- Primary Applicant Details -->
        <div class="section">
            <div class="section-title">Primary Applicant Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Full Name</span>
                    <span class="info-value">{customer.get('name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Father's/Husband's Name</span>
                    <span class="info-value">{customer.get('father_name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Gender</span>
                    <span class="info-value">{gender_display}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Date of Birth</span>
                    <span class="info-value">{dob or '-'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Phone Number</span>
                    <span class="info-value">{customer.get('phone', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Email Address</span>
                    <span class="info-value">{customer.get('email', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">PAN Number</span>
                    <span class="info-value">{customer.get('pan_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Aadhaar Number</span>
                    <span class="info-value">{customer.get('aadhar_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Nationality</span>
                    <span class="info-value">{customer.get('nationality', 'Indian')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Company</span>
                    <span class="info-value">{customer.get('company', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Designation</span>
                    <span class="info-value">{customer.get('designation', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Profession</span>
                    <span class="info-value">{customer.get('profession', '-')}</span>
                </div>
            </div>
            <div class="info-grid-2" style="margin-top: 8px;">
                <div class="info-item">
                    <span class="info-label">Permanent Address</span>
                    <span class="info-value">{customer.get('address', '-')}</span>
                </div>
            </div>
        </div>
        
        <!-- Co-Applicant Details (if exists) -->
        {f"""
        <div class="section">
            <div class="section-title">Co-Applicant Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Full Name</span>
                    <span class="info-value">{customer.get('co_applicant_name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Father's/Husband's Name</span>
                    <span class="info-value">{customer.get('co_applicant_father_name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Phone Number</span>
                    <span class="info-value">{customer.get('co_applicant_phone', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Email Address</span>
                    <span class="info-value">{customer.get('co_applicant_email', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">PAN Number</span>
                    <span class="info-value">{customer.get('co_applicant_pan', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Aadhaar Number</span>
                    <span class="info-value">{customer.get('co_applicant_aadhar', '-')}</span>
                </div>
            </div>
            <div class="info-grid-2" style="margin-top: 8px;">
                <div class="info-item">
                    <span class="info-label">Address</span>
                    <span class="info-value">{customer.get('co_applicant_address', '-')}</span>
                </div>
            </div>
        </div>
        """ if customer.get('co_applicant_name') else ''}
        
        <!-- Property Details -->
        <div class="section">
            <div class="section-title">Property Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Project</span>
                    <span class="info-value highlight">{customer.get('project', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Tower</span>
                    <span class="info-value">{customer.get('tower', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Unit Number</span>
                    <span class="info-value highlight">{customer.get('unit_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">BHK Type</span>
                    <span class="info-value">{customer.get('bhk_type', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Floor</span>
                    <span class="info-value">{customer.get('floor', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Saleable Area</span>
                    <span class="info-value">{customer.get('saleable_area', 0)} sq.ft</span>
                </div>
                <div class="info-item">
                    <span class="info-label">UDS</span>
                    <span class="info-value">{customer.get('uds', '-')} sq.ft</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Parking</span>
                    <span class="info-value">{customer.get('parking', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Additional Parking</span>
                    <span class="info-value">{customer.get('additional_parking', 0)}</span>
                </div>
            </div>
        </div>
        
        <!-- Price Details -->
        <div class="section">
            <div class="section-title">Price Details</div>
            <table class="price-table">
                <tr>
                    <th>Description</th>
                    <th class="amount">Amount</th>
                </tr>
                <tr>
                    <td>Rate per sq.ft</td>
                    <td class="amount">{format_currency(customer.get('rate_per_sqft', 0))}</td>
                </tr>
                <tr>
                    <td>Base Price ({customer.get('saleable_area', 0)} sq.ft × {format_currency(customer.get('rate_per_sqft', 0))})</td>
                    <td class="amount">{format_currency(customer.get('base_price', 0))}</td>
                </tr>
                <tr>
                    <td>Floor Rise Total</td>
                    <td class="amount">{format_currency(customer.get('floor_rise_total', 0))}</td>
                </tr>
                <tr>
                    <td>Club House Charges</td>
                    <td class="amount">{format_currency(customer.get('club_house_charges', 200000))}</td>
                </tr>
                <tr>
                    <td>Additional Charges</td>
                    <td class="amount">{format_currency(customer.get('additional_charges', 0))}</td>
                </tr>
                <tr>
                    <td>Labour Cess (0.70%)</td>
                    <td class="amount">{format_currency(customer.get('labour_cess', 0))}</td>
                </tr>
                <tr>
                    <td>GST (5%)</td>
                    <td class="amount">{format_currency(customer.get('gst_amount', 0))}</td>
                </tr>
                <tr class="total-row">
                    <td><strong>Total Flat Value</strong></td>
                    <td class="amount"><strong>{format_currency(customer.get('total_price', 0))}</strong></td>
                </tr>
            </table>
        </div>
        
        <!-- Booking & Finance Details -->
        <div class="section">
            <div class="section-title">Booking & Finance Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Booking Date</span>
                    <span class="info-value">{booking_date or '-'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Booking Amount</span>
                    <span class="info-value highlight">{format_currency(customer.get('booking_amount', 0))}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Finance Type</span>
                    <span class="info-value">{finance_display}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Finance Bank</span>
                    <span class="info-value">{customer.get('finance_bank', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Transaction Reference</span>
                    <span class="info-value">{customer.get('transaction_details', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Transaction Bank</span>
                    <span class="info-value">{customer.get('transaction_bank', '-')}</span>
                </div>
            </div>
            {f'<div class="info-item" style="margin-top: 8px;"><span class="info-label">Remarks</span><span class="info-value">{customer.get("remarks", "-")}</span></div>' if customer.get('remarks') else ''}
        </div>
        
        <!-- Signature Section -->
        <div class="signature-section">
            <div class="signature-box">
                <div class="signature-line">Customer Signature</div>
            </div>
            <div class="signature-box">
                <div class="signature-line">For RRL Builders</div>
            </div>
        </div>
        
        <div class="footer">
            <p>This is a system-generated booking form preview. Please verify all details are correct.</p>
            <p><strong>RRL Builders and Developers Pvt. Ltd.</strong> | www.rrlbuilders.in</p>
        </div>
    </body>
    </html>
    '''
    return html


def generate_terms_and_conditions_html(customer: dict) -> str:
    """Generate a Terms and Conditions PDF with the allotment letter terms"""
    
    project = customer.get('project', 'RRL Palm Altezze')
    customer_name = customer.get('name', 'Customer')
    unit_number = customer.get('unit_number', '')
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #fff;
                padding: 20px 35px;
                margin: 0;
                color: #1A1A1A;
                font-size: 10px;
                line-height: 1.5;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 15px;
                border-bottom: 3px solid #D4AF37;
                margin-bottom: 20px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .logo {{
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #1A1A1A 0%, #333 100%);
                color: #D4AF37;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 14px;
                border-radius: 6px;
            }}
            
            .company-name {{
                font-size: 14px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 8px;
                color: #D4AF37;
                font-style: italic;
            }}
            
            .document-title {{
                font-size: 16px;
                font-weight: 700;
                color: #1A1A1A;
                text-align: right;
            }}
            
            .intro {{
                margin-bottom: 15px;
                padding: 10px;
                background: #f9f9f9;
                border-left: 3px solid #D4AF37;
            }}
            
            .terms-list {{
                counter-reset: term-counter;
            }}
            
            .term-item {{
                margin-bottom: 10px;
                padding: 8px 10px;
                background: #fafafa;
                border-radius: 4px;
                border-left: 2px solid #e0e0e0;
            }}
            
            .term-item:hover {{
                border-left-color: #D4AF37;
            }}
            
            .term-number {{
                display: inline-block;
                width: 20px;
                height: 20px;
                background: #1A1A1A;
                color: #D4AF37;
                border-radius: 50%;
                text-align: center;
                line-height: 20px;
                font-weight: 600;
                font-size: 9px;
                margin-right: 8px;
            }}
            
            .term-text {{
                display: inline;
            }}
            
            .highlight {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .bank-details {{
                margin: 10px 0;
                padding: 8px;
                background: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }}
            
            .bank-details p {{
                margin: 3px 0;
            }}
            
            .acceptance {{
                margin-top: 20px;
                padding: 12px;
                background: #1A1A1A;
                color: #fff;
                border-radius: 6px;
            }}
            
            .acceptance .highlight {{
                color: #D4AF37;
            }}
            
            .signature-section {{
                margin-top: 30px;
                display: flex;
                justify-content: space-between;
            }}
            
            .signature-box {{
                text-align: center;
                width: 180px;
            }}
            
            .signature-line {{
                border-top: 1px solid #333;
                margin-top: 35px;
                padding-top: 5px;
                font-size: 9px;
            }}
            
            .footer {{
                margin-top: 15px;
                padding-top: 10px;
                border-top: 2px solid #D4AF37;
                font-size: 8px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-section">
                <div class="logo">RRL</div>
                <div>
                    <div class="company-name">RRL Builders and Developers</div>
                    <div class="company-tagline">Beyond homes. A lifestyle</div>
                </div>
            </div>
            <div class="document-title">Terms & Conditions</div>
        </div>
        
        <div class="intro">
            <p>The following Terms and Conditions govern the allotment of <span class="highlight">Unit No. {unit_number}</span> 
            in project <span class="highlight">{project}</span> to <span class="highlight">Mr./Mrs. {customer_name}</span>. 
            Please read carefully and acknowledge your understanding and acceptance.</p>
        </div>
        
        <div class="terms-list">
            <div class="term-item">
                <span class="term-number">1</span>
                <span class="term-text">In consideration of and subject to the Allottee(s) complying with the terms and conditions of this letter, executing and registering necessary documents and agreements under applicable law, and agreeing to make and making timely payment of amounts due, the developer allots the Flat in the project "{project}" in the favour of <span class="highlight">Mr./Mrs. {customer_name}</span>.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">2</span>
                <span class="term-text">All payments to be made by A/c Payee Cheque/Banker Cheque/Pay order/Demand Draft at Bangalore only or through Electronic Fund Transfer (EFT) mode drawn in favor of/to the account of <strong>"RRL BUILDERS AND DEVELOPERS PVT LTD"</strong></span>
                <div class="bank-details">
                    <p><strong>Bank:</strong> Axis Bank</p>
                    <p><strong>Account No:</strong> 922020009963054</p>
                    <p><strong>IFSC:</strong> UTIB0001504</p>
                    <p><strong>Branch:</strong> Kudlu Gate, Bangalore</p>
                </div>
            </div>
            
            <div class="term-item">
                <span class="term-number">3</span>
                <span class="term-text">The Allottee shall be liable to pay the total sale consideration (more fully described in the cost sheet) and other charges as specified herein together with the applicable government taxes and levies as per the payment plan annexed herewith, time being of the essence.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">4</span>
                <span class="term-text">The Allottee has applied for booking and allotment of Flat being fully aware of the cost of the Flat, and also of the tax regime of GST. The Applicant also confirms that he/she shall not claim any GST credit and/or claim any reduction in price of the Flat due to application of GST.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">5</span>
                <span class="term-text">To avoid penal consequences under the Income Tax Act 1961, the Allottee is required to comply with provisions of section 194IA of the Income Tax Act, 1961, by deduction Tax at Source (TDS) at the prevailing rate from installment/payment. The Allottee shall be required to submit TDS Certificate and challan showing proof of deposition of the same within 7 (Seven) days from the date of tax so deposited to the Developer.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">6</span>
                <span class="term-text">Taxation particulars of Developer: PAN - AADCR1969A | GST - 29AADCR1969A1ZW</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">7</span>
                <span class="term-text">If the upfront advance is paid by cheque, the confirmation of allotment is conditional upon realization of the cheque and funds being credited to the developer's account within 7 (Seven) days. In the event the cheque is dishonored, penalty charges will apply as per company policy.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">8</span>
                <span class="term-text">In the event of cancellation and/or termination, the Allottee agrees to forfeit, in the Developer's favor, the application amount paid plus an amount equal to 5% (Five percent) of the Total Sale Consideration and GST amounts paid. The balance amount shall be refunded within 60 days from the resale of the unit.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">9</span>
                <span class="term-text">Stamp duty and registration charges on actuals and as per prevailing rates shall be payable by the Allottee over and above the Total Sale Consideration.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">10</span>
                <span class="term-text">In the event any amount by the Allottee is prepaid, the Developer is entitled to retain and adjust the balance/excess amounts received against the next installment due, without paying any interest on such additional amounts.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">11</span>
                <span class="term-text">For this Project, the schedule of payments is linked to stage-wise completion of the Flat. The payment schedule will also be included as an annexure to the agreement of sale.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">12</span>
                <span class="term-text">Any delay or default in payment by the Allottee will attract penal interest as per the Rules on the Outstanding amount calculated from the applicable due dates till the date of actual receipt.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">13</span>
                <span class="term-text">This Letter is neither transferable nor assignable, without the Developer's prior written consent and upon payment of administrative charges as may be specified.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">14</span>
                <span class="term-text">Pre EMI (Interest Only) will be paid by the builder till the completion of the flat or ready for interior. Rate of interest will be calculated considering 30-year tenure irrespective of client's tenure period.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">15</span>
                <span class="term-text"><strong>Guidelines for External Vendors:</strong> Should you choose to engage a service provider other than the In-House Team, please be advised that a Security Deposit of Rs.2,00,000 (Two Lakhs) must be maintained. The flat owner remains fully liable for any damages caused by their vendor to the premises.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">16</span>
                <span class="term-text">Maintenance will be collected for 12 months at Rs. 3 Per sqft per month, payable before registration along with GST 18%. Corpus fund collected for 12 months at Rs. 2.5 Per sqft per month. Car parking will be allotted on sequential basis.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">17</span>
                <span class="term-text">These terms and conditions shall be deemed to be an integral part of the duly executed agreement for sale. Any disputes shall be referred exclusively to the jurisdictional Real Estate Regulatory Authority (RERA Karnataka).</span>
            </div>
        </div>
        
        <div class="acceptance">
            <p>I/We, <span class="highlight">Mr./Mrs. {customer_name}</span> have fully read and understood the terms and conditions as set out in this document. I/We undertake to abide by such terms and conditions including any amendment therein from time to time. I/We further declare that the details/information provided are true and correct.</p>
        </div>
        
        <div class="signature-section">
            <div class="signature-box">
                <div class="signature-line">Customer Signature</div>
            </div>
            <div class="signature-box">
                <div class="signature-line">Co-Applicant Signature</div>
            </div>
            <div class="signature-box">
                <div class="signature-line">For RRL Builders</div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>RRL Builders and Developers Pvt. Ltd.</strong></p>
            <p>RERA No: PRM/KA/RERA/1251/308/PR/141025/008167 | CIN: U70109KA2015PTC081706</p>
            <p>www.rrlbuilders.in</p>
        </div>
    </body>
    </html>
    '''
    return html


def generate_welcome_email_html(customer: dict) -> str:
    """Generate the welcome email HTML with black and gold theme"""
    
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #f5f5f5;
                padding: 30px;
                margin: 0;
                color: #1A1A1A;
            }}
            
            .email-container {{
                background: #fff;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                padding: 35px 45px;
                max-width: 700px;
                margin: 0 auto;
                line-height: 1.8;
            }}
            
            .header {{
                display: flex;
                align-items: center;
                gap: 15px;
                padding-bottom: 20px;
                border-bottom: 3px solid #D4AF37;
                margin-bottom: 25px;
            }}
            
            .logo {{
                width: 50px;
                height: 50px;
                background: #1A1A1A;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #D4AF37;
                font-weight: bold;
                font-size: 18px;
            }}
            
            .company-info {{
                flex: 1;
            }}
            
            .company-name {{
                font-size: 18px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 11px;
                color: #666;
            }}
            
            .greeting {{
                font-size: 18px;
                color: #1A1A1A;
                margin-bottom: 20px;
            }}
            
            .greeting span {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .flat-highlight {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .residence-details {{
                margin: 25px 0;
                padding: 20px 25px;
                background: #fafafa;
                border-left: 4px solid #D4AF37;
                border-radius: 0 8px 8px 0;
            }}
            
            .residence-details-title {{
                display: block;
                margin-bottom: 18px;
                color: #1A1A1A;
                font-size: 15px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding-bottom: 10px;
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .detail-row {{
                display: table;
                width: 100%;
                margin: 12px 0;
                font-size: 14px;
            }}
            
            .detail-label {{
                display: table-cell;
                width: 40%;
                color: #666;
                padding: 8px 0;
            }}
            
            .detail-value {{
                display: table-cell;
                width: 60%;
                font-weight: 500;
                color: #D4AF37;
                padding: 8px 0;
                text-align: right;
            }}
            
            p {{
                margin-bottom: 18px;
                color: #333;
                font-size: 14px;
            }}
            
            .signature-section {{
                margin-top: 30px;
                padding: 20px;
                background: #fafafa;
                border-radius: 8px;
            }}
            
            .signature-name {{
                font-size: 15px;
                font-weight: 600;
                color: #1A1A1A;
                margin-bottom: 3px;
            }}
            
            .signature-title {{
                font-size: 12px;
                color: #D4AF37;
                font-weight: 500;
                margin-bottom: 12px;
            }}
            
            .signature-contact {{
                font-size: 12px;
                color: #666;
                line-height: 1.6;
            }}
            
            .signature-contact a {{
                color: #D4AF37;
                text-decoration: none;
            }}
            
            .footer {{
                margin-top: 25px;
                padding-top: 20px;
                border-top: 2px solid #D4AF37;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
            
            .footer-link {{
                color: #D4AF37;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">RRL</div>
                <div class="company-info">
                    <div class="company-name">RRL Builders and Developers</div>
                    <div class="company-tagline">Beyond homes. A lifestyle</div>
                </div>
            </div>
            
            <p class="greeting">Dear <span>{customer.get('name', 'Valued Customer')}</span>,</p>
            
            <p><strong>Greetings From RRL Builders and Developers Pvt Ltd.</strong></p>
            
            <p>It is our distinct pleasure to welcome you to {customer.get('project', 'RRL Palm Altezze')} and to congratulate you on the acquisition of your Residence <span class="flat-highlight">Flat No. {customer.get('unit_number', '')}</span>.</p>
            
            <p>Your decision reflects a refined appreciation for exceptional design, uncompromising quality, and a lifestyle that goes beyond the ordinary. At RRL Builders and Developers Pvt Ltd, we create homes not merely as living spaces, but as enduring legacies—crafted with precision, discretion, and timeless elegance.</p>
            
            <p>{customer.get('project', 'RRL Palm Altezze')} has been envisioned for a select few who value privacy, sophistication, and exclusivity. Every element of your residence—from architecture and materials to amenities and services—has been thoughtfully curated to offer a living experience of rare distinction.</p>
            
            <div class="residence-details">
                <span class="residence-details-title">Residence Details</span>
                
                <div class="detail-row">
                    <span class="detail-label">Project</span>
                    <span class="detail-value">{customer.get('project', 'RRL PALM ALTEZZE').upper()}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">Residence</span>
                    <span class="detail-value">Flat No. {customer.get('unit_number', '')}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">Configuration</span>
                    <span class="detail-value">{customer.get('bhk_type', '').upper()}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">Booking Date</span>
                    <span class="detail-value">{booking_date}</span>
                </div>
            </div>
            
            <p>Your dedicated Relationship Director will connect with you personally to ensure that every interaction with us is seamless and tailored to your expectations. We remain committed to delivering not only an exceptional home, but also an ownership experience defined by transparency, attention to detail, and quiet excellence.</p>
            
            <p>Please find attached the Price Breakup document for your reference.</p>
            
            <div class="signature-section">
                <div class="signature-name">John</div>
                <div class="signature-title">CRM MANAGER</div>
                <div class="signature-contact">
                    <strong>P:</strong> 9606579135<br>
                    <strong>E:</strong> <a href="mailto:crm@rrlbuildersanddevelopers.com">crm@rrlbuildersanddevelopers.com</a><br>
                    <strong>A:</strong> 4TH Floor, RRL Tower, Sompura gate, Sarjapura Bengaluru - 562125<br><br>
                    <a href="https://www.rrlbuildersanddevelopers.com">www.rrlbuildersanddevelopers.com</a>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>RRL Builders and Developers Pvt. Ltd.</strong></p>
                <p><a href="https://www.rrlbuildersanddevelopers.com" class="footer-link">www.rrlbuildersanddevelopers.com</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

@api_router.post("/documents/generate-pdf/{customer_id}")
async def generate_price_breakup_pdf(customer_id: str, user: dict = Depends(get_current_user)):
    """Generate Price Breakup PDF for a customer"""
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate HTML
    html_content = generate_price_breakup_html(customer)
    
    # Store the generated document
    gen_doc = GeneratedDocument(
        customer_id=customer_id,
        doc_type=DocumentType.PRICE_BREAKUP,
        content=html_content,
        generated_by=user['id']
    )
    
    doc = gen_doc.model_dump()
    doc['generated_at'] = doc['generated_at'].isoformat()
    await db.generated_documents.insert_one(doc)
    
    await log_activity(user['id'], user['name'], "generate", "price_breakup_pdf", customer_id, "Generated Price Breakup PDF")
    
    # Return HTML that can be converted to PDF on frontend
    return {
        "message": "Price breakup generated",
        "document_id": gen_doc.id,
        "html_content": html_content,
        "filename": f"RRL_PalmAltezze_PriceBreakup_{customer.get('name', 'Customer').replace(' ', '_')}.pdf"
    }

@api_router.get("/communication/preview-welcome-email/{customer_id}")
async def preview_welcome_email(customer_id: str, user: dict = Depends(get_current_user)):
    """
    Preview Welcome Email with 3 PDF attachments before sending:
    1. Booking Form Preview
    2. Terms & Conditions
    3. Price Breakup
    """
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate welcome email HTML
    welcome_html = generate_welcome_email_html(customer)
    
    # Generate all 3 PDF attachment HTMLs
    form_preview_html = generate_booking_form_preview_html(customer)
    terms_conditions_html = generate_terms_and_conditions_html(customer)
    price_breakup_html = generate_price_breakup_html(customer)
    
    customer_name_safe = customer.get('name', 'Customer').replace(' ', '_')
    filename_form = f"RRL_BookingFormPreview_{customer_name_safe}.pdf"
    filename_terms = f"RRL_TermsAndConditions_{customer_name_safe}.pdf"
    filename_price = f"RRL_PriceBreakup_{customer_name_safe}.pdf"
    
    recipient_email = customer.get('email')
    subject = f"Welcome to {customer.get('project', 'RRL Builders')} - Booking Confirmation & Documents"
    
    # Default email body (editable)
    default_body = f"""Hello {customer.get('name', '')},

Greetings from RRL Builders and Developers Pvt Ltd.

It is our distinct pleasure to welcome you to {customer.get('project', 'RRL Palm Altezze')} and to congratulate you on the acquisition of your Residence Flat No. {customer.get('unit_number', '')}.

Please find attached the following documents for your reference:
1. Booking Form Preview - Your submitted booking details
2. Terms & Conditions - Important terms governing your allotment
3. Price Breakup - Detailed price calculation

Your dedicated Relationship Director will connect with you personally to ensure that every interaction with us is seamless and tailored to your expectations."""
    
    return {
        "email_type": "welcome",
        "customer_name": customer.get('name'),
        "recipient_email": recipient_email,
        "subject": subject,
        "body": default_body,
        "email_html": welcome_html,
        # 3 attachments for welcome email
        "attachment_html": form_preview_html,  # Primary attachment - Form Preview
        "attachment_filename": filename_form,
        "attachment_html_2": terms_conditions_html,  # Terms & Conditions
        "attachment_filename_2": filename_terms,
        "attachment_html_3": price_breakup_html,  # Price Breakup
        "attachment_filename_3": filename_price,
        "attachments": [filename_form, filename_terms, filename_price],
        "has_sendgrid": bool(SENDGRID_API_KEY)
    }

@api_router.get("/communication/preview-sales-agreement/{customer_id}")
async def preview_sales_agreement_email(customer_id: str, user: dict = Depends(get_current_user)):
    """
    Preview Sales Agreement Email with Sales Agreement and Price Breakup PDFs before sending.
    """
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get payment schedule for Sales Agreement
    schedule = await db.payment_schedules.find_one({"customer_id": customer_id}, {"_id": 0})
    schedule_items = schedule.get('items', []) if schedule else []
    
    # Get transaction records for payment schedule
    transactions = await db.payment_transactions.find(
        {"customer_id": customer_id}, {"_id": 0}
    ).sort("transaction_date", 1).to_list(1000)
    
    # Generate Sales Agreement HTML with transactions
    sales_agreement_html = generate_sales_agreement_html(customer, schedule_items, transactions)
    
    # Generate price breakup HTML
    price_breakup_html = generate_price_breakup_html(customer)
    
    recipient_email = customer.get('email')
    subject = f"SALE AGREEMENT DRAFT AND PRICE BREAK UP - {customer.get('unit_number', '')}"
    
    # Default email body
    default_body = f"""Hello {customer.get('name', '')},

Greetings from RRL Builders and Developers Pvt Ltd.

We are delighted to take this process ahead, please find attached draft copy of the sale agreement.

We would like to know the date when you are signing up for sale agreement.

Please review the attached documents:
1. Sale Agreement Draft
2. Price Break Up

Looking forward to your confirmation."""
    
    # Generate email HTML (same format as welcome mail)
    email_html = generate_document_email_html(customer, subject, default_body)
    
    return {
        "email_type": "sales_agreement",
        "customer_name": customer.get('name'),
        "recipient_email": recipient_email,
        "subject": subject,
        "body": default_body,
        "email_html": email_html,
        "attachment_html": sales_agreement_html,
        "attachment_html_2": price_breakup_html,
        "attachment_filename": f"RRL_SaleAgreement_{customer.get('name', 'Customer').replace(' ', '_')}.pdf",
        "attachment_filename_2": f"RRL_PriceBreakup_{customer.get('name', 'Customer').replace(' ', '_')}.pdf",
        "has_sendgrid": bool(SENDGRID_API_KEY)
    }

@api_router.get("/communication/preview-allotment-letter/{customer_id}")
async def preview_allotment_letter_email(customer_id: str, user: dict = Depends(get_current_user)):
    """
    Preview Allotment Letter Email with Allotment Letter PDF before sending.
    """
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate Allotment Letter HTML
    allotment_letter_html = generate_allotment_letter_html(customer)
    
    recipient_email = customer.get('email')
    subject = f"ALLOTMENT LETTER - {customer.get('project', 'RRL Palm Altezze')} - Flat No. {customer.get('unit_number', '')}"
    
    # Default email body
    default_body = f"""Hello {customer.get('name', '')},

Greetings from RRL Builders and Developers Pvt Ltd.

We are pleased to confirm your allotment for Flat No. {customer.get('unit_number', '')} in {customer.get('project', 'RRL Palm Altezze')}.

Please find attached your Allotment Letter for your records.

Kindly review the terms and conditions mentioned in the letter and let us know if you have any queries."""
    
    # Generate email HTML
    email_html = generate_document_email_html(customer, subject, default_body)
    
    return {
        "email_type": "allotment_letter",
        "customer_name": customer.get('name'),
        "recipient_email": recipient_email,
        "subject": subject,
        "body": default_body,
        "email_html": email_html,
        "attachment_html": allotment_letter_html,
        "attachment_filename": f"RRL_AllotmentLetter_{customer.get('name', 'Customer').replace(' ', '_')}.pdf",
        "has_sendgrid": bool(SENDGRID_API_KEY)
    }

class EmailSendRequest(BaseModel):
    email_type: str  # welcome, sales_agreement, allotment_letter
    subject: str
    body: str
    recipient_email: Optional[str] = None  # Override customer email if provided
    cc: Optional[str] = None  # CC email address

@api_router.post("/communication/send-document-email/{customer_id}")
async def send_document_email(customer_id: str, data: EmailSendRequest, user: dict = Depends(get_current_user)):
    """
    Unified endpoint to send document emails with attachments.
    Supports: welcome, sales_agreement, allotment_letter
    """
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    recipient_email = data.recipient_email or customer.get('email')
    
    # Generate email HTML based on the edited body
    email_html = generate_document_email_html(customer, data.subject, data.body)
    
    # Generate attachments based on email type
    attachments_data = []
    
    if data.email_type == "welcome":
        price_breakup_html = generate_price_breakup_html(customer)
        attachments_data.append({
            "filename": f"RRL_PriceBreakup_{customer.get('name', 'Customer').replace(' ', '_')}.pdf",
            "html": price_breakup_html,
            "doc_type": DocumentType.PRICE_BREAKUP
        })
    elif data.email_type == "sales_agreement":
        schedule = await db.payment_schedules.find_one({"customer_id": customer_id}, {"_id": 0})
        schedule_items = schedule.get('items', []) if schedule else []
        
        # Get transaction records for payment schedule
        transactions = await db.payment_transactions.find(
            {"customer_id": customer_id}, {"_id": 0}
        ).sort("transaction_date", 1).to_list(1000)
        
        sales_agreement_html = generate_sales_agreement_html(customer, schedule_items, transactions)
        price_breakup_html = generate_price_breakup_html(customer)
        
        attachments_data.append({
            "filename": f"RRL_SaleAgreement_{customer.get('name', 'Customer').replace(' ', '_')}.pdf",
            "html": sales_agreement_html,
            "doc_type": DocumentType.SALES_AGREEMENT
        })
        attachments_data.append({
            "filename": f"RRL_PriceBreakup_{customer.get('name', 'Customer').replace(' ', '_')}.pdf",
            "html": price_breakup_html,
            "doc_type": DocumentType.PRICE_BREAKUP
        })
    elif data.email_type == "allotment_letter":
        allotment_letter_html = generate_allotment_letter_html(customer)
        attachments_data.append({
            "filename": f"RRL_AllotmentLetter_{customer.get('name', 'Customer').replace(' ', '_')}.pdf",
            "html": allotment_letter_html,
            "doc_type": DocumentType.ALLOTMENT_LETTER
        })
    
    # Store generated documents
    for att in attachments_data:
        doc = GeneratedDocument(
            customer_id=customer_id,
            doc_type=att['doc_type'],
            content=att['html'],
            generated_by=user['id']
        )
        doc_dict = doc.model_dump()
        doc_dict['generated_at'] = doc_dict['generated_at'].isoformat()
        await db.generated_documents.insert_one(doc_dict)
    
    # Send via SendGrid if configured
    email_status = "pending"
    
    if SENDGRID_API_KEY:
        try:
            message = Mail(
                from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                to_emails=recipient_email,
                subject=data.subject,
                html_content=email_html
            )
            
            # Add CC if provided
            if hasattr(data, 'cc') and data.cc:
                message.add_cc(data.cc)
            
            # Generate PDFs and add as attachments
            for att in attachments_data:
                try:
                    pdf_bytes = HTML(string=att['html']).write_pdf()
                    encoded_pdf = base64.b64encode(pdf_bytes).decode()
                    
                    attachment = Attachment(
                        FileContent(encoded_pdf),
                        FileName(att['filename']),
                        FileType('application/pdf'),
                        Disposition('attachment')
                    )
                    message.add_attachment(attachment)
                    logger.info(f"Added attachment: {att['filename']}")
                except Exception as pdf_error:
                    logger.error(f"Error generating PDF attachment {att['filename']}: {str(pdf_error)}")
            
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                email_status = "sent"
                logger.info(f"{data.email_type} email sent to {recipient_email} with {len(attachments_data)} attachments")
            else:
                email_status = "failed"
                logger.error(f"Failed to send {data.email_type} email to {recipient_email}")
                
        except Exception as e:
            email_status = "error"
            logger.error(f"SendGrid error: {str(e)}")
    else:
        email_status = "simulated"
        logger.info(f"SendGrid not configured - {data.email_type} email simulated for {recipient_email}")
    
    # Log communication
    comm_log = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "type": "email",
        "subject": data.subject,
        "message": data.body,
        "status": email_status,
        "email_type": data.email_type,
        "attachments": [att['filename'] for att in attachments_data],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": user['id']
    }
    await db.communications.insert_one(comm_log)
    
    await log_activity(user['id'], user['name'], "send", "email", customer_id, f"Sent {data.email_type} email to {recipient_email}")
    
    return {
        "message": f"{data.email_type.replace('_', ' ').title()} email sent successfully",
        "status": email_status,
        "recipient": recipient_email,
        "attachments": [att['filename'] for att in attachments_data]
    }

def generate_document_email_html(customer: dict, subject: str, body: str) -> str:
    """Generate email HTML with black and gold theme - same format as welcome mail"""
    
    # Convert body with line breaks to HTML
    body_html = body.replace('\n', '<br>')
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        </style>
    </head>
    <body style="font-family: 'Roboto', Arial, sans-serif; background: #f5f5f5; padding: 30px; margin: 0; color: #1A1A1A;">
        <div style="background: #fff; border: 2px solid #D4AF37; border-radius: 8px; max-width: 700px; margin: 0 auto; overflow: hidden;">
            <!-- Header -->
            <div style="background: #1A1A1A; padding: 20px; display: flex; align-items: center;">
                <div style="background: #D4AF37; color: #1A1A1A; padding: 10px 15px; border-radius: 6px; font-weight: bold; font-size: 18px; margin-right: 15px;">RRL</div>
                <div>
                    <div style="color: #D4AF37; font-size: 18px; font-weight: 700;">RRL Builders and Developers</div>
                    <div style="color: #999; font-size: 11px;">Beyond homes. A lifestyle</div>
                </div>
            </div>
            
            <!-- Content -->
            <div style="padding: 30px 35px; line-height: 1.8;">
                <div style="font-size: 14px; color: #333;">{body_html}</div>
                
                <!-- Signature -->
                <div style="margin-top: 30px; padding: 20px; background: #fafafa; border-radius: 8px;">
                    <div style="font-size: 15px; font-weight: 600; color: #1A1A1A; margin-bottom: 3px;">John</div>
                    <div style="font-size: 12px; color: #D4AF37; font-weight: 500; margin-bottom: 12px;">CRM MANAGER</div>
                    <div style="font-size: 12px; color: #666; line-height: 1.6;">
                        <strong>P:</strong> 9606579135<br>
                        <strong>E:</strong> <a href="mailto:crm@rrlbuildersanddevelopers.com" style="color: #D4AF37;">crm@rrlbuildersanddevelopers.com</a><br>
                        <strong>A:</strong> 4TH Floor, RRL Tower, Sompura gate, Sarjapura Bengaluru - 562125<br><br>
                        <a href="https://www.rrlbuildersanddevelopers.com" style="color: #D4AF37;">www.rrlbuildersanddevelopers.com</a>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #fafafa; padding: 15px; text-align: center; font-size: 11px; color: #888; border-top: 1px solid #e0e0e0;">
                <p style="margin: 0;">RRL Builders and Developers Pvt. Ltd. | <a href="https://www.rrlbuildersanddevelopers.com" style="color: #D4AF37;">www.rrlbuildersanddevelopers.com</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

def generate_sales_agreement_html(customer: dict, schedule_items: list, transactions: list = None) -> str:
    """Generate Sales Agreement HTML with customer data filled in"""
    
    # Helper function to convert year to words
    def year_to_words(year):
        """Convert year like 2026 to 'Two Thousand and Twenty Six'"""
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
                'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
                'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        year = int(year)
        thousands = year // 1000
        hundreds = (year % 1000) // 100
        remainder = year % 100
        
        result = []
        if thousands == 2:
            result.append("Two Thousand")
        elif thousands == 1:
            result.append("One Thousand")
        
        if hundreds > 0:
            result.append(ones[hundreds] + " Hundred")
        
        if remainder > 0:
            if result:
                result.append("and")
            if remainder < 20:
                result.append(ones[remainder])
            else:
                tens_word = tens[remainder // 10]
                ones_word = ones[remainder % 10]
                if ones_word:
                    result.append(tens_word + " " + ones_word)
                else:
                    result.append(tens_word)
        
        return " ".join(result)
    
    # Format dates - "14th Day of February, Two Thousand and Twenty Six- (14-02-2026)"
    agreement_date = datetime.now()
    day_ordinal = str(agreement_date.day) + get_ordinal_suffix(agreement_date.day)
    month_name = agreement_date.strftime("%B")
    year_words = year_to_words(agreement_date.year)
    date_numeric = agreement_date.strftime("%d-%m-%Y")
    agreement_date_text = f"{day_ordinal} Day of {month_name}, {year_words}- ({date_numeric})"
    
    possession_date = "30-09-2030"  # Fixed possession date for all agreements
    
    # Format currency amounts
    def fmt(amount):
        return format_indian_currency(amount)
    
    # Calculate age from date_of_birth
    age = ""
    dob = customer.get('date_of_birth')
    if dob:
        try:
            if isinstance(dob, str):
                dob_date = datetime.strptime(dob, "%Y-%m-%d")
            else:
                dob_date = dob
            today = datetime.now()
            age = str(today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day)))
        except:
            age = ""
    
    # Generate salutation based on gender
    # S/o for male, D/o for female, W/o for spouse
    gender = customer.get('gender', '').lower() if customer.get('gender') else 'male'
    if gender == 'female':
        salutation = "D/o"
    elif gender == 'spouse':
        salutation = "W/o"
    else:
        salutation = "S/o"
    
    # Generate floor ordinal (1st, 2nd, 3rd, etc.)
    floor = customer.get('floor', 0) or 0
    floor_int = int(floor) if floor else 0
    floor_ordinal = str(floor_int) + get_ordinal_suffix(floor_int) if floor_int > 0 else "Ground"
    
    # Additional parking text
    additional_parking = customer.get('additional_parking', 0) or 0
    additional_parking_text = f" + {additional_parking} additional parking space(s)" if additional_parking > 0 else ""
    
    # Get AADHAAR number from top-level field (not custom_fields)
    aadhaar_number = customer.get('aadhar_number', '') or customer.get('aadhaar_number', '') or ''
    
    # ==================== PAYMENT SCHEDULE (Milestones from Payment Schedule Tab) ====================
    payment_schedule_rows = ""
    total = customer.get('total_price', 0) or 0
    booking_amount = customer.get('booking_amount', 0) or 0
    
    # Use schedule_items from Payment Schedule tab (the 13-point milestone schedule)
    if schedule_items and len(schedule_items) > 0:
        for i, item in enumerate(schedule_items, 1):
            milestone_name = item.get('installment_name', '') or item.get('milestone', '')
            percentage = item.get('percentage', 0) or 0
            amount = item.get('amount', 0) or 0
            
            # If amount is 0 but we have percentage and total, calculate
            if amount == 0 and percentage > 0 and total > 0:
                amount = total * percentage / 100
            
            payment_schedule_rows += f'''
            <tr>
                <td style="text-align: center;">{i}</td>
                <td>{milestone_name}</td>
                <td style="text-align: center;">{percentage}%</td>
                <td class="amount">{fmt(amount)}</td>
            </tr>
            '''
    else:
        # Use default 13-point payment schedule if no schedule_items
        default_milestones = [
            ("Initial Booking Amount (within 10 days of Booking)", 10),
            ("Post Execution of Agreement", 10),
            ("On Completion of Foundation", 10),
            ("On Completion of Podium Slab", 10),
            ("Upon Completion of 2nd Floor Roof Slab", 5),
            ("Upon Completion of 6th Floor Roof Slab", 5),
            ("Upon Completion of 10th Floor Roof Slab", 5),
            ("Upon Completion of 14th Floor Roof Slab", 5),
            ("Upon Completion of 18th Floor Roof Slab", 5),
            ("Upon Completion of 22nd Floor Roof Slab", 5),
            ("Upon Completion of Top Roof Slab", 10),
            ("Upon Completion of Flooring of Particular Property", 10),
            ("Upon Handover / Possession / Registration", 10),
        ]
        for i, (name, pct) in enumerate(default_milestones, 1):
            amount = total * pct / 100 if total > 0 else 0
            payment_schedule_rows += f'''
            <tr>
                <td style="text-align: center;">{i}</td>
                <td>{name}</td>
                <td style="text-align: center;">{pct}%</td>
                <td class="amount">{fmt(amount)}</td>
            </tr>
            '''
    
    # ==================== TRANSACTION DETAILS (All Payments Received) ====================
    transaction_rows = ""
    total_received_amount = 0
    row_num = 1
    
    # First add booking amount if exists
    if booking_amount > 0:
        total_received_amount += booking_amount
        booking_date = customer.get('booking_date', '')
        txn_bank = customer.get('transaction_bank', '') or ''
        txn_ref = customer.get('transaction_details', '') or ''
        bank_ref = f"{txn_bank} - {txn_ref}" if txn_bank or txn_ref else "Booking Payment"
        
        transaction_rows += f'''
        <tr>
            <td style="text-align: center;">{row_num}</td>
            <td>{booking_date}</td>
            <td>Booking</td>
            <td>{bank_ref}</td>
            <td class="amount">{fmt(booking_amount)}</td>
        </tr>
        '''
        row_num += 1
    
    # Add all other transactions from Payment Tracking
    if transactions and len(transactions) > 0:
        for txn in transactions:
            amount = txn.get('amount', 0) or 0
            total_received_amount += amount
            stage = (txn.get('transaction_stage', '') or '').replace('_', ' ').title()
            txn_date = txn.get('transaction_date', '')
            bank = txn.get('bank_name', '')
            txn_no = txn.get('transaction_number', '')
            
            transaction_rows += f'''
            <tr>
                <td style="text-align: center;">{row_num}</td>
                <td>{txn_date}</td>
                <td>{stage}</td>
                <td>{bank} - {txn_no}</td>
                <td class="amount">{fmt(amount)}</td>
            </tr>
            '''
            row_num += 1
    
    # If no transactions and no booking amount
    if not transaction_rows:
        transaction_rows = '''
        <tr>
            <td colspan="5" style="text-align: center; color: #666; padding: 15px;">No payments received yet</td>
        </tr>
        '''
    
    # Get template and fill in values using string replacement to avoid CSS conflicts
    template = generate_sales_agreement_template()
    
    replacements = {
        '{agreement_date_text}': agreement_date_text,
        '{customer_name}': customer.get('name', ''),
        '{age}': age,
        '{salutation}': salutation,
        '{father_name}': customer.get('father_name', ''),
        '{address}': customer.get('address', ''),
        '{aadhaar_number}': aadhaar_number,
        '{pan_number}': customer.get('pan_number', ''),
        '{phone}': customer.get('phone', ''),
        '{project}': customer.get('project', 'RRL PALM ALTEZZE'),
        '{tower}': customer.get('tower', ''),
        '{unit_number}': customer.get('unit_number', ''),
        '{floor}': str(customer.get('floor', '')),
        '{floor_ordinal}': floor_ordinal,
        '{bhk_type}': customer.get('bhk_type', ''),
        '{saleable_area}': str(customer.get('saleable_area', 0)),
        '{uds}': str(customer.get('uds', 0)),
        '{additional_parking}': str(customer.get('additional_parking', 0)),
        '{additional_parking_text}': additional_parking_text,
        '{base_price_formatted}': fmt(customer.get('base_price', 0)),
        '{club_house_formatted}': fmt(customer.get('club_house_charges', 200000)),
        '{parking_charges_formatted}': fmt(customer.get('additional_parking_charges', 0)),
        '{labour_cess_formatted}': fmt(customer.get('labour_cess', 0)),
        '{gst_formatted}': fmt(customer.get('gst_amount', 0)),
        '{total_price_formatted}': fmt(customer.get('total_price', 0)),
        '{total_price_words}': number_to_indian_words(customer.get('total_price', 0)),
        '{booking_amount_formatted}': fmt(customer.get('booking_amount', 0)),
        '{booking_amount_words}': number_to_indian_words(customer.get('booking_amount', 0)),
        '{booking_date}': customer.get('booking_date', ''),
        '{possession_date}': possession_date,
        '{payment_schedule_rows}': payment_schedule_rows,
        '{transaction_rows}': transaction_rows,
        '{total_received_formatted}': fmt(total_received_amount),
        '{date}': datetime.now().strftime("%d/%m/%Y"),
        '{customer_id}': customer.get('customer_id', '')
    }
    
    filled_html = template
    for placeholder, value in replacements.items():
        filled_html = filled_html.replace(placeholder, str(value))
    
    return filled_html

def generate_allotment_letter_html(customer: dict) -> str:
    """Generate Allotment Letter HTML with customer data filled in"""
    
    # Format booking date
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except:
            pass
    
    # Get the allotment letter template
    template = get_default_template(DocumentType.ALLOTMENT_LETTER)
    
    # Use string replacement to avoid CSS brace conflicts
    replacements = {
        '{customer_name}': customer.get('name', ''),
        '{phone}': customer.get('phone', ''),
        '{email}': customer.get('email', ''),
        '{pan_number}': customer.get('pan_number', ''),
        '{booking_date}': booking_date,
        '{unit_number}': customer.get('unit_number', ''),
        '{project}': customer.get('project', 'RRL PALM ALTEZZE'),
        '{tower}': customer.get('tower', ''),
        '{uds}': str(customer.get('uds', 0)),
        '{saleable_area}': str(customer.get('saleable_area', 0)),
        '{total_price_formatted}': format_indian_currency(customer.get('total_price', 0)),
        '{date}': datetime.now().strftime("%d/%m/%Y"),
        '{customer_id}': customer.get('customer_id', '')
    }
    
    filled_html = template
    for placeholder, value in replacements.items():
        filled_html = filled_html.replace(placeholder, str(value))
    
    return filled_html


def generate_payment_schedule_pdf_html(customer: dict, transactions: list = None) -> str:
    """Generate Payment Schedule PDF HTML with customer data and transactions"""
    
    def fmt(amount):
        """Format amount in Indian Rupee style"""
        amount = float(amount) if amount else 0
        int_part = int(amount)
        decimal_part = f"{amount:.2f}".split('.')[1]
        
        s = str(int_part)
        if len(s) > 3:
            result = s[-3:]
            s = s[:-3]
            while s:
                result = s[-2:] + ',' + result
                s = s[:-2]
        else:
            result = s
        
        return f"₹{result}.{decimal_part}"
    
    # Build transactions table
    transactions_rows = ""
    total_received = 0
    
    if transactions and len(transactions) > 0:
        for i, txn in enumerate(transactions, 1):
            amount = txn.get('amount', 0) or 0
            total_received += amount
            txn_date = txn.get('transaction_date', '-')
            bank = txn.get('bank_name', '-') or '-'
            txn_no = txn.get('transaction_number', '-') or '-'
            stage = (txn.get('transaction_stage', '-') or 'Payment').replace('_', ' ').title()
            
            transactions_rows += f'''
            <tr>
                <td style="text-align: center; padding: 10px; border: 1px solid #ddd;">{i}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{txn_date}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{stage}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{bank}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{txn_no}</td>
                <td style="text-align: right; padding: 10px; border: 1px solid #ddd;">{fmt(amount)}</td>
            </tr>
            '''
    
    total_price = customer.get('total_price', 0) or 0
    balance = total_price - total_received
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; color: #1A1A1A; }}
            .header {{ text-align: center; border-bottom: 3px solid #D4AF37; padding-bottom: 20px; margin-bottom: 20px; }}
            .header h1 {{ color: #1A1A1A; margin: 0; font-size: 24px; }}
            .header p {{ color: #666; margin: 5px 0; }}
            .customer-info {{ background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .customer-info h3 {{ color: #D4AF37; margin-top: 0; }}
            .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .info-item {{ padding: 5px 0; }}
            .info-label {{ color: #666; font-size: 12px; }}
            .info-value {{ font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #1A1A1A; color: #D4AF37; padding: 12px; text-align: left; }}
            .summary {{ margin-top: 20px; background: #1A1A1A; color: white; padding: 15px; border-radius: 8px; }}
            .summary-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #333; }}
            .summary-row:last-child {{ border-bottom: none; }}
            .summary-label {{ color: #D4AF37; }}
            .summary-value {{ font-weight: bold; }}
            .balance {{ color: #ff6b6b; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>RRL BUILDERS AND DEVELOPERS</h1>
            <p>Beyond homes. A lifestyle</p>
            <h2 style="margin-top: 15px; color: #D4AF37;">PAYMENT SCHEDULE</h2>
        </div>
        
        <div class="customer-info">
            <h3>Customer Details</h3>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Customer Name</div>
                    <div class="info-value">{customer.get('name', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Customer ID</div>
                    <div class="info-value">{customer.get('customer_id', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Project</div>
                    <div class="info-value">{customer.get('project', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Unit Number</div>
                    <div class="info-value">{customer.get('tower', '')}-{customer.get('unit_number', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Phone</div>
                    <div class="info-value">{customer.get('phone', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Email</div>
                    <div class="info-value">{customer.get('email', '-')}</div>
                </div>
            </div>
        </div>
        
        <h3>Payment Transactions</h3>
        <table>
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 15%;">Date</th>
                    <th style="width: 20%;">Type</th>
                    <th style="width: 20%;">Bank</th>
                    <th style="width: 20%;">Reference</th>
                    <th style="width: 20%; text-align: right;">Amount</th>
                </tr>
            </thead>
            <tbody>
                {transactions_rows if transactions_rows else '<tr><td colspan="6" style="text-align: center; padding: 20px; color: #666;">No transactions recorded</td></tr>'}
            </tbody>
        </table>
        
        <div class="summary">
            <div class="summary-row">
                <span class="summary-label">Total Unit Value</span>
                <span class="summary-value">{fmt(total_price)}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Total Received</span>
                <span class="summary-value" style="color: #4CAF50;">{fmt(total_received)}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Balance Pending</span>
                <span class="summary-value balance">{fmt(balance)}</span>
            </div>
        </div>
        
        <p style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
            Generated on {datetime.now().strftime("%d/%m/%Y at %H:%M")} | RRL Builders CRM
        </p>
    </body>
    </html>
    '''
    
    return html


def get_ordinal_suffix(day):
    """Get ordinal suffix for a day number"""
    if 11 <= day <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

@api_router.post("/communication/send-welcome-email/{customer_id}")
async def send_welcome_email(customer_id: str, user: dict = Depends(get_current_user)):
    """
    Send Welcome Email with 3 PDF attachments via SendGrid:
    1. Booking Form Preview - Shows all submitted form data
    2. Terms & Conditions - Allotment letter terms
    3. Price Breakup - Detailed price calculation
    """
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate welcome email HTML
    welcome_html = generate_welcome_email_html(customer)
    
    # Generate all PDF HTMLs
    price_breakup_html = generate_price_breakup_html(customer)
    form_preview_html = generate_booking_form_preview_html(customer)
    terms_conditions_html = generate_terms_and_conditions_html(customer)
    
    # Store the welcome email document
    welcome_doc = GeneratedDocument(
        customer_id=customer_id,
        doc_type=DocumentType.WELCOME_LETTER,
        content=welcome_html,
        generated_by=user['id']
    )
    
    welcome_doc_dict = welcome_doc.model_dump()
    welcome_doc_dict['generated_at'] = welcome_doc_dict['generated_at'].isoformat()
    await db.generated_documents.insert_one(welcome_doc_dict)
    
    # Store price breakup document
    price_doc = GeneratedDocument(
        customer_id=customer_id,
        doc_type=DocumentType.PRICE_BREAKUP,
        content=price_breakup_html,
        generated_by=user['id']
    )
    
    price_doc_dict = price_doc.model_dump()
    price_doc_dict['generated_at'] = price_doc_dict['generated_at'].isoformat()
    await db.generated_documents.insert_one(price_doc_dict)
    
    # File names for attachments
    customer_name_safe = customer.get('name', 'Customer').replace(' ', '_')
    filename_form_preview = f"RRL_BookingFormPreview_{customer_name_safe}.pdf"
    filename_terms = f"RRL_TermsAndConditions_{customer_name_safe}.pdf"
    filename_price = f"RRL_PriceBreakup_{customer_name_safe}.pdf"
    
    recipient_email = customer.get('email')
    subject = f"Welcome to {customer.get('project', 'RRL Builders')} - Booking Confirmation & Documents"
    
    # Send via SendGrid if configured
    email_status = "pending"
    sendgrid_response = None
    attachments_added = []
    
    if SENDGRID_API_KEY:
        try:
            message = Mail(
                from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                to_emails=recipient_email,
                subject=subject,
                html_content=welcome_html
            )
            
            # 1. Generate and attach Booking Form Preview PDF
            try:
                form_pdf_bytes = HTML(string=form_preview_html).write_pdf()
                encoded_form_pdf = base64.b64encode(form_pdf_bytes).decode()
                
                form_attachment = Attachment(
                    FileContent(encoded_form_pdf),
                    FileName(filename_form_preview),
                    FileType('application/pdf'),
                    Disposition('attachment')
                )
                message.add_attachment(form_attachment)
                attachments_added.append(filename_form_preview)
                logger.info(f"Added Booking Form Preview attachment: {filename_form_preview}")
            except Exception as pdf_error:
                logger.error(f"Error generating Form Preview PDF: {str(pdf_error)}")
            
            # 2. Generate and attach Terms & Conditions PDF
            try:
                terms_pdf_bytes = HTML(string=terms_conditions_html).write_pdf()
                encoded_terms_pdf = base64.b64encode(terms_pdf_bytes).decode()
                
                terms_attachment = Attachment(
                    FileContent(encoded_terms_pdf),
                    FileName(filename_terms),
                    FileType('application/pdf'),
                    Disposition('attachment')
                )
                message.add_attachment(terms_attachment)
                attachments_added.append(filename_terms)
                logger.info(f"Added Terms & Conditions attachment: {filename_terms}")
            except Exception as pdf_error:
                logger.error(f"Error generating Terms & Conditions PDF: {str(pdf_error)}")
            
            # 3. Generate and attach Price Breakup PDF
            try:
                price_pdf_bytes = HTML(string=price_breakup_html).write_pdf()
                encoded_price_pdf = base64.b64encode(price_pdf_bytes).decode()
                
                price_attachment = Attachment(
                    FileContent(encoded_price_pdf),
                    FileName(filename_price),
                    FileType('application/pdf'),
                    Disposition('attachment')
                )
                message.add_attachment(price_attachment)
                attachments_added.append(filename_price)
                logger.info(f"Added Price Breakup attachment: {filename_price}")
            except Exception as pdf_error:
                logger.error(f"Error generating Price Breakup PDF: {str(pdf_error)}")
            
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                email_status = "sent"
                sendgrid_response = {
                    "status_code": response.status_code, 
                    "body": f"Email sent successfully with {len(attachments_added)} attachments"
                }
                logger.info(f"Welcome email sent to {recipient_email} with {len(attachments_added)} PDFs - Status: {response.status_code}")
            else:
                email_status = "failed"
                sendgrid_response = {"status_code": response.status_code, "error": "Unexpected status code"}
                logger.error(f"Failed to send email to {recipient_email} - Status: {response.status_code}")
                
        except Exception as e:
            email_status = "failed"
            sendgrid_response = {"error": str(e)}
            logger.error(f"SendGrid error sending email to {recipient_email}: {str(e)}")
    else:
        email_status = "mocked (no API key)"
        attachments_added = [filename_form_preview, filename_terms, filename_price]
        logger.warning("SendGrid API key not configured - email not sent")
    
    # Log communication
    log = CommunicationLog(
        customer_id=customer_id,
        channel="email",
        message_type="Welcome Email",
        content=f"""
To: {recipient_email}
Subject: {subject}

[Welcome Email HTML Body]

Attachments:
1. {filename_form_preview} (Booking Form Preview)
2. {filename_terms} (Terms & Conditions)
3. {filename_price} (Price Breakup)
        """,
        status=email_status,
        sent_by=user['id']
    )
    
    log_doc = log.model_dump()
    log_doc['sent_at'] = log_doc['sent_at'].isoformat()
    await db.communication_logs.insert_one(log_doc)
    
    # Update customer stage if still pending
    if customer.get('stage') == 'pending_approval':
        await db.customers.update_one(
            {"id": customer_id},
            {"$set": {"stage": "qualified", "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    await log_activity(user['id'], user['name'], "send", "welcome_email", customer_id, f"Sent welcome email to {recipient_email} with 3 PDFs - Status: {email_status}")
    
    return {
        "message": f"Welcome email {email_status}",
        "welcome_doc_id": welcome_doc.id,
        "price_breakup_doc_id": price_doc.id,
        "email_to": recipient_email,
        "email_status": email_status,
        "attachments": attachments_added,
        "sendgrid_response": sendgrid_response
    }

@api_router.get("/documents/html/{doc_id}")
async def get_document_html(doc_id: str, user: dict = Depends(get_current_user)):
    """Get the HTML content of a generated document for preview/PDF conversion"""
    doc = await db.generated_documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": doc['id'],
        "doc_type": doc['doc_type'],
        "content": doc['content'],
        "generated_at": doc['generated_at']
    }

@api_router.get("/documents/{customer_id}")
async def get_customer_documents(customer_id: str, user: dict = Depends(get_current_user)):
    documents = await db.generated_documents.find({"customer_id": customer_id}, {"_id": 0}).to_list(100)
    return documents

@api_router.put("/documents/{doc_id}/status")
async def update_document_status(doc_id: str, status: AgreementStatus, user: dict = Depends(get_current_user)):
    result = await db.generated_documents.update_one({"id": doc_id}, {"$set": {"status": status.value}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await log_activity(user['id'], user['name'], "update", "document", doc_id, f"Status changed to {status.value}")
    return {"message": "Document status updated"}

# ==================== DOCUMENT CHECKLIST ====================
@api_router.get("/checklist/{customer_id}")
async def get_checklist(customer_id: str, user: dict = Depends(get_current_user)):
    checklist = await db.document_checklists.find_one({"customer_id": customer_id}, {"_id": 0})
    if not checklist:
        # Create default checklist
        checklist = DocumentChecklist(customer_id=customer_id)
        doc = checklist.model_dump()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.document_checklists.insert_one(doc)
        return doc
    return checklist

@api_router.put("/checklist/{customer_id}")
async def update_checklist(customer_id: str, items: Dict[str, bool], user: dict = Depends(get_current_user)):
    result = await db.document_checklists.update_one(
        {"customer_id": customer_id},
        {"$set": {"items": items, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    await log_activity(user['id'], user['name'], "update", "checklist", customer_id, "Updated document checklist")
    return {"message": "Checklist updated"}

# ==================== COMMUNICATION ====================
@api_router.post("/communication/email")
async def send_email_notification(
    customer_id: str,
    subject: str,
    message: str,
    attachment_doc_id: Optional[str] = None,
    attachment_ids: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    recipient_email = customer.get('email')
    email_status = "pending"
    sendgrid_response = None
    attachments_info = []
    
    # Process attachments if provided
    attachment_list = []
    if attachment_ids:
        doc_ids = [id.strip() for id in attachment_ids.split(",") if id.strip()]
        for doc_id in doc_ids:
            # Try to find in generated_documents first
            doc = await db.generated_documents.find_one({"id": doc_id}, {"_id": 0})
            if doc:
                attachments_info.append(f"Generated: {doc.get('doc_type', 'document')}")
            else:
                # Try customer_documents
                doc = await db.customer_documents.find_one({"id": doc_id}, {"_id": 0})
                if doc:
                    attachments_info.append(f"Uploaded: {doc.get('filename', doc.get('doc_type', 'document'))}")
    
    # Build HTML email content with black and gold theme
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        </style>
    </head>
    <body style="font-family: 'Roboto', Arial, sans-serif; line-height: 1.6; color: #1A1A1A; background: #f5f5f5; margin: 0; padding: 30px;">
        <div style="max-width: 650px; margin: 0 auto; background: #fff; border: 2px solid #D4AF37; border-radius: 8px; overflow: hidden;">
            <!-- Header -->
            <div style="background: #1A1A1A; padding: 20px; display: flex; align-items: center;">
                <div style="background: #D4AF37; color: #1A1A1A; padding: 10px 15px; border-radius: 6px; font-weight: bold; font-size: 18px; margin-right: 15px;">RRL</div>
                <div>
                    <div style="color: #D4AF37; font-size: 18px; font-weight: 700;">RRL Builders and Developers</div>
                    <div style="color: #999; font-size: 11px;">Beyond homes. A lifestyle</div>
                </div>
            </div>
            
            <!-- Content -->
            <div style="padding: 30px;">
                <p style="margin: 0 0 20px 0;">Dear {customer.get('name', 'Customer')},</p>
                <div style="white-space: pre-line; margin-bottom: 25px;">{message}</div>
                
                <!-- Signature -->
                <div style="margin-top: 30px; padding: 20px; background: #fafafa; border-radius: 8px;">
                    <div style="font-size: 15px; font-weight: 600; color: #1A1A1A; margin-bottom: 3px;">John</div>
                    <div style="font-size: 12px; color: #D4AF37; font-weight: 500; margin-bottom: 12px;">CRM MANAGER</div>
                    <div style="font-size: 12px; color: #666; line-height: 1.6;">
                        <strong>P:</strong> 9606579135<br>
                        <strong>E:</strong> <a href="mailto:crm@rrlbuildersanddevelopers.com" style="color: #D4AF37;">crm@rrlbuildersanddevelopers.com</a><br>
                        <strong>A:</strong> 4TH Floor, RRL Tower, Sompura gate, Sarjapura Bengaluru - 562125<br><br>
                        <a href="https://www.rrlbuildersanddevelopers.com" style="color: #D4AF37;">www.rrlbuildersanddevelopers.com</a>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #fafafa; padding: 15px; text-align: center; font-size: 11px; color: #888; border-top: 1px solid #e0e0e0;">
                <p style="margin: 0;">RRL Builders and Developers Pvt. Ltd. | <a href="https://www.rrlbuildersanddevelopers.com" style="color: #D4AF37;">www.rrlbuildersanddevelopers.com</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Send via SendGrid if configured
    if SENDGRID_API_KEY:
        try:
            sg_message = Mail(
                from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(sg_message)
            
            if response.status_code in [200, 201, 202]:
                email_status = "sent"
                sendgrid_response = {"status_code": response.status_code}
                logger.info(f"Email sent to {recipient_email} - Subject: {subject}")
            else:
                email_status = "failed"
                sendgrid_response = {"status_code": response.status_code}
                logger.error(f"Failed to send email to {recipient_email} - Status: {response.status_code}")
                
        except Exception as e:
            email_status = "failed"
            sendgrid_response = {"error": str(e)}
            logger.error(f"SendGrid error: {str(e)}")
    else:
        email_status = "mocked (no API key)"
    
    # Build log content with attachment info
    log_content = f"To: {recipient_email}\nSubject: {subject}\n\n{message}"
    if attachments_info:
        log_content += f"\n\nAttachments:\n- " + "\n- ".join(attachments_info)
    
    # Log the communication
    log = CommunicationLog(
        customer_id=customer_id,
        channel="email",
        message_type=subject,
        content=log_content,
        status=email_status,
        sent_by=user['id']
    )
    
    doc = log.model_dump()
    doc['sent_at'] = doc['sent_at'].isoformat()
    await db.communication_logs.insert_one(doc)
    
    await log_activity(user['id'], user['name'], "send", "email", customer_id, f"Email: {subject} - Status: {email_status}")
    
    return {"message": f"Email {email_status}", "log_id": log.id, "email_status": email_status, "sendgrid_response": sendgrid_response}

@api_router.post("/communication/whatsapp")
async def send_whatsapp_notification(
    customer_id: str,
    message: str,
    user: dict = Depends(get_current_user)
):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # MOCKED: In production, integrate with Twilio
    log = CommunicationLog(
        customer_id=customer_id,
        channel="whatsapp",
        message_type="notification",
        content=f"To: {customer['phone']}\n\n{message}",
        status="sent (MOCKED)",
        sent_by=user['id']
    )
    
    doc = log.model_dump()
    doc['sent_at'] = doc['sent_at'].isoformat()
    await db.communication_logs.insert_one(doc)
    
    await log_activity(user['id'], user['name'], "send", "whatsapp", customer_id, "WhatsApp notification")
    
    return {"message": "WhatsApp sent (MOCKED - Configure Twilio for production)", "log_id": log.id}

@api_router.get("/communication/{customer_id}")
async def get_communication_history(customer_id: str, user: dict = Depends(get_current_user)):
    logs = await db.communication_logs.find({"customer_id": customer_id}, {"_id": 0}).sort("sent_at", -1).to_list(100)
    return logs

# ==================== GOOGLE FORMS WEBHOOK ====================
@api_router.post("/webhook/google-form")
async def google_form_webhook(data: GoogleFormWebhook, background_tasks: BackgroundTasks):
    # Create customer from form data
    customer = Customer(
        name=data.customer_name,
        phone=data.phone,
        email=data.email,
        project=data.project,
        tower=data.tower,
        unit_number=data.unit_number,
        father_name=data.father_name or "",
        pan_number=data.pan_number or "",
        booking_amount=data.booking_amount or 0,
        booking_date=data.booking_date or datetime.now().strftime("%Y-%m-%d"),
        agreement_status=AgreementStatus.DRAFT
    )
    customer.customer_id = await generate_customer_id()
    
    doc = customer.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.customers.insert_one(doc)
    
    # Create default checklist
    checklist = DocumentChecklist(customer_id=customer.id)
    checklist_doc = checklist.model_dump()
    checklist_doc['updated_at'] = checklist_doc['updated_at'].isoformat()
    await db.document_checklists.insert_one(checklist_doc)
    
    # Log welcome email (MOCKED)
    welcome_log = CommunicationLog(
        customer_id=customer.id,
        channel="email",
        message_type="welcome",
        content=f"Welcome to RRL Builders! Your booking for {data.project} - {data.unit_number} has been received.",
        status="sent (MOCKED)",
        sent_by="system"
    )
    log_doc = welcome_log.model_dump()
    log_doc['sent_at'] = log_doc['sent_at'].isoformat()
    await db.communication_logs.insert_one(log_doc)
    
    await log_activity("system", "System", "create", "customer", customer.id, f"Customer created via Google Form: {customer.name}")
    
    return {"message": "Customer created successfully", "customer_id": customer.customer_id}

# ==================== DASHBOARD ====================
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    total_customers = await db.customers.count_documents({})
    pending_agreements = await db.customers.count_documents({"agreement_status": {"$in": ["draft", "sent"]}})
    
    # Calculate payments
    today = datetime.now(timezone.utc).date()
    week_end = today + timedelta(days=7)
    
    # === REVENUE CALCULATION FROM INDIVIDUAL TRANSACTION RECORDS ===
    # Sum all transaction amounts from payment_transactions collection for dynamic updates
    transactions = await db.payment_transactions.find({}, {"_id": 0, "amount": 1}).to_list(100000)
    total_revenue = sum(t.get('amount', 0) or 0 for t in transactions)
    
    # Get total flat value and balance from customers
    customers = await db.customers.find({}, {"_id": 0, "total_price": 1, "booking_amount": 1}).to_list(10000)
    total_flat_value = sum(c.get('total_price', 0) or 0 for c in customers)
    
    # Add booking amounts that might not be in transactions yet
    total_booking_amounts = sum(c.get('booking_amount', 0) or 0 for c in customers)
    
    # Check if booking amounts are already included in transactions
    # If total_revenue is much less than booking amounts, add them
    if total_revenue < total_booking_amounts:
        total_revenue = total_booking_amounts + total_revenue
    
    # Total balance = total flat value - total revenue collected
    total_balance = total_flat_value - total_revenue
    
    # Total pending = same as balance
    total_pending = total_balance
    
    # === PAYMENT SCHEDULE ANALYSIS (for due dates) ===
    schedules = await db.payment_schedules.find({}, {"_id": 0}).to_list(1000)
    
    payments_due_this_week = 0
    overdue_payments = 0
    payment_status_counts = {"pending": 0, "paid": 0, "overdue": 0, "partial": 0}
    
    for schedule in schedules:
        for item in schedule.get('items', []):
            status = item.get('payment_status', 'pending')
            payment_status_counts[status] = payment_status_counts.get(status, 0) + 1
            
            if status in ['pending', 'partial']:
                try:
                    due_date = datetime.strptime(item['due_date'], "%Y-%m-%d").date()
                    if due_date < today:
                        overdue_payments += 1
                    elif due_date <= week_end:
                        payments_due_this_week += 1
                except (ValueError, TypeError):
                    pass
    
    # Calculate pending percentage
    total_amount = total_revenue + total_pending
    pending_percentage = round((total_pending / total_amount * 100), 2) if total_amount > 0 else 0
    
    # Monthly revenue (last 6 months) - calculate from transaction dates
    monthly_revenue = []
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        month_name = month_date.strftime("%b")
        # For now, distribute evenly (can be enhanced with actual date-based calculation)
        monthly_revenue.append({"month": month_name, "revenue": total_revenue / 6 if total_revenue > 0 else 0})
    
    return DashboardStats(
        total_customers=total_customers,
        pending_agreements=pending_agreements,
        payments_due_this_week=payments_due_this_week,
        overdue_payments=overdue_payments,
        total_revenue=total_revenue if user['role'] == 'admin' else 0,
        total_pending=total_pending if user['role'] == 'admin' else 0,
        total_flat_value=total_flat_value if user['role'] == 'admin' else 0,
        total_balance=total_balance if user['role'] == 'admin' else 0,
        pending_percentage=pending_percentage if user['role'] == 'admin' else 0,
        monthly_revenue=monthly_revenue if user['role'] == 'admin' else [],
        payment_status_breakdown=payment_status_counts
    )

@api_router.get("/dashboard/recent-activities")
async def get_recent_activities(limit: int = 20, user: dict = Depends(get_current_user)):
    activities = await db.activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return activities

@api_router.get("/dashboard/upcoming-due-dates")
async def get_upcoming_due_dates(user: dict = Depends(get_current_user)):
    """
    Get customers with payment due dates in the next 5 days.
    Due date rule: 10 days from booking date.
    """
    today = datetime.now(timezone.utc).date()
    
    # Get all customers
    customers = await db.customers.find(
        {"stage": {"$ne": "pending_approval"}},
        {"_id": 0}
    ).to_list(1000)
    
    upcoming = []
    
    for customer in customers:
        booking_date_str = customer.get('booking_date')
        if not booking_date_str:
            continue
        
        try:
            # Parse booking date
            if isinstance(booking_date_str, str):
                booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
            else:
                booking_date = booking_date_str
            
            # Due date is 10 days from booking date
            due_date = booking_date + timedelta(days=10)
            
            # Check if due date is within next 5 days (including overdue up to 3 days)
            days_until_due = (due_date - today).days
            
            if -3 <= days_until_due <= 5:
                upcoming.append({
                    "customer_id": customer.get('id'),
                    "customer_name": customer.get('name'),
                    "project": customer.get('project'),
                    "unit_number": customer.get('unit_number'),
                    "booking_date": booking_date.isoformat(),
                    "due_date": due_date.isoformat(),
                    "days_until_due": days_until_due,
                    "total_price": customer.get('total_price', 0),
                    "balance_amount": customer.get('balance_amount', 0),
                })
        except Exception as e:
            logger.error(f"Error parsing dates for customer {customer.get('id')}: {e}")
            continue
    
    # Sort by due date (closest first)
    upcoming.sort(key=lambda x: x['days_until_due'])
    
    return upcoming

# ==================== ACTIVITY LOGS ====================
@api_router.get("/activity-logs")
async def get_activity_logs(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    user: dict = Depends(get_current_user)
):
    query = {}
    if entity_type:
        query["entity_type"] = entity_type
    if entity_id:
        query["entity_id"] = entity_id
    
    logs = await db.activity_logs.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    return logs

# ==================== PROJECTS (for dropdowns) ====================
@api_router.get("/projects")
async def get_projects(user: dict = Depends(get_current_user)):
    # Return predefined RRL projects
    return [
        {"name": "RRL Palm Altezze", "location": "Varthur, Bangalore"},
        {"name": "RRL NC 216", "location": "Bangalore"},
        {"name": "RRL Palacio", "location": "Medahalli, Bangalore"},
        {"name": "RRL Nature Woods", "location": "Sarjapur, Bangalore"},
        {"name": "RRL Towers", "location": "Sarjapur"},
        {"name": "RRL Complex", "location": "Attibele Sarjapur Road"}
    ]

# ==================== UNIT PRICING ====================
@api_router.post("/units")
async def create_unit_pricing(unit: UnitPricingCreate, user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    """Create a new unit with pricing"""
    unit_doc = UnitPricing(
        **unit.model_dump(),
        uds=round(unit.saleable_area * 0.495046, 2)
    )
    doc = unit_doc.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.units.insert_one(doc)
    await log_activity(user['id'], user['name'], "create", "unit", unit_doc.id, f"Created unit {unit.unit_number}")
    return {**doc, "_id": None}

@api_router.get("/units")
async def get_units(
    project: Optional[str] = None,
    tower: Optional[str] = None,
    bhk_type: Optional[str] = None,
    is_available: Optional[bool] = None,
    user: dict = Depends(get_current_user)
):
    """Get all units with optional filters"""
    query = {}
    if project:
        query["project"] = project
    if tower:
        query["tower"] = tower
    if bhk_type:
        query["bhk_type"] = bhk_type
    if is_available is not None:
        query["is_available"] = is_available
    
    units = await db.units.find(query, {"_id": 0}).to_list(1000)
    return units

@api_router.get("/units/{unit_id}")
async def get_unit(unit_id: str, user: dict = Depends(get_current_user)):
    unit = await db.units.find_one({"id": unit_id}, {"_id": 0})
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@api_router.put("/units/{unit_id}")
async def update_unit(unit_id: str, updates: Dict[str, Any], user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    # Recalculate UDS if saleable_area changed
    if 'saleable_area' in updates:
        updates['uds'] = round(updates['saleable_area'] * 0.495046, 2)
    
    result = await db.units.update_one({"id": unit_id}, {"$set": updates})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    await log_activity(user['id'], user['name'], "update", "unit", unit_id, "Updated unit")
    return {"message": "Unit updated"}

@api_router.post("/units/bulk-import")
async def bulk_import_units(units: List[UnitPricingCreate], user: dict = Depends(check_role([UserRole.ADMIN]))):
    """Bulk import units from Excel data"""
    created = 0
    for unit_data in units:
        unit_doc = UnitPricing(
            **unit_data.model_dump(),
            uds=round(unit_data.saleable_area * 0.495046, 2)
        )
        doc = unit_doc.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.units.insert_one(doc)
        created += 1
    
    await log_activity(user['id'], user['name'], "import", "units", "", f"Imported {created} units")
    return {"message": f"Imported {created} units successfully"}

# ==================== PUBLIC BOOKING FORM (No Auth Required) ====================
class BookingFormData(BaseModel):
    """Public booking form submission"""
    # Primary Applicant
    name: str
    phone: str
    email: EmailStr
    father_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None  # male, female, or spouse
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    profession: Optional[str] = None
    nationality: str = "Indian"
    
    # Co-Applicant (optional)
    co_applicant_name: Optional[str] = None
    co_applicant_father_name: Optional[str] = None
    co_applicant_phone: Optional[str] = None
    co_applicant_email: Optional[str] = None
    co_applicant_pan: Optional[str] = None
    co_applicant_aadhar: Optional[str] = None
    co_applicant_address: Optional[str] = None
    co_applicant_profession: Optional[str] = None
    co_applicant_nationality: Optional[str] = "Indian"
    
    # Property Selection
    project: str
    tower: str
    unit_number: str
    bhk_type: Optional[str] = ""
    floor: int = 0
    saleable_area: float = 0
    rate_per_sqft: float = 0
    floor_rise_cost: float = 0  # Manual floor rise cost per sqft
    parking: Optional[str] = "1"
    additional_parking: int = 0
    
    # Calculated prices (from frontend)
    total_price: float = 0
    base_price: float = 0
    floor_rise_total: float = 0
    club_house_charges: float = 200000
    additional_parking_charges: float = 0
    labour_cess: float = 0
    gst_amount: float = 0
    
    # Initial Payment Info
    booking_amount: float = 0
    transaction_details: Optional[str] = None
    transaction_date: Optional[str] = None
    transaction_bank: Optional[str] = None
    
    # Finance Preference
    finance_type: str = "self"  # self, loan, mixed
    finance_bank: Optional[str] = None
    
    # Remarks
    remarks: Optional[str] = None

@api_router.post("/public/booking-form")
async def submit_booking_form(data: BookingFormData):
    """
    Public endpoint for booking form submission.
    Creates a customer with 'pending_approval' stage.
    """
    # Use data from frontend if provided, otherwise try to get from unit database
    unit = await db.units.find_one({
        "project": data.project,
        "tower": data.tower,
        "unit_number": data.unit_number
    }, {"_id": 0})
    
    # Use frontend data first, fallback to unit data if available
    rate_per_sqft = data.rate_per_sqft if data.rate_per_sqft > 0 else (unit.get('rate_per_sqft', 0) if unit else 0)
    saleable_area = data.saleable_area if data.saleable_area > 0 else (unit.get('saleable_area', 0) if unit else 0)
    floor = data.floor if data.floor > 0 else (unit.get('floor', 0) if unit else 0)
    bhk_type = data.bhk_type if data.bhk_type else (unit.get('bhk_type', '') if unit else '')
    uds = round(saleable_area * 0.495046, 2) if saleable_area > 0 else 0
    floor_rise_cost = data.floor_rise_cost if data.floor_rise_cost > 0 else 0
    
    # Use frontend calculated prices if available, otherwise calculate
    if data.total_price > 0:
        base_price = data.base_price
        floor_rise_total = data.floor_rise_total
        club_house = data.club_house_charges
        parking_charges = data.additional_parking_charges
        labour_cess = data.labour_cess
        gst = data.gst_amount
        total_price = data.total_price
    else:
        # Base price = Total Saleable Area × Rate/sqft
        base_price = rate_per_sqft * saleable_area
        # Floor rise is manual cost per sqft × saleable area
        floor_rise_total = floor_rise_cost * saleable_area
        club_house = 200000  # Default club house
        parking_charges = data.additional_parking * 300000  # ₹3,00,000 per additional parking
        subtotal = base_price + floor_rise_total + club_house + parking_charges
        labour_cess = subtotal * 0.007  # 0.70%
        gst = subtotal * 0.05  # 5%
        total_price = subtotal + labour_cess + gst
    
    customer = Customer(
        name=data.name,
        phone=data.phone,
        email=data.email,
        father_name=data.father_name or "",
        date_of_birth=data.date_of_birth,
        gender=data.gender or "male",
        pan_number=data.pan_number or "",
        aadhar_number=data.aadhar_number or "",
        address=data.address or "",
        company=data.company,
        designation=data.designation,
        nationality=data.nationality,
        co_applicant_name=data.co_applicant_name,
        co_applicant_father_name=data.co_applicant_father_name,
        co_applicant_phone=data.co_applicant_phone,
        co_applicant_email=data.co_applicant_email,
        co_applicant_pan=data.co_applicant_pan,
        co_applicant_aadhar=data.co_applicant_aadhar,
        co_applicant_address=data.co_applicant_address,
        project=data.project,
        tower=data.tower,
        unit_number=data.unit_number,
        floor=floor,
        bhk_type=bhk_type,
        saleable_area=saleable_area,
        uds=uds,
        parking=data.parking,
        additional_parking=data.additional_parking,
        rate_per_sqft=rate_per_sqft,
        base_price=round(base_price, 2),
        club_house_charges=round(club_house, 2),
        additional_parking_charges=round(parking_charges, 2),
        labour_cess=round(labour_cess, 2),
        gst_percentage=5,
        gst_amount=round(gst, 2),
        total_price=round(total_price, 2),
        booking_amount=data.booking_amount,
        booking_date=data.transaction_date or datetime.now().strftime("%Y-%m-%d"),
        total_received=data.booking_amount,
        balance_amount=round(total_price - data.booking_amount, 2),
        payment_received_percentage=round((data.booking_amount / total_price * 100) if total_price > 0 else 0, 2),
        payment_pending_percentage=round(100 - ((data.booking_amount / total_price * 100) if total_price > 0 else 0), 2),
        finance_type=data.finance_type,
        finance_bank=data.finance_bank,
        stage="pending_approval",  # Key: starts as pending
        agreement_status="draft",
        transaction_details=data.transaction_details,
        transaction_date=data.transaction_date,
        transaction_bank=data.transaction_bank,
        remarks=data.remarks,
        custom_fields={
            "profession": data.profession or "",
            "floor_rise_cost": floor_rise_cost,
            "floor_rise_total": round(floor_rise_total, 2),
            "co_applicant_profession": data.co_applicant_profession or "",
            "co_applicant_nationality": data.co_applicant_nationality or "Indian",
        }
    )
    customer.customer_id = await generate_customer_id()
    
    doc = customer.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.customers.insert_one(doc)
    
    # Create default checklist
    checklist = DocumentChecklist(customer_id=customer.id)
    checklist_doc = checklist.model_dump()
    checklist_doc['updated_at'] = checklist_doc['updated_at'].isoformat()
    await db.document_checklists.insert_one(checklist_doc)
    
    # Mark unit as unavailable
    if unit:
        await db.units.update_one(
            {"id": unit['id']},
            {"$set": {"is_available": False}}
        )
    
    await log_activity("system", "Booking Form", "create", "customer", customer.id, f"New booking: {customer.name} for {data.project} - {data.unit_number}")
    
    # === AUTO-SEND WELCOME EMAIL WITH PRICE BREAKUP ===
    email_status = "not_sent"
    if customer.email and SENDGRID_API_KEY:
        try:
            # Generate welcome email HTML
            welcome_html = generate_welcome_email_html(doc)
            
            # Generate price breakup HTML
            price_breakup_html = generate_price_breakup_html(doc)
            
            # Create email message
            subject = f"Welcome to {customer.project} - Booking Confirmation & Terms"
            message = Mail(
                from_email=(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                to_emails=customer.email,
                subject=subject,
                html_content=welcome_html
            )
            
            # Generate and attach Price Breakup PDF
            try:
                pdf_bytes = HTML(string=price_breakup_html).write_pdf()
                encoded_pdf = base64.b64encode(pdf_bytes).decode()
                
                filename = f"RRL_PriceBreakup_{customer.name.replace(' ', '_')}.pdf"
                attachment = Attachment(
                    FileContent(encoded_pdf),
                    FileName(filename),
                    FileType('application/pdf'),
                    Disposition('attachment')
                )
                message.add_attachment(attachment)
            except Exception as pdf_error:
                logger.error(f"Error generating PDF for auto-email: {str(pdf_error)}")
            
            # Send email
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                email_status = "sent"
                logger.info(f"Auto-sent welcome email to {customer.email} for new booking")
                
                # Log communication
                log = CommunicationLog(
                    customer_id=customer.id,
                    channel="email",
                    message_type="Auto Welcome Email",
                    content=f"To: {customer.email}\nSubject: {subject}\n\n[Auto-sent on booking submission with Price Breakup PDF]",
                    status="sent",
                    sent_by="system"
                )
                log_doc = log.model_dump()
                log_doc['sent_at'] = log_doc['sent_at'].isoformat()
                await db.communication_logs.insert_one(log_doc)
            else:
                email_status = "failed"
                logger.error(f"Failed to auto-send welcome email: Status {response.status_code}")
                
        except Exception as e:
            email_status = "error"
            logger.error(f"Error auto-sending welcome email: {str(e)}")
    
    return {
        "message": "Booking submitted successfully! Our team will contact you shortly.",
        "customer_id": customer.customer_id,
        "reference_id": customer.id,
        "welcome_email_status": email_status
    }

# Public document upload endpoint (no auth required)
@api_router.post("/public/upload-document/{customer_id}")
async def public_upload_document(
    customer_id: str,
    doc_type: str = Form(...),
    file: UploadFile = File(...)
):
    """Public endpoint to upload documents for a customer during booking"""
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Read file content and convert to base64 for storage
    content = await file.read()
    base64_content = base64.b64encode(content).decode('utf-8')
    
    # Store in database
    doc_record = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "doc_type": doc_type,
        "filename": file.filename,
        "content_type": file.content_type,
        "content_base64": base64_content,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "uploaded_by": "public_booking"
    }
    
    await db.customer_documents.insert_one(doc_record)
    
    # Update customer's uploaded_documents dict
    uploaded_docs = customer.get('uploaded_documents', {})
    uploaded_docs[doc_type] = doc_record['id']
    await db.customers.update_one(
        {"id": customer_id},
        {"$set": {"uploaded_documents": uploaded_docs}}
    )
    
    await log_activity("system", "Booking Form", "upload", "document", customer_id, f"Uploaded {doc_type}")
    return {"message": "Document uploaded", "doc_id": doc_record['id']}

# ==================== LEADS MANAGEMENT (Pending Approvals) ====================
@api_router.get("/leads/pending")
async def get_pending_leads(user: dict = Depends(get_current_user)):
    """Get all customers pending approval"""
    leads = await db.customers.find(
        {"stage": "pending_approval"},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return leads

@api_router.put("/leads/{customer_id}/approve")
async def approve_lead(customer_id: str, user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    """Approve a pending lead - moves to 'qualified' stage"""
    result = await db.customers.update_one(
        {"id": customer_id, "stage": "pending_approval"},
        {"$set": {
            "stage": "qualified",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found or already approved")
    
    await log_activity(user['id'], user['name'], "approve", "lead", customer_id, "Lead approved and qualified")
    return {"message": "Lead approved successfully"}

@api_router.put("/leads/{customer_id}/reject")
async def reject_lead(customer_id: str, reason: str = "", user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    """Reject a pending lead"""
    # Get customer to release the unit
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Release the unit
    await db.units.update_one(
        {"project": customer['project'], "tower": customer['tower'], "unit_number": customer['unit_number']},
        {"$set": {"is_available": True}}
    )
    
    # Delete the customer record
    await db.customers.delete_one({"id": customer_id})
    await db.document_checklists.delete_one({"customer_id": customer_id})
    
    await log_activity(user['id'], user['name'], "reject", "lead", customer_id, f"Lead rejected: {reason}")
    return {"message": "Lead rejected and removed"}

@api_router.put("/leads/{customer_id}/stage")
async def update_lead_stage(customer_id: str, stage: str, user: dict = Depends(get_current_user)):
    """Update customer stage"""
    valid_stages = ["pending_approval", "qualified", "agreement_pending", "agreement_done", "registration_done"]
    if stage not in valid_stages:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {valid_stages}")
    
    result = await db.customers.update_one(
        {"id": customer_id},
        {"$set": {
            "stage": stage,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    await log_activity(user['id'], user['name'], "update", "customer_stage", customer_id, f"Stage changed to {stage}")
    return {"message": f"Stage updated to {stage}"}

# ==================== DOCUMENT UPLOAD ====================
@api_router.post("/customers/{customer_id}/upload-document")
async def upload_customer_document(
    customer_id: str,
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """Upload a document for a customer (PAN, Aadhaar, etc.)"""
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Read file content and convert to base64 for storage
    content = await file.read()
    base64_content = base64.b64encode(content).decode('utf-8')
    
    # Store in database
    doc_record = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "doc_type": doc_type,
        "filename": file.filename,
        "content_type": file.content_type,
        "content_base64": base64_content,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "uploaded_by": user['id']
    }
    
    await db.customer_documents.insert_one(doc_record)
    
    # Update customer's uploaded_documents dict
    uploaded_docs = customer.get('uploaded_documents', {})
    uploaded_docs[doc_type] = doc_record['id']
    await db.customers.update_one(
        {"id": customer_id},
        {"$set": {"uploaded_documents": uploaded_docs}}
    )
    
    await log_activity(user['id'], user['name'], "upload", "document", customer_id, f"Uploaded {doc_type}")
    return {"message": "Document uploaded", "doc_id": doc_record['id']}

@api_router.get("/customers/{customer_id}/documents-list")
async def get_customer_uploaded_documents(customer_id: str, user: dict = Depends(get_current_user)):
    """Get list of uploaded documents for a customer"""
    docs = await db.customer_documents.find(
        {"customer_id": customer_id},
        {"_id": 0, "content_base64": 0}  # Exclude base64 for listing
    ).to_list(100)
    return docs

@api_router.get("/documents/download/{doc_id}")
async def download_document(doc_id: str, user: dict = Depends(get_current_user)):
    """Download a specific document"""
    doc = await db.customer_documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Decode base64 content
    content = base64.b64decode(doc['content_base64'])
    
    return Response(
        content=content,
        media_type=doc.get('content_type', 'application/octet-stream'),
        headers={
            "Content-Disposition": f"attachment; filename={doc['filename']}"
        }
    )

@api_router.get("/documents/preview/{doc_id}")
async def preview_document(doc_id: str, user: dict = Depends(get_current_user)):
    """Preview a document (returns base64 for frontend display)"""
    doc = await db.customer_documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": doc['id'],
        "filename": doc['filename'],
        "content_type": doc.get('content_type', 'application/octet-stream'),
        "content_base64": doc['content_base64']
    }

# Delete generated document
@api_router.delete("/documents/{doc_id}")
async def delete_generated_document(doc_id: str, user: dict = Depends(get_current_user)):
    """Delete a generated document - restricted for accounts role"""
    # Accounts role cannot delete documents
    if user['role'] == 'accounts':
        raise HTTPException(status_code=403, detail="Accounts role cannot delete documents")
    
    doc = await db.generated_documents.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await db.generated_documents.delete_one({"id": doc_id})
    await log_activity(user['id'], user['name'], "delete", "document", doc_id, f"Deleted generated document: {doc.get('doc_type')}")
    
    return {"message": "Document deleted successfully"}

# Delete uploaded customer document
@api_router.delete("/customers/{customer_id}/documents/{doc_id}")
async def delete_uploaded_document(customer_id: str, doc_id: str, user: dict = Depends(get_current_user)):
    """Delete an uploaded customer document - restricted for accounts role"""
    # Accounts role cannot delete documents
    if user['role'] == 'accounts':
        raise HTTPException(status_code=403, detail="Accounts role cannot delete documents")
    
    doc = await db.customer_documents.find_one({"id": doc_id, "customer_id": customer_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await db.customer_documents.delete_one({"id": doc_id})
    
    # Update customer's uploaded_documents dict
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if customer:
        uploaded_docs = customer.get('uploaded_documents', {})
        # Remove the doc_id reference from uploaded_documents
        for key, val in list(uploaded_docs.items()):
            if val == doc_id:
                del uploaded_docs[key]
                break
        await db.customers.update_one(
            {"id": customer_id},
            {"$set": {"uploaded_documents": uploaded_docs}}
        )
    
    await log_activity(user['id'], user['name'], "delete", "uploaded_document", doc_id, f"Deleted uploaded document: {doc.get('filename', doc.get('doc_type'))}")
    
    return {"message": "Document deleted successfully"}

# ==================== HEALTH CHECK ====================
@api_router.get("/")
async def root():
    return {"message": "RRL Builders CRM API", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Root-level health endpoint for Kubernetes health probes
@app.get("/health")
async def root_health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# ==================== EXPORT FUNCTIONALITY ====================
@api_router.get("/export/customers/csv")
async def export_customers_csv(user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    """Export all customers data as CSV"""
    import io
    import csv
    
    customers = await db.customers.find({}, {"_id": 0}).to_list(10000)
    
    if not customers:
        raise HTTPException(status_code=404, detail="No customers found")
    
    output = io.StringIO()
    
    # Define CSV headers
    headers = [
        "Customer ID", "Name", "Email", "Phone", "Project", "Tower", "Unit Number",
        "BHK Type", "Floor", "Saleable Area", "Rate/Sqft", "Base Price", "Floor Rise Cost",
        "Club House", "Additional Parking", "Labour Cess", "GST Amount", "Total Price",
        "Booking Amount", "Booking Date", "Total Received", "Balance Amount",
        "Payment Received %", "Agreement Status", "Stage", "Father Name", "PAN Number",
        "Address", "Created At"
    ]
    
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    
    for c in customers:
        writer.writerow({
            "Customer ID": c.get('customer_id', ''),
            "Name": c.get('name', ''),
            "Email": c.get('email', ''),
            "Phone": c.get('phone', ''),
            "Project": c.get('project', ''),
            "Tower": c.get('tower', ''),
            "Unit Number": c.get('unit_number', ''),
            "BHK Type": c.get('unit_type', ''),
            "Floor": c.get('floor', ''),
            "Saleable Area": c.get('saleable_area', 0),
            "Rate/Sqft": c.get('rate_per_sqft', 0),
            "Base Price": c.get('base_price', 0),
            "Floor Rise Cost": c.get('custom_fields', {}).get('floor_rise_cost', 0),
            "Club House": c.get('club_house_charges', 0),
            "Additional Parking": c.get('additional_parking_charges', 0),
            "Labour Cess": c.get('labour_cess', 0),
            "GST Amount": c.get('gst_amount', 0),
            "Total Price": c.get('total_price', 0),
            "Booking Amount": c.get('booking_amount', 0),
            "Booking Date": c.get('booking_date', ''),
            "Total Received": c.get('total_received', 0),
            "Balance Amount": c.get('balance_amount', 0),
            "Payment Received %": c.get('payment_received_percentage', 0),
            "Agreement Status": c.get('agreement_status', ''),
            "Stage": c.get('stage', ''),
            "Father Name": c.get('father_name', ''),
            "PAN Number": c.get('pan_number', ''),
            "Address": c.get('address', ''),
            "Created At": c.get('created_at', '')
        })
    
    csv_content = output.getvalue()
    output.close()
    
    await log_activity(user['id'], user['name'], "export", "customers", "all", "Exported customers to CSV")
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=RRL_Customers_Export.csv"}
    )

@api_router.get("/export/customers/excel")
async def export_customers_excel(user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER]))):
    """Export all customers data as Excel"""
    import io
    
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        raise HTTPException(status_code=500, detail="Excel export not available. Please install openpyxl.")
    
    customers = await db.customers.find({}, {"_id": 0}).to_list(10000)
    
    if not customers:
        raise HTTPException(status_code=404, detail="No customers found")
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Customers"
    
    # Define headers
    headers = [
        "Customer ID", "Name", "Email", "Phone", "Project", "Tower", "Unit Number",
        "BHK Type", "Floor", "Saleable Area", "Rate/Sqft", "Base Price", "Floor Rise Cost",
        "Club House", "Additional Parking", "Labour Cess", "GST Amount", "Total Price",
        "Booking Amount", "Booking Date", "Total Received", "Balance Amount",
        "Payment Received %", "Agreement Status", "Stage", "Created At"
    ]
    
    # Style headers with black and gold theme
    header_fill = PatternFill(start_color="1A1A1A", end_color="1A1A1A", fill_type="solid")
    header_font = Font(color="D4AF37", bold=True, name="Roboto")
    thin_border = Border(
        left=Side(style='thin', color='D4AF37'),
        right=Side(style='thin', color='D4AF37'),
        top=Side(style='thin', color='D4AF37'),
        bottom=Side(style='thin', color='D4AF37')
    )
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        cell.border = thin_border
    
    # Add data
    for row, c in enumerate(customers, 2):
        data = [
            c.get('customer_id', ''),
            c.get('name', ''),
            c.get('email', ''),
            c.get('phone', ''),
            c.get('project', ''),
            c.get('tower', ''),
            c.get('unit_number', ''),
            c.get('unit_type', ''),
            c.get('floor', ''),
            c.get('saleable_area', 0),
            c.get('rate_per_sqft', 0),
            c.get('base_price', 0),
            c.get('custom_fields', {}).get('floor_rise_cost', 0),
            c.get('club_house_charges', 0),
            c.get('additional_parking_charges', 0),
            c.get('labour_cess', 0),
            c.get('gst_amount', 0),
            c.get('total_price', 0),
            c.get('booking_amount', 0),
            c.get('booking_date', ''),
            c.get('total_received', 0),
            c.get('balance_amount', 0),
            c.get('payment_received_percentage', 0),
            c.get('agreement_status', ''),
            c.get('stage', ''),
            c.get('created_at', '')
        ]
        for col, value in enumerate(data, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = thin_border
            cell.font = Font(name="Roboto")
    
    # Auto-adjust column widths
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[column].width = min(max_length + 2, 50)
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    await log_activity(user['id'], user['name'], "export", "customers", "all", "Exported customers to Excel")
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=RRL_Customers_Export.xlsx"}
    )

@api_router.get("/export/payments/csv")
async def export_payments_csv(user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.ACCOUNTS]))):
    """Export all payment schedules as CSV"""
    import io
    import csv
    
    schedules = await db.payment_schedules.find({}, {"_id": 0}).to_list(10000)
    customers = {c['id']: c for c in await db.customers.find({}, {"_id": 0, "id": 1, "name": 1, "customer_id": 1, "project": 1, "unit_number": 1}).to_list(10000)}
    
    output = io.StringIO()
    headers = ["Customer ID", "Customer Name", "Project", "Unit", "Installment", "Milestone", "Amount", "Due Date", "Status", "Payment Date"]
    
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    
    for schedule in schedules:
        customer = customers.get(schedule.get('customer_id'), {})
        for item in schedule.get('items', []):
            writer.writerow({
                "Customer ID": customer.get('customer_id', ''),
                "Customer Name": customer.get('name', ''),
                "Project": customer.get('project', ''),
                "Unit": customer.get('unit_number', ''),
                "Installment": item.get('installment_name', ''),
                "Milestone": item.get('milestone', ''),
                "Amount": item.get('amount', 0),
                "Due Date": item.get('due_date', ''),
                "Status": item.get('payment_status', ''),
                "Payment Date": item.get('payment_date', '')
            })
    
    csv_content = output.getvalue()
    output.close()
    
    await log_activity(user['id'], user['name'], "export", "payments", "all", "Exported payments to CSV")
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=RRL_Payments_Export.csv"}
    )

# ==================== PAYMENT SCHEDULE PDF ====================
def generate_payment_schedule_html(customer: dict, schedule_items: list) -> str:
    """Generate HTML for Payment Schedule PDF with black and gold theme"""
    
    def format_inr(amount):
        """Format amount in Indian Rupee style without L/Cr abbreviations"""
        amount = float(amount) if amount else 0
        int_part = int(amount)
        decimal_part = f"{amount:.2f}".split('.')[1]
        
        # Format with Indian comma system
        s = str(int_part)
        if len(s) > 3:
            result = s[-3:]
            s = s[:-3]
            while s:
                result = s[-2:] + ',' + result
                s = s[:-2]
        else:
            result = s
        
        return f"₹{result}.{decimal_part}"
    
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except:
            pass
    
    # Generate schedule rows
    schedule_rows = ""
    cumulative = 0
    for i, item in enumerate(schedule_items, 1):
        cumulative += item.get('amount', 0)
        status_color = "#28a745" if item.get('payment_status') == 'paid' else "#dc3545" if item.get('payment_status') == 'overdue' else "#D4AF37"
        schedule_rows += f'''
        <tr>
            <td style="text-align: center;">{i}</td>
            <td>{item.get('installment_name', '')}</td>
            <td style="text-align: center;">{item.get('percentage', 0)}%</td>
            <td style="text-align: right;">{format_inr(item.get('amount', 0))}</td>
            <td style="text-align: right; color: #D4AF37; font-weight: bold;">{format_inr(cumulative)}</td>
            <td style="text-align: center;">{item.get('due_date', '-')}</td>
            <td style="text-align: center; color: {status_color}; font-weight: bold;">{item.get('payment_status', 'pending').upper()}</td>
        </tr>
        '''
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #f5f5f5;
                padding: 30px;
                color: #1A1A1A;
            }}
            
            .container {{
                background: #fff;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                padding: 30px;
                max-width: 900px;
                margin: 0 auto;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #D4AF37;
                padding-bottom: 20px;
                margin-bottom: 25px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logo {{
                width: 60px;
                height: 60px;
                background: #1A1A1A;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #D4AF37;
                font-weight: bold;
                font-size: 24px;
            }}
            
            .company-name {{
                font-size: 22px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 12px;
                color: #666;
            }}
            
            .document-title {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 14px;
            }}
            
            .customer-info {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 25px;
                padding: 15px;
                background: #fafafa;
                border-radius: 8px;
                border-left: 4px solid #D4AF37;
            }}
            
            .info-item {{
                display: flex;
                justify-content: space-between;
            }}
            
            .info-label {{
                color: #666;
                font-size: 12px;
            }}
            
            .info-value {{
                font-weight: 500;
                color: #1A1A1A;
            }}
            
            .schedule-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            
            .schedule-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 12px 10px;
                font-weight: 500;
                font-size: 12px;
                text-transform: uppercase;
            }}
            
            .schedule-table td {{
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
                font-size: 11px;
            }}
            
            .schedule-table tr:nth-child(even) {{
                background: #fafafa;
            }}
            
            .totals-section {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 25px;
            }}
            
            .total-box {{
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }}
            
            .total-box.received {{
                background: #e8f5e9;
                border: 1px solid #28a745;
            }}
            
            .total-box.pending {{
                background: #fff3e0;
                border: 1px solid #D4AF37;
            }}
            
            .total-box.total {{
                background: #1A1A1A;
                color: #D4AF37;
            }}
            
            .total-label {{
                font-size: 11px;
                text-transform: uppercase;
            }}
            
            .total-value {{
                font-size: 18px;
                font-weight: 700;
                margin-top: 5px;
            }}
            
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                text-align: center;
                font-size: 10px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-section">
                    <div class="logo">RRL</div>
                    <div>
                        <div class="company-name">RRL Builders and Developers</div>
                        <div class="company-tagline">Beyond homes. A lifestyle</div>
                    </div>
                </div>
                <div class="document-title">PAYMENT SCHEDULE</div>
            </div>
            
            <div class="customer-info">
                <div class="info-item">
                    <span class="info-label">Customer Name</span>
                    <span class="info-value">{customer.get('name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Customer ID</span>
                    <span class="info-value">{customer.get('customer_id', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Project</span>
                    <span class="info-value">{customer.get('project', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Unit Number</span>
                    <span class="info-value">{customer.get('unit_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Total Value</span>
                    <span class="info-value">{format_inr(customer.get('total_price', 0))}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Booking Date</span>
                    <span class="info-value">{booking_date}</span>
                </div>
            </div>
            
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 35%;">Particulars</th>
                        <th style="width: 8%;">%</th>
                        <th style="width: 15%;">Amount</th>
                        <th style="width: 15%;">Cumulative</th>
                        <th style="width: 12%;">Due Date</th>
                        <th style="width: 10%;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {schedule_rows}
                </tbody>
            </table>
            
            <div class="totals-section">
                <div class="total-box received">
                    <div class="total-label">Total Received</div>
                    <div class="total-value" style="color: #28a745;">{format_inr(customer.get('total_received', 0))}</div>
                </div>
                <div class="total-box pending">
                    <div class="total-label">Balance Pending</div>
                    <div class="total-value" style="color: #D4AF37;">{format_inr(customer.get('balance_amount', 0))}</div>
                </div>
                <div class="total-box total">
                    <div class="total-label">Total Property Value</div>
                    <div class="total-value">{format_inr(customer.get('total_price', 0))}</div>
                </div>
            </div>
            
            <div class="footer">
                <p>RRL Builders and Developers Pvt Ltd | www.rrlbuildersanddevelopers.com</p>
                <p>This is a computer-generated document. Generated on {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

@api_router.post("/documents/generate-payment-schedule-pdf/{customer_id}")
async def generate_payment_schedule_pdf(customer_id: str, user: dict = Depends(get_current_user)):
    """Generate Payment Schedule PDF for a customer"""
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    schedule = await db.payment_schedules.find_one({"customer_id": customer_id}, {"_id": 0})
    schedule_items = schedule.get('items', []) if schedule else []
    
    if not schedule_items:
        raise HTTPException(status_code=404, detail="No payment schedule found. Please generate one first.")
    
    html_content = generate_payment_schedule_html(customer, schedule_items)
    
    await log_activity(user['id'], user['name'], "generate", "payment_schedule_pdf", customer_id, "Generated Payment Schedule PDF")
    
    return {
        "html": html_content,
        "filename": f"RRL_PaymentSchedule_{customer.get('name', 'Customer').replace(' ', '_')}.pdf"
    }


# ==================== ADMIN DATA RESET ENDPOINT ====================
@api_router.post("/admin/reset-data-with-seed")
async def reset_data_with_seed(user: dict = Depends(get_current_user)):
    """
    Admin-only endpoint to reset the database with seed data.
    This will DELETE all existing customers and transactions, then load seed data.
    """
    import json
    
    if user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Delete existing data
        customers_deleted = await db.customers.delete_many({})
        transactions_deleted = await db.payment_transactions.delete_many({})
        schedules_deleted = await db.payment_schedules.delete_many({})
        documents_deleted = await db.documents.delete_many({})
        
        logger.info(f"Deleted: {customers_deleted.deleted_count} customers, {transactions_deleted.deleted_count} transactions")
        
        # Load seed data
        seed_dir = os.path.dirname(os.path.abspath(__file__))
        
        customers_count = 0
        transactions_count = 0
        
        # Seed customers
        customers_file = os.path.join(seed_dir, "seed_data_customers.json")
        if os.path.exists(customers_file):
            with open(customers_file, "r") as f:
                customers_data = json.load(f)
            if customers_data:
                await db.customers.insert_many(customers_data)
                customers_count = len(customers_data)
                logger.info(f"Seeded {customers_count} customers into database")
        
        # Seed transactions
        transactions_file = os.path.join(seed_dir, "seed_data_transactions.json")
        if os.path.exists(transactions_file):
            with open(transactions_file, "r") as f:
                transactions_data = json.load(f)
            if transactions_data:
                await db.payment_transactions.insert_many(transactions_data)
                transactions_count = len(transactions_data)
                logger.info(f"Seeded {transactions_count} transactions into database")
        
        return {
            "success": True,
            "message": "Database reset and seeded successfully",
            "deleted": {
                "customers": customers_deleted.deleted_count,
                "transactions": transactions_deleted.deleted_count,
                "schedules": schedules_deleted.deleted_count,
                "documents": documents_deleted.deleted_count
            },
            "seeded": {
                "customers": customers_count,
                "transactions": transactions_count
            }
        }
    except Exception as e:
        logger.error(f"Error resetting data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting data: {str(e)}")


# Include the router in the main app - MUST be after all route definitions
app.include_router(api_router)

# Include modular routers under /api prefix
# Phase 2: These routers will gradually replace the inline routes in api_router
app.include_router(auth_router, prefix="/api")
app.include_router(auth_admin_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(customers_router, prefix="/api")
app.include_router(schedule_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")
app.include_router(calculator_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    import os
    import json
    
    # Create default admin user if not exists
    admin = await db.users.find_one({"email": "admin@rrlbuilders.com"})
    if not admin:
        admin_user = User(
            email="admin@rrlbuilders.com",
            name="Admin User",
            role=UserRole.ADMIN,
            phone="9876543210"
        )
        doc = admin_user.model_dump()
        doc['password_hash'] = hash_password("admin123")
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
        logger.info("Default admin user created: admin@rrlbuilders.com / admin123")
    
    # Create RRL CRM Admin user if not exists
    crm_admin = await db.users.find_one({"email": "crm@rrlbuildersanddevelopers.com"})
    if not crm_admin:
        crm_admin_user = User(
            email="crm@rrlbuildersanddevelopers.com",
            name="RRL CRM Admin",
            role=UserRole.ADMIN,
            phone=None
        )
        doc = crm_admin_user.model_dump()
        doc['password_hash'] = hash_password("#RRLnew2026")
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
        logger.info("RRL CRM Admin user created: crm@rrlbuildersanddevelopers.com")
    
    # Seed customer data if database is empty
    customer_count = await db.customers.count_documents({})
    if customer_count == 0:
        logger.info("No customers found. Seeding customer data...")
        # Load seed data from files
        seed_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Seed customers
        customers_file = os.path.join(seed_dir, "seed_data_customers.json")
        if os.path.exists(customers_file):
            with open(customers_file, "r") as f:
                customers_data = json.load(f)
            if customers_data:
                await db.customers.insert_many(customers_data)
                logger.info(f"Seeded {len(customers_data)} customers into database")
        
        # Seed transactions
        transactions_file = os.path.join(seed_dir, "seed_data_transactions.json")
        if os.path.exists(transactions_file):
            with open(transactions_file, "r") as f:
                transactions_data = json.load(f)
            if transactions_data:
                await db.payment_transactions.insert_many(transactions_data)
                logger.info(f"Seeded {len(transactions_data)} transactions into database")
    else:
        logger.info(f"Database already has {customer_count} customers. Skipping seed.")
    
    # Create indexes
    await db.customers.create_index("customer_id", unique=True)
    await db.customers.create_index("email")
    await db.users.create_index("email", unique=True)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
