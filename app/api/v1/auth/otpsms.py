from fastapi import APIRouter, Body, Depends, HTTPException
from app.api import deps
from sqlalchemy.orm import Session
from app.crud import user as user_crud, credential as credential_crud
from app import models, schemas
from app.core import security, responses
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import requests, json
from fastapi.encoders import jsonable_encoder
from app.core.config import settings
from datetime import datetime, timedelta
import math, random
import vonage

router = APIRouter()

# Vonage
client = vonage.Client(key="f6756e22", secret="S2F8wPqPWqdiLsJH")
sms = vonage.Sms(client)

def generateOTP() :
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

# REQUEST OTPSMS
@router.get("")
def request_otpsms(db: Session = Depends(deps.get_db), user: models.User = Depends(deps.get_current_user), token_data: schemas.AuthTokenPayload = Depends(deps.get_current_authtoken)):

    # Check token step
    if token_data.nextstep != 30:
        raise HTTPException(status_code=400, detail="Invalid authentication token step")

    """
    # Generate and store OTP code
    otpcode = OTPCode(code=generateOTP(), user_id=user.id)
    db.session.add(otpcode)
    db.session.commit()

    # Send OTP code (DISABLED FOR DEV)
    if ENV == "dev":
        print(otpcode.code)
    else:
        otpsms = sms.send_message(
            {
                "from": "Noth",
                "to": user.phone,
                "text": "Your OTP code is %s" % otpcode.code,
            }
        )

        if otpsms["messages"][0]["status"] != "0":
            abort(500)

    additional_claims = {"type": "authentication", "nextstep": "3S", "current_level": 3}
    auth_token = create_access_token(identity=user.username, additional_claims=additional_claims)
    msg = { "message": "SMS OTP sent successfully", "authenticated": False, "auth_token": auth_token }
    return msg
    """

    # Build authtoken
    authtoken = security.create_auth_token(user.email, nextstep=31, current_level=3)
    return responses.generate_auth_response(authtoken, "bearer")




# CHECK OTPSMS
@router.post("")
def check_otpsms(db: Session = Depends(deps.get_db), user: models.User = Depends(deps.get_current_user), token_data: schemas.AuthTokenPayload = Depends(deps.get_current_authtoken)):
    # Check token step
    if token_data.nextstep != 31:
        raise HTTPException(status_code=400, detail="Invalid authentication token step")

    """
    # Parse and check request
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('otpcode', location='json', type=int, required=True)
    reqbody = parser.parse_args()

    # Check if valid OTP code
    otpcode = OTPCode.query.filter_by(user_id=user.id).order_by(OTPCode.created_at.desc()).first()
    if not otpcode or otpcode.code != reqbody.otpcode or otpcode.created_at < datetime.now() - timedelta(seconds=int(OTP_LIFETIME)):
        abort(401, 'invalid OTP code')

    # Generate session token
    additional_claims = {"type": "session", "loa": 3}
    session_token = create_access_token(identity=user.username, additional_claims=additional_claims)
    message = { "authenticated": True, "session_token": session_token }
    msg = Response(response=json.dumps(message), status=200, mimetype="application/json")
    set_access_cookies(msg, session_token)
    msg.set_cookie("authenticated", "true", secure=True, domain=AUTHENTICATED_COOKIE_DOMAIN)
    msg.set_cookie("username", user.username, secure=True, domain=AUTHENTICATED_COOKIE_DOMAIN)

    return msg
    """
    # Build authtoken
    authtoken = security.create_auth_token(db_user.email, nextstep=30, current_level=3)
    return responses.generate_auth_response(authtoken, "bearer")

 