from flask_restx import Namespace, Resource, fields
from flask import Blueprint, json
from flask import Flask, session, request, redirect, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, decode_token, get_jwt
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

mail_authstate = 2

@api.route('')
class SendAuthenticationMail(Resource):
    @jwt_required()
    def post(self):
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        email = user.email
        firstname = user.firstname
        lastname = user.lastname

        # Generate token
        token = s.dumps(email, salt='user-mailauth')

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
            "htmlContent": "<html><head></head><body><a href='%s/authentication/mail/%s'>Click here to authenticate</a></body></html>" % (API_URL, token)
        }
        r = requests.post(mailapiurl, headers=headers, data=json.dumps(payload))

        if r.status_code == 201:
            msg = { "message": "authentication mail send successfully" }
            status = 200
        else:
            abort(500)

        resp = Response(response=json.dumps(msg), status=status, mimetype="application/json")
        return resp

@api.route('/<token>')
class CheckAuthenticationMail(Resource):
    @jwt_required()
    def get(self, token):
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        # Define new auth state
        state = get_jwt().get("state")
        newstate = state | mail_authstate

        try:
            email = s.loads(token, salt='user-mailauth', max_age=600)
            if email == user.email:
                additional_claims = {"state": newstate}
                msg = create_access_token(identity=user.username, additional_claims=additional_claims)
                status = 200
            else:
                raise
        except:
            abort(401, 'mail authentication failed')

        resp = Response(response=json.dumps(msg), status=status, mimetype="application/json")
        return resp