from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import get_current_active_user
from app.database import get_db
from app.models import User
from app.schemas import AuthResponse, LoginRequest, MeResponse, RegisterRequest
from app.services import AuthService, UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService.register(db, payload)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(db, payload)


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_active_user)):
    return MeResponse(
        user=current_user,
        effective_permissions=UserService.get_effective_permission_codes(current_user),
    )
