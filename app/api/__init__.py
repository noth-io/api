from __future__ import print_function, absolute_import, unicode_literals
from flask import Blueprint, json
from flask import current_app as app
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.client import ClientData
from fido2.server import Fido2Server
from fido2.ctap2 import AttestationObject, AuthenticatorData, AttestedCredentialData
from fido2 import cbor
from flask import Flask, session, request, redirect, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from database.models import db, User, Fido2Credential
from flask_restx import Api
from flask_restx import Namespace, Resource, fields
from flask_mail import Message, Mail
import requests
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# Config Mail
mailapikey = "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"
mailapiurl = "https://api.sendinblue.com/v3/smtp/email"
s = URLSafeTimedSerializer('Thisisasecret!')

# Init API
api = Api(
    title='Noth API',
    version='1.0',
    description='Noth API documentation')

@api.route('/users')
class Users(Resource):
    def get(self):
        users = User.query.all()
        response = []
        for user in users:
            response.append(user.json())

        resp = Response(response=json.dumps(response, default=str), status=200, mimetype="application/json")
        return resp

    def post(self):
        # Get body form data
        username = request.form['username']
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']

        # Insert in DB
        user = User(username=username, email=email, firstname=firstname, lastname=lastname)
        db.session.add(user)
        try:
            db.session.commit()
            msg = '{"msg": "registration success"}'
            status = 201
        except Exception as error:
            print(error)
            if "UNIQUE constraint" in str(error):
                msg = '{"msg": "user with this username or email is already registered"}'
                status = 409
            else:
                msg = None
                status = 500

        resp = Response(response=msg, status=status, mimetype="application/json")
        return resp

@api.route('/users/<id>/verify')
class SendUserVerifyMail(Resource):
    def get(self, id):
        # Get user from DB
        user = User.query.filter_by(id=id).first()
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
            msg = { "msg": "confirmation mail send successfully" }
            status = 200
        else:
            msg = {}
            status = 500

        resp = Response(response=json.dumps(msg), status=status, mimetype="application/json")
        return resp

@api.route('/users/<id>/verify/<token>')
class CheckUserVerifyMail(Resource):
    def get(self, id, token):
        # Get user from DB
        user = User.query.filter_by(id=id).first()

        if user.verified is True:
            msg = { "msg": "user is already verified" }
            status = 200
        else: 
            try:
                email = s.loads(token, salt='user-confirm', max_age=600)
                if email == user.email:
                    # Update verified in DB
                    user.verified = True
                    db.session.commit()
                    msg = { "msg": "user is verified" }
                    status = 200
                else:
                    raise
            except:
                msg = { "msg": "user can't be verified" }
                status = 404

        resp = Response(response=json.dumps(msg), status=status, mimetype="application/json")
        return resp