from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import require_permissions
from app.database import get_db
from app.schemas import PermissionCreate, PermissionResponse, PermissionUpdate
from app.services import PermissionService

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/", response_model=List[PermissionResponse])
def get_permissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["permission.read"])),
):
    return PermissionService.get_all(db, skip, limit)


@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["permission.read"])),
):
    permission = PermissionService.get_by_id(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.post("/", response_model=PermissionResponse, status_code=201)
def create_permission(
    payload: PermissionCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["permission.create"])),
):
    existing = PermissionService.get_by_code(db, payload.code)
    if existing:
        raise HTTPException(status_code=409, detail="Permission code already exists")
    return PermissionService.create(db, payload)


@router.put("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    payload: PermissionUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["permission.update"])),
):
    permission = PermissionService.update(db, permission_id, payload)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.delete("/{permission_id}", status_code=204)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["permission.delete"])),
):
    if not PermissionService.delete(db, permission_id):
        raise HTTPException(status_code=404, detail="Permission not found")
    return None
