"""
Auth module for RRL CRM.
Exports routers and commonly used functions.
"""
from auth.routes import router, admin_router, users_router, get_current_user, log_activity
from auth.utils import hash_password, verify_password, create_token, check_role
from auth.models import (
    UserBase, UserCreate, UserLogin, User, UserResponse, TokenResponse,
    VerifyEmailRequest, ResetPasswordRequest, AdminResetPasswordRequest
)

__all__ = [
    # Routers
    "router",
    "admin_router", 
    "users_router",
    # Functions
    "get_current_user",
    "log_activity",
    "hash_password",
    "verify_password",
    "create_token",
    "check_role",
    # Models
    "UserBase",
    "UserCreate",
    "UserLogin",
    "User",
    "UserResponse",
    "TokenResponse",
    "VerifyEmailRequest",
    "ResetPasswordRequest",
    "AdminResetPasswordRequest",
]
