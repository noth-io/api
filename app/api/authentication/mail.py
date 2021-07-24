from flask_restx import Namespace, Resource, fields
from flask import Blueprint, json
from flask import Flask, session, request, redirect, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, decode_token, get_jwt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import requests
from database.models import db, User

api = Namespace('Mail', description='Mail authentication API')

# Config Mail
mailapikey = "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"
mailapiurl = "https://api.sendinblue.com/v3/smtp/email"
s = URLSafeTimedSerializer('Thisisasecret!')

mail_authlevel = 2

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
                "name":"Noth",
                "email":"admin@noth.io"
            },
            "to": [  
                {  
                    "email": email,
                    "name": "%s %s" % (firstname, lastname)
                }
            ],
            "subject": "User authentication",
            "htmlContent": "<html><head></head><body><a href='https://192.168.5.52:5000/authentication/mail/%s'>Click here to authenticate</a></body></html>" % (token)
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

        # Get authentication level
        level = get_jwt().get("level")
        newlevel = level | mail_authlevel

        try:
            email = s.loads(token, salt='user-mailauth', max_age=600)
            if email == user.email:
                additional_claims = {"level": newlevel}
                msg = create_access_token(identity=user.username, additional_claims=additional_claims)
                status = 200
            else:
                raise
        except:
            abort(401, 'mail authentication failed')

        resp = Response(response=json.dumps(msg), status=status, mimetype="application/json")
        return resp