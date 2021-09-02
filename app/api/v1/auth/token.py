from fastapi import APIRouter, Body, Depends, HTTPException
from api import deps
from sqlalchemy.orm import Session
from crud import user as user_crud
import models, schemas
from core import security
from datetime import timedelta
from core.config import settings

router = APIRouter()

@router.post("")
def get_token(db: Session = Depends(deps.get_db)):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            "jdoe@foo", expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }