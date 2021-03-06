from flask import Blueprint, json
from flask import Flask, session, request, redirect, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from database.models import db, User, OTPCode
from flask_restx import Api
from flask_restx import Namespace, Resource, fields, reqparse
import requests
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import math, random
import vonage
from datetime import datetime, timedelta

# import config
from config import *

# Config Mail
mailapikey = MAIL_API_KEY
mailapiurl = MAIL_API_URL
s = URLSafeTimedSerializer(MAIL_TOKEN_CONFIRM_SECRET)

# Init API
api = Namespace('Confirm User', description='User confirmation API')

# Vonage
client = vonage.Client(key="f6756e22", secret="S2F8wPqPWqdiLsJH")
sms = vonage.Sms(client)

def generateOTP() :
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

@api.route('/confirm/email')
class SendUserConfirmMail(Resource):
    @jwt_required()
    def get(self):

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
        token = s.dumps(user.json(), salt='user-confirm')

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

@api.route('/confirm/email/<token>')
class CheckUserConfirmMail(Resource):
    def post(self, token):
        try:
            userToken = s.loads(token, salt='user-confirm', max_age=600)
            user = User.query.filter_by(username=userToken["username"]).first()
            if user:
                # Update confirmed in DB
                # Got to SMS OTP confirmation
                #user.confirmed = True
                #db.session.commit()
                additional_claims = {"type": "register", "step": 2}
                register_token = create_access_token(identity=user.username, additional_claims=additional_claims)
                msg = { "message": "user email is confirmed", "register_token": register_token }
            else:
                raise
        except:
            abort(404, "user email can't be confirmed")

        #additional_claims = {"type": "session", "loa": 1}
        #session_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        #msg = { "message": "user is confirmed", "session_token": session_token }
        return msg

@api.route('/confirm/phone')
class ConfirmPhone(Resource):
    # Generate and send OTP SMS code
    @jwt_required()
    def get(self):
        # Check if correct registration step
        if get_jwt().get("type") != "register" or get_jwt().get("step") != 2:
            abort(400)

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')
        if user.confirmed is True:
            abort(400, 'user is already confirmed')

        # Generate and store OTP code
        otpcode = OTPCode(code=generateOTP(), user_id=user.id)
        db.session.add(otpcode)
        db.session.commit()

        # Send OTP code (DISABLED FOR DEV)
        if ENV == "dev":
            print(otpcode.code)
        else:
            otpsms = sms.send_message(
                {
                    "from": "Noth",
                    "to": user.phone,
                    "text": "Your OTP code is %s" % otpcode.code,
                }
            )

            if otpsms["messages"][0]["status"] != "0":
                abort(500)

        additional_claims = {"type": "register", "step": 3}
        register_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        msg = { "message": "confirmation OTP SMS sent successfully", "register_token": register_token }
        return msg

    # Validate OTP SMS code
    @jwt_required()
    def post(self):
        # Check if correct registration step
        if get_jwt().get("type") != "register" or get_jwt().get("step") != 3:
            abort(400)

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')
        if user.confirmed is True:
            abort(400, 'user is already confirmed')

        # Parse and check request
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('otpcode', location='json', type=int, required=True)
        reqbody = parser.parse_args()

        # Check if valid OTP code
        otpcode = OTPCode.query.filter_by(user_id=user.id).order_by(OTPCode.created_at.desc()).first()
        if not otpcode or otpcode.code != reqbody.otpcode or otpcode.created_at < datetime.now() - timedelta(seconds=int(OTP_LIFETIME)):
            abort(401, 'invalid OTP code')

        additional_claims = {"type": "register", "step": 4}
        register_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        msg = { "message": "your mobile phone is confirmed", "register_token": register_token }
        return msg
