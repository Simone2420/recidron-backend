from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from app.schemas.permission import PermissionResponse
from app.schemas.person import PersonResponse
from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    person_id: Optional[int] = None


class UserCreate(UserBase):
    password: str
    role_ids: List[int] = []
    permission_ids: List[int] = []


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    person_id: Optional[int] = None
    role_ids: Optional[List[int]] = None
    permission_ids: Optional[List[int]] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    person: Optional[PersonResponse] = None
    roles: List[RoleResponse] = []
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True
