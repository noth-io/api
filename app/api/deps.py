from typing import Generator
from app.db.session import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from app import models
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud import user as user_crud
from app.core.config import settings
from app.core import security

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
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        #token_data = schemas.TokenPayload(**payload)
    except:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )
    user = user_crud.get_user_by_email(db, email=payload['sub'])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_admin(
    current_user: models.User = Depends(get_current_user),
    ) -> models.User:
    #if not user_crud.is_admin(current_user):
    #    raise HTTPException(
    #        status_code=400, detail="The user doesn't have enough privileges"
    #    )
    return current_user

