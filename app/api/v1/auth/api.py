from fastapi import APIRouter
from app.api.v1.auth import token, username, email, otpsms

router = APIRouter()
router.include_router(username.router, prefix="/username")
router.include_router(email.router, prefix="/email")
router.include_router(otpsms.router, prefix="/otpsms")
router.include_router(token.router, prefix="/token")
