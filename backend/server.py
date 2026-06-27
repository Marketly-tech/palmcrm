"""
RRL Builders CRM - Main Application Entry Point
Thin shell that initializes the FastAPI app, configures CORS,
includes all modular routers, and handles startup/shutdown events.
"""
import os
import json
import logging
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import db, client

# Import routers from modular route files
from auth import router as auth_router, admin_router as auth_admin_router, users_router
from customers import router as customers_router
from payments import schedule_router, transactions_router, calculator_router
from dashboard import router as dashboard_router
from documents import documents_router, checklist_router, upload_router
from email_service import email_router
from booking import router as booking_router
from settings import router as settings_router, notes_router, overdue_router, misc_router, followups_router

# Import models/utilities needed for startup
from auth import User, hash_password
from utils.enums import UserRole
from utils.payment_helpers import auto_generate_booking_transaction

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="RRL Builders CRM", version="2.0.0")

# ==================== CORS MIDDLEWARE ====================
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.CORS_ORIGINS.split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== INCLUDE ALL ROUTERS ====================
# Auth routers
app.include_router(auth_router, prefix="/api")
app.include_router(auth_admin_router, prefix="/api")
app.include_router(users_router, prefix="/api")

# Customer routers
app.include_router(customers_router, prefix="/api")

# Payment routers
app.include_router(schedule_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")
app.include_router(calculator_router, prefix="/api")

# Dashboard router
app.include_router(dashboard_router, prefix="/api")

# Document routers
app.include_router(documents_router, prefix="/api")
app.include_router(checklist_router, prefix="/api")
app.include_router(upload_router, prefix="/api")

# Email/Communication router
app.include_router(email_router, prefix="/api")

# Booking & Leads router
app.include_router(booking_router, prefix="/api")

# Settings, Notes, Overdue, Units, Export, Activity, Projects
app.include_router(settings_router, prefix="/api")
app.include_router(notes_router, prefix="/api")
app.include_router(overdue_router, prefix="/api")
app.include_router(misc_router, prefix="/api")
app.include_router(followups_router, prefix="/api")


# ==================== HEALTH CHECKS ====================
@app.get("/api/")
async def api_root():
    return {"message": "RRL Builders CRM API", "version": "2.0.0"}


@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health")
async def root_health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


# ==================== ADMIN DATA RESET ====================
@app.post("/api/admin/reset-data-with-seed")
async def reset_data_with_seed():
    """Admin-only: Reset the database with seed data."""
    try:
        customers_deleted = await db.customers.delete_many({})
        transactions_deleted = await db.payment_transactions.delete_many({})
        schedules_deleted = await db.payment_schedules.delete_many({})
        documents_deleted = await db.documents.delete_many({})

        logger.info(f"Deleted: {customers_deleted.deleted_count} customers, {transactions_deleted.deleted_count} transactions")

        seed_dir = os.path.dirname(os.path.abspath(__file__))
        customers_count = 0
        transactions_count = 0

        customers_file = os.path.join(seed_dir, "seed_data_customers.json")
        if os.path.exists(customers_file):
            with open(customers_file, "r") as f:
                customers_data = json.load(f)
            if customers_data:
                await db.customers.insert_many(customers_data)
                customers_count = len(customers_data)

        transactions_file = os.path.join(seed_dir, "seed_data_transactions.json")
        if os.path.exists(transactions_file):
            with open(transactions_file, "r") as f:
                transactions_data = json.load(f)
            if transactions_data:
                await db.payment_transactions.insert_many(transactions_data)
                transactions_count = len(transactions_data)

        return {
            "success": True,
            "message": "Database reset and seeded successfully",
            "deleted": {"customers": customers_deleted.deleted_count, "transactions": transactions_deleted.deleted_count, "schedules": schedules_deleted.deleted_count, "documents": documents_deleted.deleted_count},
            "seeded": {"customers": customers_count, "transactions": transactions_count}
        }
    except Exception as e:
        logger.error(f"Error resetting data: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error resetting data: {str(e)}")


# ==================== STARTUP / SHUTDOWN EVENTS ====================
@app.on_event("startup")
async def startup_event():
    # Create default admin user if not exists
    admin = await db.users.find_one({"email": "admin@rrlbuilders.com"})
    if not admin:
        admin_user = User(email="admin@rrlbuilders.com", name="Admin User", role=UserRole.ADMIN, phone="9876543210")
        doc = admin_user.model_dump()
        doc['password_hash'] = hash_password("admin123")
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
        logger.info("Default admin user created: admin@rrlbuilders.com / admin123")

    # Create RRL CRM Admin user if not exists
    crm_admin = await db.users.find_one({"email": "crm@rrlbuildersanddevelopers.com"})
    if not crm_admin:
        crm_admin_user = User(email="crm@rrlbuildersanddevelopers.com", name="RRL CRM Admin", role=UserRole.ADMIN, phone=None)
        doc = crm_admin_user.model_dump()
        doc['password_hash'] = hash_password("#RRLnew2026")
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
        logger.info("RRL CRM Admin user created: crm@rrlbuildersanddevelopers.com")

    # Create Accounts role user if not exists
    accounts_user = await db.users.find_one({"email": "accounts@rrlbuilders.com"})
    if not accounts_user:
        from auth.models import User as AuthUser
        accounts_user_obj = AuthUser(email="accounts@rrlbuilders.com", name="Accounts User", role=UserRole.ACCOUNTS, phone=None)
        doc = accounts_user_obj.model_dump()
        doc['password_hash'] = hash_password("accounts123")
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
        logger.info("Accounts user created: accounts@rrlbuilders.com")

    # Seed customer data if database is empty
    customer_count = await db.customers.count_documents({})
    if customer_count == 0:
        logger.info("No customers found. Seeding customer data...")
        seed_dir = os.path.dirname(os.path.abspath(__file__))

        customers_file = os.path.join(seed_dir, "seed_data_customers.json")
        if os.path.exists(customers_file):
            with open(customers_file, "r") as f:
                customers_data = json.load(f)
            if customers_data:
                await db.customers.insert_many(customers_data)
                logger.info(f"Seeded {len(customers_data)} customers into database")

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

    # One-time migration: Auto-generate booking transactions for existing customers
    migration_flag = await db.settings.find_one({"type": "migration_booking_txn_done"})
    if not migration_flag:
        logger.info("Running one-time migration: auto-generate booking transactions...")
        all_customers = await db.customers.find({"booking_amount": {"$gt": 0}}, {"_id": 0}).to_list(10000)
        migrated = 0
        for cust in all_customers:
            cid = cust.get("id")
            ba = cust.get("booking_amount", 0) or 0
            if ba <= 0 or not cid:
                continue
            existing = await db.payment_transactions.find(
                {"customer_id": cid, "$or": [{"transaction_stage": "booking"}, {"transaction_type": "booking"}]},
                {"_id": 0, "amount": 1}
            ).to_list(1000)
            existing_sum = sum(t.get("amount", 0) or 0 for t in existing)
            if existing_sum >= ba:
                continue
            await auto_generate_booking_transaction(cid, cust, created_by="system-migration")
            migrated += 1
        logger.info(f"Migration complete: auto-generated booking transactions for {migrated} customers")
        await db.settings.insert_one({"type": "migration_booking_txn_done", "migrated_count": migrated, "run_at": datetime.now(timezone.utc).isoformat()})


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
