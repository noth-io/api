from fastapi import APIRouter, Body, Depends, HTTPException
from app.api import deps
from sqlalchemy.orm import Session
from app.crud import user as user_crud, credential as credential_crud
from app import models, schemas
from app.core import security, responses
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import requests, json
from fastapi.encoders import jsonable_encoder

router = APIRouter()

# Config Mail
MAIL_SENDER_NAME = "Noth"
MAIL_SENDER_EMAIL = "admin@noth.io"
NOTH_UI_URL = "https://noth-dev.meanite.tk"
mailapikey = "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"
mailapiurl = "https://api.sendinblue.com/v3/smtp/email"
s = URLSafeTimedSerializer("toto")

mail_level = 2
mail_step = 2

@router.get("")
def request_auth_mail(db: Session = Depends(deps.get_db), user: models.User = Depends(deps.get_current_user)):
    """
    # Check if correct authentication step
    if get_jwt().get("nextstep") != mail_step:
        abort(400)
        
    """

    # Generate token
    token = s.dumps(jsonable_encoder(user), salt='user-mailauth')

    # Build mail API Call
    headers = { "accept": "application/json", "api-key": mailapikey, "content-type": "application/json" }
    payload = {  
        "sender": {  
            "name": MAIL_SENDER_NAME,
            "email": MAIL_SENDER_EMAIL
        },
        "to": [  
            {  
                "email": user.email,
                "name": "%s %s" % (user.firstname, user.lastname)
            }
        ],
        "subject": "User authentication",
        "htmlContent": "<html><head></head><body><a href='%s/login/mail/%s'>Click here to authenticate</a></body></html>" % (NOTH_UI_URL, token)
    }
    r = requests.post(mailapiurl, headers=headers, data=json.dumps(payload))

    if r.status_code != 201:
        abort(500)

    authtoken = security.create_auth_token(user.email, nextstep=21, current_level=1)
    return responses.generate_auth_response(authtoken, "bearer")

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
     
    authtoken = security.create_auth_token(db_user.email, nextstep=30, current_level=3)
    return responses.generate_auth_response(authtoken, "bearer")