from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import require_permissions
from app.database import get_db
from app.schemas import RoleCreate, RoleResponse, RoleUpdate
from app.services import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=List[RoleResponse])
def get_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["role.read"])),
):
    return RoleService.get_all(db, skip, limit)


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["role.read"])),
):
    role = RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/", response_model=RoleResponse, status_code=201)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["role.create"])),
):
    existing = RoleService.get_by_name(db, payload.name)
    if existing:
        raise HTTPException(status_code=409, detail="Role name already exists")
    return RoleService.create(db, payload)


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["role.update"])),
):
    role = RoleService.update(db, role_id, payload)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.delete("/{role_id}", status_code=204)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["role.delete"])),
):
    if not RoleService.delete(db, role_id):
        raise HTTPException(status_code=404, detail="Role not found")
    return None
