from fastapi import APIRouter, Body, Depends, HTTPException
from api import deps
from sqlalchemy.orm import Session
from crud import otp as otp_crud
import models, schemas
from core import security, responses
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import requests, json
from fastapi.encoders import jsonable_encoder
from core.config import settings
import vonage
from fastapi.responses import JSONResponse

router = APIRouter()

# Vonage
client = vonage.Client(key="f6756e22", secret="S2F8wPqPWqdiLsJH")
sms = vonage.Sms(client)

# REQUEST OTPSMS
@router.get("")
def request_otpsms(db: Session = Depends(deps.get_db), user: models.User = Depends(deps.get_current_user), token_data: schemas.AuthTokenPayload = Depends(deps.get_current_authtoken)):

    # Check token step
    if token_data.nextstep != 30:
        raise HTTPException(status_code=400, detail="Invalid authentication token step")

    # Generate and store OTP code
    code = otp_crud.create_otp(db, user.id)

    # Send OTP code (PRINT ONLY FOR DEV)
    if settings.ENV == "DEV":
        print(code)
    else:
        otpsms = sms.send_message(
            {
                "from": "Noth",
                "to": user.phone,
                "text": "Your OTP code is %s" % otpcode,
            }
        )

        if otpsms["messages"][0]["status"] != "0":
            raise HTTPException(status_code=500)

    # Build authtoken
    authtoken = security.create_auth_token(user.email, nextstep=31, current_level=3)
    return responses.generate_auth_response(authtoken, "bearer")


# CHECK OTPSMS
@router.post("")
def check_otpsms(OTP: schemas.OTPBase, db: Session = Depends(deps.get_db), user: models.User = Depends(deps.get_current_user), token_data: schemas.AuthTokenPayload = Depends(deps.get_current_authtoken)):
    # Check token step
    if token_data.nextstep != 31:
        raise HTTPException(status_code=400, detail="Invalid authentication token step")

    # Validate OTP code
    otp_crud.is_valid_otp(db, OTP.code, user.id, settings.OTP_LIFETIME)

    # Return session token
    session_token = security.create_session_token(user.email, loa=3)
    content = { "authenticated": True }
    response = JSONResponse(content=content)
    response.set_cookie(key="session", value=session_token, secure=True, domain=settings.COOKIE_DOMAIN, httponly=True)
    response.set_cookie(key="authenticated", value=True, secure=True, domain=settings.COOKIE_DOMAIN)
    response.set_cookie(key="username", value=user.email, secure=True, domain=settings.COOKIE_DOMAIN)
    return response
