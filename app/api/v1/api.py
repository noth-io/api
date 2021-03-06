from fastapi import APIRouter
from api.v1.users import users
from api.v1 import auth
from api.v1 import credentials

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(credentials.router, prefix="/credentials", tags=["credentials"])