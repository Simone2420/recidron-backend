from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.person import PersonCreate
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    person: PersonCreate


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    token: TokenResponse
    user: UserResponse
    effective_permissions: List[str] = []


class MeResponse(BaseModel):
    user: UserResponse
    effective_permissions: List[str] = []
