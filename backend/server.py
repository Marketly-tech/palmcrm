from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi import status as http_status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'rrl-crm-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Create the main app
app = FastAPI(title="RRL Builders CRM API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

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

# ==================== UNIT PRICING MODEL ====================
class UnitPricing(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project: str
    tower: str
    unit_number: str
    floor: int
    bhk_type: str  # 2BHK, 3BHK
    carpet_area: float
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
    carpet_area: float
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
    carpet_area: float = 0
    saleable_area: float = 0
    uds: float = 0  # Undivided Share
    parking: Optional[str] = None
    additional_parking: int = 0  # Number of additional parking
    
    # Pricing
    rate_per_sqft: float = 0
    base_price: float = 0  # rate * saleable_area
    club_house_charges: float = 0  # Default 200000
    infrastructure_charges: float = 0
    additional_parking_charges: float = 0  # 300000 per parking
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

class PriceCalculation(BaseModel):
    """Enhanced price calculation matching the Excel formula"""
    unit_number: Optional[str] = None
    unit_type: Optional[str] = None  # 2BHK, 3BHK
    floor_number: int = 0
    saleable_area: float  # sq.ft
    rate_per_sqft: float
    include_club_house: bool = True  # Rs. 2L if true
    club_house_charges: float = 200000
    additional_parking_count: int = 0  # Rs. 3L per parking
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
    additional_parking_charges: float
    subtotal_before_taxes: float  # base + club + parking
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
    count = await db.customers.count_documents({})
    return f"RRL-{str(count + 1).zfill(5)}"

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
            {"customer_id": {"$regex": search, "$options": "i"}}
        ]
    if project:
        query["project"] = project
    if agreement_status:
        query["agreement_status"] = agreement_status
    
    customers = await db.customers.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.customers.count_documents(query)
    
    return {"customers": customers, "total": total}

@api_router.get("/customers/{customer_id}")
async def get_customer(customer_id: str, user: dict = Depends(get_current_user)):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@api_router.put("/customers/{customer_id}")
async def update_customer(customer_id: str, updates: Dict[str, Any], user: dict = Depends(get_current_user)):
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
    await log_activity(user['id'], user['name'], "update", "payment_item", item_id, "Updated payment status")
    return {"message": "Payment item updated"}

@api_router.get("/payments/overview")
async def get_payments_overview(user: dict = Depends(get_current_user)):
    today = datetime.now(timezone.utc).date()
    week_end = today + timedelta(days=7)
    
    schedules = await db.payment_schedules.find({}, {"_id": 0}).to_list(1000)
    
    pending = []
    overdue = []
    upcoming = []
    
    for schedule in schedules:
        customer = await db.customers.find_one({"id": schedule['customer_id']}, {"_id": 0, "name": 1, "customer_id": 1, "unit_number": 1})
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
    Formula: (Rate/sqft × Saleable Area) + Club House + Additional Parking + Labour Cess + GST
    """
    # Base price = Rate × Saleable Area
    base_price = data.rate_per_sqft * data.saleable_area
    
    # Club house charges (optional, default Rs. 2L)
    club_house = data.club_house_charges if data.include_club_house else 0
    
    # Additional parking charges (Rs. 3L per parking)
    additional_parking = data.additional_parking_count * data.additional_parking_rate
    
    # Subtotal before taxes
    subtotal = base_price + club_house + additional_parking
    
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
        additional_parking_charges=round(additional_parking, 2),
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
    
    template = await db.document_templates.find_one({"doc_type": data.doc_type.value}, {"_id": 0})
    if not template:
        # Use default template
        template = {"content": get_default_template(data.doc_type)}
    
    # Replace placeholders
    content = template['content']
    
    # Format total price with Indian currency format
    total_price = customer.get('total_price', 0)
    total_price_formatted = "{:,.0f}".format(total_price) if total_price else "0"
    
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
        "{carpet_area}": str(customer.get('carpet_area', 0)),
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

def get_default_template(doc_type: DocumentType) -> str:
    templates = {
        DocumentType.SALES_AGREEMENT: """
SALES AGREEMENT

Date: {date}

This Sales Agreement is entered into between RRL Builders and Developers (hereinafter "Seller") and {customer_name} S/o {father_name} (hereinafter "Buyer").

PROPERTY DETAILS:
- Project: {project}
- Tower: {tower}
- Unit Number: {unit_number}
- Carpet Area: {carpet_area} sq.ft
- Saleable Area: {saleable_area} sq.ft

CONSIDERATION:
Total Agreement Value: Rs. {total_price}/-
Booking Amount Paid: Rs. {booking_amount}/-

BUYER DETAILS:
Name: {customer_name}
PAN: {pan_number}
Phone: {phone}
Email: {email}

The Buyer agrees to the terms and conditions of this agreement and shall make payments as per the agreed schedule.

For RRL Builders and Developers                    Buyer

_______________________                             _______________________
Authorized Signatory                                {customer_name}
""",
        DocumentType.ALLOTMENT_LETTER: """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.5;
            color: #000;
            background: #fff;
            padding: 20px 40px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 14pt;
            font-weight: bold;
            text-decoration: underline;
        }
        
        .recipient {
            margin-bottom: 15px;
        }
        
        .recipient p {
            margin: 2px 0;
        }
        
        .subject {
            margin: 15px 0;
            font-weight: bold;
        }
        
        .greeting {
            margin: 10px 0;
        }
        
        .content {
            text-align: justify;
            margin: 15px 0;
        }
        
        .section-title {
            font-weight: bold;
            text-decoration: underline;
            margin: 20px 0 10px 0;
        }
        
        .terms {
            margin-left: 20px;
        }
        
        .terms p {
            margin: 10px 0;
            text-align: justify;
        }
        
        .terms-number {
            font-weight: bold;
        }
        
        table.details {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        table.details th, table.details td {
            border: 1px solid #000;
            padding: 8px 12px;
            text-align: left;
        }
        
        table.details th {
            background: #f0f0f0;
            font-weight: bold;
            width: 40%;
        }
        
        .highlight {
            background-color: #ffff00;
            padding: 2px 4px;
        }
        
        .signature-section {
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
        }
        
        .signature-box {
            width: 45%;
        }
        
        .signature-line {
            border-top: 1px solid #000;
            margin-top: 60px;
            padding-top: 5px;
        }
        
        .declaration {
            margin-top: 30px;
            padding: 15px;
            border: 1px solid #000;
        }
        
        .bank-details {
            margin: 15px 0;
            padding: 10px;
            background: #f9f9f9;
            border: 1px solid #ddd;
        }
        
        .bank-details p {
            margin: 3px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>ALLOTMENT LETTER</h1>
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
        
        <p style="margin-top: 15px;">You hereby acknowledge and confirm that the copies of title documents have been handed over to you and that you have scrutinized and are satisfied with the title of the Developer to the project being good and marketable.</p>
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
    
    <div style="margin-top: 30px; font-size: 10pt; text-align: center; color: #666;">
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
    """Generate HTML for Price Breakup PDF matching the pink template"""
    
    # Format currency in Indian format
    def format_inr(amount):
        amount = float(amount) if amount else 0
        if amount >= 10000000:  # Crores
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # Lakhs
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.2f}"
    
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
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Open Sans', sans-serif;
                background: #FFF5F7;
                padding: 40px;
            }}
            
            .container {{
                background: #FFD6E0;
                border: 3px solid #FF69B4;
                border-radius: 8px;
                padding: 40px;
                max-width: 800px;
                margin: 0 auto;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #FF69B4;
                padding-bottom: 20px;
            }}
            
            .header h1 {{
                font-family: 'Playfair Display', serif;
                color: #333;
                font-size: 28px;
                font-weight: 700;
            }}
            
            .header h2 {{
                font-family: 'Playfair Display', serif;
                color: #666;
                font-size: 18px;
                margin-top: 5px;
            }}
            
            .section {{
                margin-bottom: 25px;
            }}
            
            .section-title {{
                font-family: 'Playfair Display', serif;
                font-size: 16px;
                color: #333;
                font-weight: 600;
                margin-bottom: 10px;
                border-bottom: 1px solid #FF69B4;
                padding-bottom: 5px;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }}
            
            .info-item {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px dashed #FFB6C1;
            }}
            
            .info-label {{
                color: #666;
                font-size: 14px;
            }}
            
            .info-value {{
                color: #333;
                font-weight: 600;
                font-size: 14px;
            }}
            
            .price-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            
            .price-table th, .price-table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #FFB6C1;
            }}
            
            .price-table th {{
                background: #FFB6C1;
                color: #333;
                font-weight: 600;
            }}
            
            .price-table tr:hover {{
                background: #FFE4E9;
            }}
            
            .price-table .total-row {{
                background: #FF69B4;
                color: white;
                font-weight: 700;
                font-size: 16px;
            }}
            
            .price-table .amount {{
                text-align: right;
                font-family: monospace;
            }}
            
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #FF69B4;
                font-size: 12px;
                color: #666;
            }}
            
            .footer-note {{
                font-style: italic;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>RRL PALM ALTEZZE</h1>
                <h2>PRICE BREAK-UP AND UNIT DETAILS</h2>
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
                        <span class="info-label">Carpet Area:</span>
                        <span class="info-value">{customer.get('carpet_area', 0)} sq.ft</span>
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
                <p style="margin-top: 20px; text-align: center;">
                    <strong>RRL Builders and Developers Pvt. Ltd.</strong><br>
                    Thank you for choosing RRL Palm Altezze
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

def generate_welcome_email_html(customer: dict) -> str:
    """Generate the pink welcome email HTML matching the screenshot"""
    
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
            @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@500;600&family=Open+Sans:wght@400;500&display=swap');
            
            body {{
                font-family: 'Open Sans', sans-serif;
                background: #FFF5F7;
                padding: 40px;
                margin: 0;
            }}
            
            .email-container {{
                background: #FFD6E0;
                border: 3px solid #FF69B4;
                border-radius: 4px;
                padding: 40px 50px;
                max-width: 700px;
                margin: 0 auto;
                line-height: 1.8;
            }}
            
            .greeting {{
                font-family: 'Dancing Script', cursive;
                font-size: 24px;
                color: #8B008B;
                margin-bottom: 20px;
            }}
            
            .company-name {{
                font-weight: 600;
            }}
            
            .flat-highlight {{
                font-family: 'Dancing Script', cursive;
                font-style: italic;
                font-weight: 600;
            }}
            
            .residence-details {{
                margin: 25px 0;
                padding: 15px 0;
            }}
            
            .residence-details strong {{
                display: block;
                margin-bottom: 10px;
            }}
            
            .detail-line {{
                margin: 5px 0;
                padding-left: 10px;
            }}
            
            .detail-value {{
                font-family: 'Dancing Script', cursive;
                font-weight: 600;
                color: #8B008B;
            }}
            
            p {{
                margin-bottom: 20px;
                color: #333;
                font-size: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <p class="greeting">Dear, <span class="detail-value">{customer.get('name', 'Valued Customer')}</span></p>
            
            <p><strong class="company-name">Greetings From RRL Builders and Developers Pvt Ltd.</strong></p>
            
            <p>It is our distinct pleasure to welcome you to {customer.get('project', 'RRL Palm Altezze')} and to congratulate you on the acquisition of your Residence <span class="flat-highlight">Flat No. {customer.get('unit_number', '')}</span>.</p>
            
            <p>Your decision reflects a refined appreciation for exceptional design, uncompromising quality, and a lifestyle that goes beyond the ordinary. At RRL Builders and Developers Pvt Ltd, we create homes not merely as living spaces, but as enduring legacies—crafted with precision, discretion, and timeless elegance.</p>
            
            <p>{customer.get('project', 'RRL Palm Altezze')} has been envisioned for a select few who value privacy, sophistication, and exclusivity. Every element of your residence—from architecture and materials to amenities and services—has been thoughtfully curated to offer a living experience of rare distinction.</p>
            
            <div class="residence-details">
                <strong>Residence Details:</strong>
                <div class="detail-line">Project: <span class="detail-value">{customer.get('project', 'RRL PALM ALTEZZE').upper()}</span></div>
                <div class="detail-line">Residence: <span class="detail-value">Flat NO: {customer.get('unit_number', '')}</span></div>
                <div class="detail-line">Configuration: <span class="detail-value">{customer.get('bhk_type', '').upper()}</span></div>
                <div class="detail-line">Booking Date: <span class="detail-value">{booking_date}</span></div>
            </div>
            
            <p>Your dedicated Relationship Director will connect with you personally to ensure that every interaction with us is seamless and tailored to your expectations. We remain committed to delivering not only an exceptional home, but also an ownership experience defined by transparency, attention to detail, and quiet excellence.</p>
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

@api_router.post("/communication/send-welcome-email/{customer_id}")
async def send_welcome_email(customer_id: str, user: dict = Depends(get_current_user)):
    """
    Send Welcome Email with Price Breakup PDF attachment.
    Currently MOCKED - logs the email content for testing.
    """
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate welcome email HTML
    welcome_html = generate_welcome_email_html(customer)
    
    # Generate price breakup HTML (for PDF attachment)
    price_breakup_html = generate_price_breakup_html(customer)
    
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
    
    # Log communication (MOCKED)
    filename = f"RRL_PalmAltezze_PriceBreakup_{customer.get('name', 'Customer').replace(' ', '_')}.pdf"
    
    log = CommunicationLog(
        customer_id=customer_id,
        channel="email",
        message_type="Welcome Email",
        content=f"""
To: {customer.get('email')}
Subject: Welcome to RRL Palm Altezze - Booking Confirmation

[Welcome Email HTML Body - Pink themed]

Attachment: {filename}
        """,
        status="sent (MOCKED)",
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
    
    await log_activity(user['id'], user['name'], "send", "welcome_email", customer_id, f"Sent welcome email to {customer.get('email')}")
    
    return {
        "message": "Welcome email sent (MOCKED - Configure SendGrid for production)",
        "welcome_doc_id": welcome_doc.id,
        "price_breakup_doc_id": price_doc.id,
        "email_to": customer.get('email'),
        "attachment_filename": filename,
        "welcome_html": welcome_html,
        "price_breakup_html": price_breakup_html
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
    user: dict = Depends(get_current_user)
):
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # MOCKED: In production, integrate with SendGrid
    # For now, log the communication
    log = CommunicationLog(
        customer_id=customer_id,
        channel="email",
        message_type=subject,
        content=f"To: {customer['email']}\nSubject: {subject}\n\n{message}",
        status="sent (MOCKED)",
        sent_by=user['id']
    )
    
    doc = log.model_dump()
    doc['sent_at'] = doc['sent_at'].isoformat()
    await db.communication_logs.insert_one(doc)
    
    await log_activity(user['id'], user['name'], "send", "email", customer_id, f"Email: {subject}")
    
    return {"message": "Email sent (MOCKED - Configure SendGrid for production)", "log_id": log.id}

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
    
    schedules = await db.payment_schedules.find({}, {"_id": 0}).to_list(1000)
    
    payments_due_this_week = 0
    overdue_payments = 0
    total_revenue = 0
    
    payment_status_counts = {"pending": 0, "paid": 0, "overdue": 0, "partial": 0}
    
    for schedule in schedules:
        for item in schedule.get('items', []):
            status = item.get('payment_status', 'pending')
            payment_status_counts[status] = payment_status_counts.get(status, 0) + 1
            
            if status == 'paid':
                total_revenue += item.get('amount', 0)
            elif status != 'paid':
                try:
                    due_date = datetime.strptime(item['due_date'], "%Y-%m-%d").date()
                    if due_date < today:
                        overdue_payments += 1
                    elif due_date <= week_end:
                        payments_due_this_week += 1
                except (ValueError, TypeError):
                    pass
    
    # Monthly revenue (last 6 months)
    monthly_revenue = []
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        month_name = month_date.strftime("%b")
        # In production, calculate actual revenue per month
        monthly_revenue.append({"month": month_name, "revenue": total_revenue / 6 if total_revenue > 0 else 0})
    
    return DashboardStats(
        total_customers=total_customers,
        pending_agreements=pending_agreements,
        payments_due_this_week=payments_due_this_week,
        overdue_payments=overdue_payments,
        total_revenue=total_revenue if user['role'] == 'admin' else 0,
        monthly_revenue=monthly_revenue if user['role'] == 'admin' else [],
        payment_status_breakdown=payment_status_counts
    )

@api_router.get("/dashboard/recent-activities")
async def get_recent_activities(limit: int = 20, user: dict = Depends(get_current_user)):
    activities = await db.activity_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return activities

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
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    nationality: str = "Indian"
    
    # Co-Applicant (optional)
    co_applicant_name: Optional[str] = None
    co_applicant_phone: Optional[str] = None
    co_applicant_email: Optional[str] = None
    co_applicant_pan: Optional[str] = None
    co_applicant_aadhar: Optional[str] = None
    
    # Property Selection
    project: str
    tower: str
    unit_number: str
    bhk_type: Optional[str] = ""
    floor: int = 0
    carpet_area: float = 0
    saleable_area: float = 0
    rate_per_sqft: float = 0
    parking: Optional[str] = "1"
    additional_parking: int = 0
    
    # Calculated prices (from frontend)
    total_price: float = 0
    base_price: float = 0
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
    carpet_area = data.carpet_area if data.carpet_area > 0 else (unit.get('carpet_area', 0) if unit else 0)
    floor = data.floor if data.floor > 0 else (unit.get('floor', 0) if unit else 0)
    bhk_type = data.bhk_type if data.bhk_type else (unit.get('bhk_type', '') if unit else '')
    uds = round(saleable_area * 0.495046, 2) if saleable_area > 0 else 0
    
    # Calculate floor rise (₹50/sqft per floor)
    floor_rise_per_sqft = floor * 50
    effective_rate = rate_per_sqft + floor_rise_per_sqft
    
    # Use frontend calculated prices if available, otherwise calculate
    if data.total_price > 0:
        base_price = data.base_price
        club_house = data.club_house_charges
        parking_charges = data.additional_parking_charges
        labour_cess = data.labour_cess
        gst = data.gst_amount
        total_price = data.total_price
    else:
        base_price = effective_rate * saleable_area
        club_house = 200000  # Default club house
        parking_charges = data.additional_parking * 300000  # ₹3L per additional parking
        subtotal = base_price + club_house + parking_charges
        labour_cess = subtotal * 0.007  # 0.70%
        gst = subtotal * 0.05  # 5%
        total_price = subtotal + labour_cess + gst
    
    customer = Customer(
        name=data.name,
        phone=data.phone,
        email=data.email,
        father_name=data.father_name or "",
        date_of_birth=data.date_of_birth,
        pan_number=data.pan_number or "",
        aadhar_number=data.aadhar_number or "",
        address=data.address or "",
        company=data.company,
        designation=data.designation,
        nationality=data.nationality,
        co_applicant_name=data.co_applicant_name,
        co_applicant_phone=data.co_applicant_phone,
        co_applicant_email=data.co_applicant_email,
        co_applicant_pan=data.co_applicant_pan,
        co_applicant_aadhar=data.co_applicant_aadhar,
        project=data.project,
        tower=data.tower,
        unit_number=data.unit_number,
        floor=floor,
        bhk_type=bhk_type,
        carpet_area=carpet_area,
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
    
    return {
        "message": "Booking submitted successfully! Our team will contact you shortly.",
        "customer_id": customer.customer_id,
        "reference_id": customer.id
    }

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

# ==================== HEALTH CHECK ====================
@api_router.get("/")
async def root():
    return {"message": "RRL Builders CRM API", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
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
    
    # Create indexes
    await db.customers.create_index("customer_id", unique=True)
    await db.customers.create_index("email")
    await db.users.create_index("email", unique=True)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
