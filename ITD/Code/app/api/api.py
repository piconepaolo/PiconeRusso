from fastapi import APIRouter

from app.api.endpoints import auth, notification, team, user, tournament
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(user.router, prefix=settings.USERS_STR, tags=["users"])
api_router.include_router(auth.router, prefix=settings.AUTH_STR, tags=["auth"])
api_router.include_router(
    notification.router, prefix=settings.NOTIFICATIONS_STR, tags=["notifications"]
)
api_router.include_router(team.router, prefix=settings.TEAMS_STR, tags=["teams"])
api_router.include_router(
    tournament.router, prefix=settings.TOURNAMENTS_STR, tags=["tournaments"]
)
