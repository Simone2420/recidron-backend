from typing import Callable, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload

from app.core.security import decode_access_token
from app.database import get_db
from app.models import Role, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def _get_user_effective_permissions(user: User) -> set[str]:
    permission_codes = {permission.code for permission in user.permissions if permission.is_active}

    for role in user.roles:
        if not role.is_active:
            continue
        for permission in role.permissions:
            if permission.is_active:
                permission_codes.add(permission.code)

    return permission_codes


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    subject = payload.get("sub")
    if not subject:
        raise credentials_exception

    user = (
        db.query(User)
        .options(
            joinedload(User.person),
            joinedload(User.roles).joinedload(Role.permissions),
            joinedload(User.permissions),
        )
        .filter(User.id == int(subject))
        .first()
    )
    if not user:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


def require_permissions(required_permissions: List[str]) -> Callable:
    def _permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.is_superuser:
            return current_user

        permission_codes = _get_user_effective_permissions(current_user)
        missing_permissions = [code for code in required_permissions if code not in permission_codes]

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing_permissions)}",
            )

        return current_user

    return _permission_dependency
