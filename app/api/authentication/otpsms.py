import vonage
from flask import Flask, jsonify, request, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt, set_access_cookies
from flask import Blueprint
from flask import current_app as app
from flask_restx import Namespace, Resource, fields, reqparse
from database.models import db, User, Fido2Credential, OTPCode
from datetime import datetime, timedelta
import math, random

# import config
from config import *
otpsms_level = 1
otpsms_step = 1

api = Namespace('OTP SMS', description='OTP SMS authentication API')

# Vonage
client = vonage.Client(key="f6756e22", secret="S2F8wPqPWqdiLsJH")
sms = vonage.Sms(client)

def generateOTP() :
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

@api.route('')
class ConfirmPhone(Resource):
    # Generate and send OTP SMS code
    @jwt_required()
    def get(self):
        # Check if correct token
        if get_jwt().get("type") != "authentication" or get_jwt().get("nextstep") != 3:
            abort(400)

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

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

        additional_claims = {"type": "authentication", "nextstep": "3S", "current_level": 3}
        auth_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        msg = { "message": "SMS OTP sent successfully", "authenticated": False, "auth_token": auth_token }
        return msg

    # Validate OTP SMS code
    @jwt_required()
    def post(self):
        # Check if correct registration step
        if get_jwt().get("type") != "authentication" or get_jwt().get("nextstep") != "3S":
            abort(400)

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        # Parse and check request
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('otpcode', location='json', type=int, required=True)
        reqbody = parser.parse_args()

        # Check if valid OTP code
        otpcode = OTPCode.query.filter_by(user_id=user.id).order_by(OTPCode.created_at.desc()).first()
        if not otpcode or otpcode.code != reqbody.otpcode or otpcode.created_at < datetime.now() - timedelta(seconds=int(OTP_LIFETIME)):
            abort(401, 'invalid OTP code')

        # Generate session token
        additional_claims = {"type": "session", "loa": 3}
        session_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        message = { "authenticated": True, "session_token": session_token }
        msg = Response(response=json.dumps(message), status=200, mimetype="application/json")
        set_access_cookies(msg, session_token)
        msg.set_cookie("authenticated", "true", secure=True, domain=AUTHENTICATED_COOKIE_DOMAIN)
        msg.set_cookie("username", user.username, secure=True, domain=AUTHENTICATED_COOKIE_DOMAIN)

        return msg