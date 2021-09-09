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

    # Build mail API Call
    headers = { "accept": "application/json", "api-key": settings.MAIL_API_KEY, "content-type": "application/json" }
    payload = {  
        "sender": {  
            "name": settings.MAIL_SENDER_NAME,
            "email": settings.MAIL_SENDER_EMAIL
        },
        "to": [  
            {  
                "email": user.email,
                "name": "%s %s" % (user.firstname, user.lastname)
            }
        ],
        "subject": "User authentication",
        "htmlContent": "<html><head></head><body><a href='%s/login/mail/%s'>Click here to authenticate</a></body></html>" % (settings.NOTH_UI_URL, token)
    }

    # Send mail
    r = requests.post(settings.MAIL_API_URL, headers=headers, data=json.dumps(payload))
    if r.status_code != 201:
        raise HTTPException(status_code=500)

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
    authtoken = security.create_auth_token(db_user.email, nextstep=30, current_level=3)
    return responses.generate_auth_response(authtoken, "bearer")