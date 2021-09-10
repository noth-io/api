from fastapi import APIRouter
from api.v1.auth import token, username, email, otpsms, fido2

router = APIRouter()
router.include_router(username.router, prefix="/username")
router.include_router(email.router, prefix="/email")
router.include_router(otpsms.router, prefix="/otpsms")
router.include_router(token.router, prefix="/token")
router.include_router(fido2.router, prefix="/fido2")
