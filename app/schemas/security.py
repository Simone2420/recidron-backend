from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class PermissionResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    module: str
    action: str

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    permissions: list[PermissionResponse] = []

    class Config:
        from_attributes = True


class PersonCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)


class PersonResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    person: PersonCreate
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    is_superuser: bool
    person: PersonResponse
    roles: list[RoleResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class AssignRoleRequest(BaseModel):
    role_name: str
