from fastapi import APIRouter

from app.api.v1.auth import token

router = APIRouter()
router.include_router(token.router, prefix="/token")