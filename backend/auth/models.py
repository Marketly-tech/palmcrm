"""
Authentication models for RRL CRM.
Matches the working models from server.py.
"""
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, EmailStr, ConfigDict
import uuid

from utils.enums import UserRole


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


class VerifyEmailRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str


class AdminResetPasswordRequest(BaseModel):
    user_id: str
    new_password: str
