"""
Authentication models for RRL CRM.
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from utils.enums import UserRole


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.SALES
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: str
    status: str = "active"
    created_at: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: str = "active"


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


class VerifyEmailRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str
    token: Optional[str] = None


class AdminResetPasswordRequest(BaseModel):
    user_id: str
    new_password: str
