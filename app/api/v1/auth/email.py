from fastapi import APIRouter, Body, Depends, HTTPException
from app.api import deps
from sqlalchemy.orm import Session
from app.crud import user as user_crud, credential as credential_crud
from app import models, schemas
from app.core import security, responses
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import requests
import json

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
        
    # Check identity in DB
    current_identity = get_jwt_identity()
    user = User.query.filter_by(username=current_identity).first()
    if not user:
        abort(401, 'invalid user')
    """

    # Generate token
    token = s.dumps(user.email, salt='user-mailauth')

    print(user.email)
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

    #additional_claims = {"type": "authentication", "nextstep": "2S", "current_level": 1}
    #auth_token = create_access_token(identity=user.username, additional_claims=additional_claims)
    #msg = { "message": "authentication mail sent successfully", "authenticated": False, "auth_token": auth_token }
    return "titi"

"""
@api.route('/<token>')
class CheckAuthenticationMail(Resource):
    def post(self, token):

        # Check token
        try:
            userToken = s.loads(token, salt='user-mailauth', max_age=600)
            user = User.query.filter_by(username=userToken["username"]).first()
            if not user:
                raise
        except:
            abort(401, 'mail authentication failed')
     

        # Calculate new auth level
        #old_level = get_jwt().get("current_level")
        #new_level = old_level | mail_level
        #print(new_level)

        
        # If target level reached (todo : convert to function)
        if get_jwt().get("target_level") == new_level:
            # Generate session token
            additional_claims = {"type": "session", "loa": 1}
            session_token = create_access_token(identity=user.username, additional_claims=additional_claims)
            message = { "authenticated": True, "session_token": session_token }
            msg = Response(response=json.dumps(message), status=200, mimetype="application/json")
            set_access_cookies(msg, session_token)
            msg.set_cookie("authenticated", "true", secure=True)
        else:
            additional_claims = {"type": "authentication", "target_level": get_jwt().get("target_level"), "nextstep": 4, "current_level": new_level}
            auth_token = create_access_token(identity=user.username, additional_claims=additional_claims)
            msg = { "authenticated": False, "auth_token": auth_token }
        
        # TEMPORARY, NEED TO IMPLEMENT AUTH SEQUENCES
        additional_claims = {"type": "authentication", "nextstep": 3, "current_level": 3}
        auth_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        msg = { "authenticated": False, "auth_token": auth_token }
        return msg
"""