from fastapi import APIRouter

from app.api.v1.users import users
from app.api.v1 import auth

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])