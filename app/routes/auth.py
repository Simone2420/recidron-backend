from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, require_permission
from app.database import get_db
from app.models import User
from app.schemas.security import AssignRoleRequest, PermissionResponse, RoleResponse, Token, UserCreate, UserResponse
from app.services.security import SecurityService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        return SecurityService.register_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = SecurityService.authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = SecurityService.create_token_for_user(user)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission("roles.read"))],
)
def read_roles(db: Session = Depends(get_db)):
    return SecurityService.list_roles(db)


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission("permissions.read"))],
)
def read_permissions(db: Session = Depends(get_db)):
    return SecurityService.list_permissions(db)


@router.post(
    "/users/{user_id}/roles",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("users.assign_role"))],
)
def assign_role_to_user(user_id: int, payload: AssignRoleRequest, db: Session = Depends(get_db)):
    try:
        user = SecurityService.assign_role_to_user(db, user_id, payload.role_name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post(
    "/users/{user_id}/promote-to-admin",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("users.update"))],
)
def promote_user_to_admin(user_id: int, db: Session = Depends(get_db)):
    try:
        user = SecurityService.promote_user_to_admin(db, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
