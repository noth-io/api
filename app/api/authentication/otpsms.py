import vonage
from flask import Flask, jsonify, request, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt, set_access_cookies
from flask import Blueprint
from flask import current_app as app
from flask_restx import Namespace, Resource, fields
from database.models import db, User, Fido2Credential
import datetime
import math, random
# import config
from config import *

api = Namespace('OTP SMS', description='OTP SMS authentication API')

#username_level = 1
#username_step = 1
client = vonage.Client(key="f6756e22", secret="S2F8wPqPWqdiLsJH")
sms = vonage.Sms(client)

def generateOTP() :
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

@api.route('')
class OTPSMSAuthentication(Resource):
    #@jwt_required()
    def get(self):
        responseData = sms.send_message(
            {
                "from": "Noth",
                "to": "33617454309",
                "text": "A text message sent using the Nexmo SMS API",
            }
        )

        if responseData["messages"][0]["status"] == "0":
            msg = 'ok'
        else:
            msg = 'ko'
        #msg = generateOTP()

        return msg