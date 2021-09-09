from typing import Generator
from db.session import SessionLocal
from fastapi.security import OAuth2PasswordBearer
import models, schemas
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from crud import user as user_crud
from core.config import settings
from core import security

from jose import jwt

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> models.User:
    token_data = security.validate_token(token)
    user = user_crud.get_user_by_email(db, email=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_user_from_cookie(db: Session = Depends(get_db), session: str = Cookie(None)) -> models.User:
    token_data = security.validate_token(session)
    user = user_crud.get_user_by_email(db, email=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_authtoken(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> schemas.AuthTokenPayload:
    token_data = security.validate_token(token)
    return token_data

def get_current_active_admin(
    current_user: models.User = Depends(get_current_user),
    ) -> models.User:
    # TO ENABLE
    #if not user_crud.is_admin(current_user):
    #    raise HTTPException(
    #        status_code=400, detail="The user doesn't have enough privileges"
    #    )
    return current_user

"""
def get_auth_token(
    current_user: models.User = Depends(get_current_user),
    ) -> models.User:
    print(current_user)
    #if not user_crud.is_admin(current_user):
    #    raise HTTPException(
    #        status_code=400, detail="The user doesn't have enough privileges"
    #    )
    return current_user
"""
