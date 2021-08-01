from flask import Blueprint, json
from flask import Flask, session, request, redirect, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from database.models import db, User
from flask_restx import Api
from flask_restx import Namespace, Resource, fields
import requests
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# import config
from config import *

# Config Mail
mailapikey = MAIL_API_KEY
mailapiurl = MAIL_API_URL
s = URLSafeTimedSerializer(MAIL_TOKEN_CONFIRM_SECRET)

# Init API
api = Namespace('Confirm User', description='User confirmation API')

@api.route('/confirm')
class SendUserConfirmMail(Resource):
    @jwt_required()
    def post(self):

        # Check if correct registration step
        if get_jwt().get("type") != "register" or get_jwt().get("step") != 0:
            abort(400)

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')
        if user.confirmed is True:
            abort(400, 'user is already confirmed')

        username = user.username
        email = user.email
        firstname = user.firstname
        lastname = user.lastname

        # Generate token
        token = s.dumps(email, salt='user-confirm')

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
            "subject": "Account confirmation",
            "htmlContent": "<html><head></head><body><a href='%s/register/confirm/%s'>Click here to confirm your account</a></body></html>" % (NOTH_UI_URL, token)
        }
        r = requests.post(mailapiurl, headers=headers, data=json.dumps(payload))

        if r.status_code != 201:
            abort(500)

        additional_claims = {"type": "register", "step": 1}
        register_token = create_access_token(identity=username, additional_claims=additional_claims)

        msg = { "message": "confirmation mail send successfully", "register_token": register_token }
        return msg

@api.route('/confirm/<token>')
class CheckUserConfirmMail(Resource):
    @jwt_required()
    def get(self, token):
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')
        if user.confirmed is True:
            abort(400, 'user is already confirmed')

        try:
            email = s.loads(token, salt='user-confirm', max_age=600)
            if email == user.email:
                # Update confirmed in DB
                user.confirmed = True
                db.session.commit()
            else:
                raise
        except:
            abort(404, "user can't be confirmed")

        additional_claims = {"type": "session", "loa": 1}
        session_token = create_access_token(identity=user.username, additional_claims=additional_claims)

        msg = { "message": "user is confirmed", "session_token": session_token }
        return msg