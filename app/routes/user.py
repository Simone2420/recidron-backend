from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import require_permissions
from app.database import get_db
from app.schemas import UserCreate, UserResponse, UserUpdate
from app.services import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["user.read"])),
):
    return UserService.get_all(db, skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["user.read"])),
):
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["user.create"])),
):
    if UserService.get_by_username(db, payload.username):
        raise HTTPException(status_code=409, detail="Username already exists")

    if UserService.get_by_email(db, str(payload.email)):
        raise HTTPException(status_code=409, detail="Email already exists")

    return UserService.create(db, payload)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["user.update"])),
):
    user = UserService.update(db, user_id, payload)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permissions(["user.delete"])),
):
    if not UserService.delete(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return None
