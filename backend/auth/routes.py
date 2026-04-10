"""
Authentication routes for RRL CRM.
Handles user registration, login, password reset, and user management.
"""
from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
import jwt

from config import settings
from database import get_database
from utils.enums import UserRole
from auth.models import (
    UserCreate, UserLogin, User, UserResponse, TokenResponse,
    VerifyEmailRequest, ResetPasswordRequest, AdminResetPasswordRequest
)
from auth.utils import hash_password, verify_password, create_token, check_role, get_current_user

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])
admin_router = APIRouter(tags=["Admin"])
users_router = APIRouter(prefix="/users", tags=["Users"])


async def log_activity(user_id: str, user_name: str, action: str, entity_type: str, entity_id: str, details: str):
    """Log user activity."""
    db = get_database()
    from auth.models import User
    import uuid
    log = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "user_name": user_name,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.activity_logs.insert_one(log)


# ==================== AUTH ROUTES ====================
@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user."""
    db = get_database()
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


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with email and password."""
    db = get_database()
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


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(
        id=user['id'],
        email=user['email'],
        name=user['name'],
        role=user['role'],
        phone=user.get('phone'),
        is_active=user.get('is_active', True),
        created_at=user['created_at']
    )


@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest):
    """Verify if email exists in the system for password reset."""
    db = get_database()
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found in our system")
    return {"exists": True, "message": "Email verified"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    """Reset user password."""
    db = get_database()
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


# ==================== ADMIN ROUTES ====================
@admin_router.post("/admin/reset-user-password")
async def admin_reset_user_password(data: AdminResetPasswordRequest, current_user: dict = Depends(get_current_user)):
    """Admin can reset any user's password."""
    db = get_database()
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
@users_router.get("", response_model=List[UserResponse])
async def get_users(user: dict = Depends(check_role([UserRole.ADMIN]))):
    """Get all users (admin only)."""
    db = get_database()
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return [UserResponse(**u) for u in users]


@users_router.put("/{user_id}")
async def update_user(user_id: str, updates: Dict[str, Any], user: dict = Depends(check_role([UserRole.ADMIN]))):
    """Update a user (admin only)."""
    db = get_database()
    if 'password' in updates:
        updates['password_hash'] = hash_password(updates.pop('password'))
    
    result = await db.users.update_one({"id": user_id}, {"$set": updates})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    await log_activity(user['id'], user['name'], "update", "user", user_id, "Updated user")
    return {"message": "User updated"}


@users_router.delete("/{user_id}")
async def delete_user(user_id: str, user: dict = Depends(check_role([UserRole.ADMIN]))):
    """Delete a user (admin only)."""
    db = get_database()
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    await log_activity(user['id'], user['name'], "delete", "user", user_id, "Deleted user")
    return {"message": "User deleted"}
