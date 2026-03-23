from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import Person, User
from app.schemas import AuthResponse, LoginRequest, RegisterRequest, TokenResponse
from app.services.user import UserService


class AuthService:
    @staticmethod
    def _build_auth_response(user: User) -> AuthResponse:
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        effective_permissions = UserService.get_effective_permission_codes(user)

        return AuthResponse(
            token=TokenResponse(access_token=token, expires_in=expires_in),
            user=user,
            effective_permissions=effective_permissions,
        )

    @staticmethod
    def register(db: Session, payload: RegisterRequest) -> AuthResponse:
        existing_user = UserService.get_by_username(db, payload.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

        existing_email = UserService.get_by_email(db, payload.email)
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        if payload.person.email:
            existing_person_email = db.query(Person).filter(Person.email == payload.person.email).first()
            if existing_person_email:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Person email already exists")

        person = Person(**payload.person.model_dump())
        db.add(person)
        db.flush()

        user = User(
            username=payload.username,
            email=payload.email,
            password_hash=get_password_hash(payload.password),
            person_id=person.id,
            is_active=True,
            is_superuser=False,
        )

        db.add(user)
        db.commit()

        fresh_user = UserService.get_by_id(db, user.id)
        return AuthService._build_auth_response(fresh_user)

    @staticmethod
    def login(db: Session, payload: LoginRequest) -> AuthResponse:
        user: Optional[User] = UserService.get_by_email(db, payload.username_or_email)
        if not user:
            user = UserService.get_by_username(db, payload.username_or_email)

        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

        fresh_user = UserService.get_by_id(db, user.id)
        return AuthService._build_auth_response(fresh_user)
