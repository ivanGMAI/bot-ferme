from core.config import settings
from fastapi import APIRouter
from features.admins.router import router as admin_router
from features.users.router import router as user_router
from features.health.router import router as health_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)
router.include_router(health_router)
router.include_router(admin_router)
router.include_router(user_router)
