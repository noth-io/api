from flask import Blueprint, json
from flask import Flask, session, request, redirect, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from database.models import db, User
from flask_restx import Api
from flask_restx import Namespace, Resource, fields
import requests
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# Config Mail
mailapikey = "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"
mailapiurl = "https://api.sendinblue.com/v3/smtp/email"
s = URLSafeTimedSerializer('Thisisasecret!')

# Init API
api = Namespace('User verify', description='User verify API')

@api.route('/<id>/verify')
class SendUserVerifyMail(Resource):
    def get(self, id):
        # Get user from DB
        user = User.query.filter_by(id=id).first()
        if not user:
            abort(401, 'invalid user')
        if user.verified is True:
            abort(400, 'user is already verified')

        email = user.email
        firstname = user.firstname
        lastname = user.lastname

        # Generate token
        token = s.dumps(email, salt='user-confirm')

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
            "subject": "Account confirmation",
            "htmlContent": "<html><head></head><body><a href='https://192.168.5.52:5000/users/%s/verify/%s'>Click here to confirm your account</a></body></html>" % (id, token)
        }
        r = requests.post(mailapiurl, headers=headers, data=json.dumps(payload))

        if r.status_code == 201:
            msg = { "message": "confirmation mail send successfully" }
            status = 200
        else:
            abort(500)

        resp = Response(response=json.dumps(msg), status=status, mimetype="application/json")
        return resp

@api.route('/<id>/verify/<token>')
class CheckUserVerifyMail(Resource):
    def get(self, id, token):
        # Get user from DB
        user = User.query.filter_by(id=id).first()
        if not user:
            abort(401, 'invalid user')
        if user.verified is True:
            abort(400, 'user is already verified')

        try:
            email = s.loads(token, salt='user-confirm', max_age=600)
            if email == user.email:
                # Update verified in DB
                user.verified = True
                db.session.commit()
                msg = { "message": "user is verified" }
                status = 200
            else:
                raise
        except:
            abort(404, "user can't be verified")

        resp = Response(response=json.dumps(msg), status=status, mimetype="application/json")
        return resp