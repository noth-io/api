from fastapi import APIRouter
from api.v1.credentials import fido2

router = APIRouter()
router.include_router(fido2.router, prefix="/fido2")