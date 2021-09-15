from fastapi import APIRouter, Body, Depends, HTTPException
from api import deps
from sqlalchemy.orm import Session
from crud import user as user_crud
import models, schemas
from typing import Any, List
from core import security
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from core.config import settings
from fastapi.encoders import jsonable_encoder
import requests, json
from utils import email
from fastapi.responses import JSONResponse

router = APIRouter()
s = URLSafeTimedSerializer(settings.AUTH_MAIL_TOKEN_KEY)

@router.get("", response_model=List[schemas.User])
def get_users(db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_active_admin)):
    return user_crud.get_users(db)

@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(deps.get_db)):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}")
def get_user(user_id: int, db: Session = Depends(deps.get_db)):
    db_user = user_crud.delete_user(db, user_id=user_id)
    if db_user is False:
        raise HTTPException(status_code=404, detail="User not found")
    return { "message": "user deleted" }

###########################################
# User registration
###########################################
# Create USER
@router.post("")
def create_user(user: schemas.UserBase, db: Session = Depends(deps.get_db)):
    # Check if user with this email exists
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered (email)")
    
    # Check if user with this phone exists
    db_user = user_crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered (phone)")

    # Generate email confirmation token
    token = s.dumps(jsonable_encoder(user), salt='user-mailconfirm')

    # Send confirm email
    email.send(user, type="confirm", token=token)

    return { "message": "User confirmation mail has been sent" }

"""
# Send confirm USER email
@router.get("/confirm/email")
def request_auth_mail(db: Session = Depends(deps.get_db), user: models.User = Depends(deps.get_current_user), token_data: schemas.RegisterTokenPayload = Depends(deps.get_current_registertoken)):

    # Check token step
    if token_data.step != 0:
        raise HTTPException(status_code=400, detail="Invalid register token step")

    # Generate token
    token = s.dumps(jsonable_encoder(user), salt='user-mailconfirm')

    # Send confirm email
    email.send(user, type="confirm", token=token)

    # Return register token
    return { "register_token": security.create_register_token(user.email, step=1) }
"""

# Validate confirm USER email and create user in DB
@router.post("/confirm/email/{token}")
def check_auth_mail_token(token: str, db: Session = Depends(deps.get_db)):
    # Check confirm mail token
    try:
        emailToken = s.loads(token, salt='user-mailconfirm', max_age=600)
    except:
        raise HTTPException(status_code=400, detail="Can't validate confirm mail token")
    
    # Create user in DB
    user = user_crud.create_user(db, schemas.UserBase.parse_raw(json.dumps(emailToken)))

    # Return session token
    session_token = security.create_session_token(user.email, loa=1)
    content = { "authenticated": True, "message": "User email is confirmed" }
    response = JSONResponse(content=content)
    response.set_cookie(key="session", value=session_token, secure=True, domain=settings.COOKIE_DOMAIN, httponly=True)
    response.set_cookie(key="authenticated", value=True, secure=True, domain=settings.COOKIE_DOMAIN)
    response.set_cookie(key="username", value=user.email, secure=True, domain=settings.COOKIE_DOMAIN)
    return response
