from flask_restx import Namespace, Resource, fields
from flask import Blueprint, json
from flask import Flask, session, request, redirect, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, decode_token, get_jwt, set_access_cookies
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import requests
from database.models import db, User

# import config
from config import *

# Config Mail
mailapikey = MAIL_API_KEY
mailapiurl = MAIL_API_URL
s = URLSafeTimedSerializer(MAIL_TOKEN_AUTHENTICATION_SECRET)

api = Namespace('Mail', description='Mail authentication API')

mail_level = 2
mail_step = 2

@api.route('')
class SendAuthenticationMail(Resource):
    @jwt_required()
    def get(self):

        # Check if correct authentication step
        if get_jwt().get("nextstep") != mail_step:
            abort(400)
            
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        email = user.email
        firstname = user.firstname
        lastname = user.lastname

        # Generate token
        token = s.dumps(user.json(), salt='user-mailauth')

        # Build mail API Call
        headers = { "accept": "application/json", "api-key": mailapikey, "content-type": "application/json" }
        payload = {  
            "sender": {  
                "name": MAIL_SENDER_NAME,
                "email": MAIL_SENDER_EMAIL
            },
            "to": [  
                {  
                    "email": email,
                    "name": "%s %s" % (firstname, lastname)
                }
            ],
            "subject": "User authentication",
            "htmlContent": "<html><head></head><body><a href='%s/login/mail/%s'>Click here to authenticate</a></body></html>" % (NOTH_UI_URL, token)
        }
        r = requests.post(mailapiurl, headers=headers, data=json.dumps(payload))

        if r.status_code != 201:
            abort(500)

        additional_claims = {"type": "authentication", "nextstep": "2S", "current_level": 1}
        auth_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        msg = { "message": "authentication mail sent successfully", "authenticated": False, "auth_token": auth_token }
        return msg


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

        """
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
        """
        # TEMPORARY, NEED TO IMPLEMENT AUTH SEQUENCES
        additional_claims = {"type": "authentication", "nextstep": 3, "current_level": 3}
        auth_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        msg = { "authenticated": False, "auth_token": auth_token }
        return msg