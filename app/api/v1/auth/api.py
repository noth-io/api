from fastapi import APIRouter

from app.api.v1.auth import token, username

router = APIRouter()
router.include_router(username.router, prefix="/username")
router.include_router(token.router, prefix="/token")