from fastapi import APIRouter, Body, Depends, HTTPException
from api import deps
from sqlalchemy.orm import Session
from crud import user as user_crud, credential as credential_crud
import models, schemas
from core import security, responses
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import requests, json
from fastapi.encoders import jsonable_encoder
from core.config import settings
from utils import email
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("")
def logout(db: Session = Depends(deps.get_db), user: schemas.User = Depends(deps.get_current_user_from_cookie)):
    content = { "authenticated": False }
    response = JSONResponse(content=content)
    response.set_cookie(key="session", secure=True, domain=settings.COOKIE_DOMAIN, httponly=True, expires=0)
    response.set_cookie(key="authenticated", secure=True, domain=settings.COOKIE_DOMAIN, expires=0)
    response.set_cookie(key="username", secure=True, domain=settings.COOKIE_DOMAIN, expires=0)
    return response
