from flask import Blueprint, json
from flask import Flask, session, request, redirect, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
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
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')
        if user.confirmed is True:
            abort(400, 'user is already confirmed')

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
            "htmlContent": "<html><head></head><body><a href='%s/users/confirm/%s'>Click here to confirm your account</a></body></html>" % (API_URL, token)
        }
        r = requests.post(mailapiurl, headers=headers, data=json.dumps(payload))

        if r.status_code == 201:
            msg = { "message": "confirmation mail send successfully" }
            status = 200
        else:
            abort(500)

        resp = Response(response=json.dumps(msg), status=status, mimetype="application/json")
        return resp

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
                msg = { "message": "user is confirmed" }
                status = 200
            else:
                raise
        except:
            abort(404, "user can't be confirmed")

        resp = Response(response=json.dumps(msg), status=status, mimetype="application/json")
        return resp