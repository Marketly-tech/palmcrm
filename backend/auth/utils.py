"""
Authentication utilities for RRL CRM.
Password hashing, token creation, and user verification.
"""
from datetime import datetime, timedelta, timezone
from typing import List
import jwt
import bcrypt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from utils.enums import UserRole

# JWT Security
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: str, email: str, role: str) -> str:
    """Create a JWT token for a user."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def check_role(required_roles: List[UserRole]):
    """Create a dependency that checks if user has required role."""
    async def role_checker(user: dict = Depends(get_current_user)):
        if UserRole(user["role"]) not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker


# Note: get_current_user is defined in routes.py because it needs database access
# It will be imported from there when needed

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Placeholder - actual implementation is in routes.py because it needs db access.
    This is here for import consistency.
    """
    raise NotImplementedError("Use get_current_user from auth.routes instead")
