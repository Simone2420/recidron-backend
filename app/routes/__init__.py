from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.item import router as item_router
from app.routes.permission import router as permission_router
from app.routes.person import router as person_router
from app.routes.role import router as role_router
from app.routes.user import router as user_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(item_router)
router.include_router(person_router)
router.include_router(user_router)
router.include_router(role_router)
router.include_router(permission_router)

__all__ = ["router"]