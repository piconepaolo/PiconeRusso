from fastapi import APIRouter

from app.api.endpoints import auth, user
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(user.router, prefix=settings.USERS_STR, tags=["users"])
api_router.include_router(auth.router, prefix=settings.AUTH_STR, tags=["auth"])
