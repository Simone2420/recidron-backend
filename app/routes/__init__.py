from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.item import router as item_router

router = APIRouter()
router.include_router(item_router)
router.include_router(auth_router)

__all__ = ["router", "item_router", "auth_router"]