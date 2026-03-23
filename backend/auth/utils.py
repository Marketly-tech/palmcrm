"""
Authentication utilities for RRL CRM.
Password hashing, token creation, and user verification.
"""
from datetime import datetime, timedelta, timezone
from typing import List
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from utils.enums import UserRole

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(password, hashed)


def create_token(user_id: str, email: str, role: str) -> str:
    """Create a JWT token for a user."""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user from JWT token."""
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def check_role(required_roles: List[UserRole]):
    """Create a dependency that checks if user has required role."""
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in [r.value for r in required_roles]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker


def check_not_accounts_role(user: dict):
    """Check if user is NOT in accounts role (for edit/delete restrictions)."""
    if user.get("role") == UserRole.ACCOUNTS.value:
        raise HTTPException(status_code=403, detail="Accounts role cannot perform this action")
    return True
