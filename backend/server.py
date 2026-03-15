from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, BackgroundTasks
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
from fastapi.responses import StreamingResponse

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

class AgreementStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    SIGNED = "signed"
    COMPLETED = "completed"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIAL = "partial"

class DocumentType(str, Enum):
    SALES_AGREEMENT = "sales_agreement"
    ALLOTMENT_LETTER = "allotment_letter"
    DISBURSEMENT_LETTER = "disbursement_letter"

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
    name: str
    phone: str
    email: EmailStr
    father_name: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    project: str
    tower: str
    unit_number: str
    carpet_area: float = 0
    saleable_area: float = 0
    parking: Optional[str] = None
    total_price: float = 0
    booking_amount: float = 0
    booking_date: Optional[str] = None
    agreement_status: AgreementStatus = AgreementStatus.DRAFT
    bank_loan_status: Optional[str] = None
    custom_fields: Dict[str, Any] = {}

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
    carpet_area: float
    rate_per_sqft: float
    floor_rise_charges: float = 0
    parking_charges: float = 0
    gst_percentage: float = 5
    other_charges: float = 0

class PriceResult(BaseModel):
    base_price: float
    floor_rise: float
    parking: float
    other_charges: float
    subtotal: float
    gst_amount: float
    total_agreement_value: float

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
    
    await log_activity(user['id'], user['name'], "update", "user", user_id, f"Updated user")
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
    
    await log_activity(user['id'], user['name'], "update", "customer", customer_id, f"Updated customer")
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
    await log_activity(user['id'], user['name'], "update", "payment_item", item_id, f"Updated payment status")
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
            except:
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
@api_router.post("/calculator/price", response_model=PriceResult)
async def calculate_price(data: PriceCalculation):
    base_price = data.carpet_area * data.rate_per_sqft
    subtotal = base_price + data.floor_rise_charges + data.parking_charges + data.other_charges
    gst_amount = subtotal * (data.gst_percentage / 100)
    total = subtotal + gst_amount
    
    return PriceResult(
        base_price=round(base_price, 2),
        floor_rise=round(data.floor_rise_charges, 2),
        parking=round(data.parking_charges, 2),
        other_charges=round(data.other_charges, 2),
        subtotal=round(subtotal, 2),
        gst_amount=round(gst_amount, 2),
        total_agreement_value=round(total, 2)
    )

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
    placeholders = {
        "{customer_name}": customer.get('name', ''),
        "{customer_id}": customer.get('customer_id', ''),
        "{unit_number}": customer.get('unit_number', ''),
        "{tower}": customer.get('tower', ''),
        "{project}": customer.get('project', ''),
        "{total_price}": str(customer.get('total_price', 0)),
        "{carpet_area}": str(customer.get('carpet_area', 0)),
        "{saleable_area}": str(customer.get('saleable_area', 0)),
        "{booking_amount}": str(customer.get('booking_amount', 0)),
        "{booking_date}": customer.get('booking_date', ''),
        "{date}": datetime.now().strftime("%d-%m-%Y"),
        "{father_name}": customer.get('father_name', ''),
        "{pan_number}": customer.get('pan_number', ''),
        "{phone}": customer.get('phone', ''),
        "{email}": customer.get('email', ''),
        "{address}": customer.get('address', ''),
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
        DocumentType.ALLOTMENT_LETTER: """
ALLOTMENT LETTER

Date: {date}
Ref: {customer_id}

Dear {customer_name},

We are pleased to inform you that the following unit has been allotted to you:

PROJECT: {project}
TOWER: {tower}
UNIT NUMBER: {unit_number}
CARPET AREA: {carpet_area} sq.ft
TOTAL VALUE: Rs. {total_price}/-

Please complete the necessary documentation and payment formalities at the earliest.

Congratulations on your new home!

For RRL Builders and Developers

_______________________
Authorized Signatory
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
                except:
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
