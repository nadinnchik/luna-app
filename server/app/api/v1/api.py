from fastapi import APIRouter
from app.api.v1.endpoints import auth, profile, children, quiz, analytics

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(children.router, prefix="/children", tags=["children"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
