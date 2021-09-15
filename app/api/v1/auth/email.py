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
s = URLSafeTimedSerializer(settings.AUTH_MAIL_TOKEN_KEY)

# REQUEST AUTH MAIL
@router.get("")
def request_auth_mail(db: Session = Depends(deps.get_db), user: models.User = Depends(deps.get_current_user), token_data: schemas.AuthTokenPayload = Depends(deps.get_current_authtoken)):

    # Check token step
    if token_data.nextstep != 20:
        raise HTTPException(status_code=400, detail="Invalid authentication token step")

    # Generate token
    token = s.dumps(jsonable_encoder(user), salt='user-mailauth')

    # Send authentication email
    email.send(user, type="authentication", token=token)

    # Build authtoken
    authtoken = security.create_auth_token(user.email, nextstep=21, current_level=1)
    return responses.generate_auth_response(authtoken, "bearer")

# CHECK AUTH MAIL TOKEN
@router.post("/{token}")
def check_auth_mail_token(token: str, db: Session = Depends(deps.get_db)):
    # Check auth mail token
    try:
        emailToken = s.loads(token, salt='user-mailauth', max_age=600)
        db_user = user_crud.get_user_by_email(db, email=emailToken["email"])
        if not db_user:
            raise
    except:
        raise HTTPException(status_code=400, detail="Can't validate auth mail token")
     
    # Build authtoken
    #authtoken = security.create_auth_token(db_user.email, nextstep=30, current_level=3)
    #return responses.generate_auth_response(authtoken, "bearer")
    # Return session token
    session_token = security.create_session_token(db_user.email, loa=1)
    content = { "authenticated": True }
    response = JSONResponse(content=content)
    response.set_cookie(key="session", value=session_token, secure=True, domain=settings.COOKIE_DOMAIN, httponly=True)
    response.set_cookie(key="authenticated", value=True, secure=True, domain=settings.COOKIE_DOMAIN)
    response.set_cookie(key="username", value=db_user.email, secure=True, domain=settings.COOKIE_DOMAIN)
    return response