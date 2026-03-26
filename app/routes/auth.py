from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import get_current_active_user
from app.database import get_db
from app.models import User
from app.schemas import AuthResponse, LoginRequest, MeResponse, RegisterRequest, TokenResponse
from app.services import AuthService, UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService.register(db, payload)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(db, payload)


@router.post("/token", response_model=TokenResponse)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    auth_response = AuthService.login(
        db,
        LoginRequest(username_or_email=form_data.username, password=form_data.password),
    )
    return auth_response.token


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_active_user)):
    return MeResponse(
        user=current_user,
        effective_permissions=UserService.get_effective_permission_codes(current_user),
    )
