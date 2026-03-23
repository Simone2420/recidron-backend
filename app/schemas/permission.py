from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PermissionBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool = True


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
