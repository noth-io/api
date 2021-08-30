from fastapi import APIRouter, Body, Depends, HTTPException
from app.api import deps
from sqlalchemy.orm import Session
from app.crud import user as user_crud
from app import models, schemas
from app.core import security
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("")
def get_token(db: Session = Depends(deps.get_db)):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            "romain.grente@gmail.com", expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }