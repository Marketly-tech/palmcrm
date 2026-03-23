"""
Database module for RRL CRM backend.
Handles MongoDB connection and provides database/collection references.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

# MongoDB client instance
client: AsyncIOMotorClient = None
db = None


async def connect_to_mongo():
    """Initialize MongoDB connection."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]
    print(f"Connected to MongoDB: {settings.DB_NAME}")
    return db


async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


def get_database():
    """Get database instance."""
    return db


def get_collection(collection_name: str):
    """Get a specific collection from the database."""
    return db[collection_name]


# Collection shortcuts
def users_collection():
    return db["users"]


def customers_collection():
    return db["customers"]


def payment_schedules_collection():
    return db["payment_schedules"]


def payment_transactions_collection():
    return db["payment_transactions"]


def documents_collection():
    return db["documents"]


def document_templates_collection():
    return db["document_templates"]


def document_checklists_collection():
    return db["document_checklists"]


def communication_logs_collection():
    return db["communication_logs"]


def activity_logs_collection():
    return db["activity_logs"]


def unit_pricing_collection():
    return db["unit_pricing"]


def uploaded_documents_collection():
    return db["uploaded_documents"]
