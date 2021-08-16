from __future__ import print_function, absolute_import, unicode_literals
from flask_restx import Namespace, Resource, fields
from flask import Blueprint, jsonify, json
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.client import ClientData
from fido2.server import Fido2Server
from fido2.ctap2 import AttestationObject, AuthenticatorData, AttestedCredentialData
from fido2 import cbor
from flask import Flask, session, request, redirect, abort, Response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from database.models import db, User, Fido2Credential
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# import config
from config import *

api = Namespace('Fido 2 Register', description='Fido 2 register API')

# Fido 2 variables
rp = PublicKeyCredentialRpEntity(FIDO2_RP, FIDO2_NAME)
server = Fido2Server(rp)
credentials = []
s = URLSafeTimedSerializer(FIDO2STATE_SECRET)

@api.route('')
class FIDO2Creds(Resource):
    # Get all FIDO2 credentials for authenticated user
    @jwt_required(locations=["cookies"])
    def get(self):
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        creds = Fido2Credential.query.filter_by(user_id=user.id)
        response = []
        for cred in creds:
            response.append(cred.json())

        resp = Response(response=json.dumps(response, default=str), status=200, mimetype="application/json")
        return resp

@api.route('/register/begin')
class Fido2RegisterBegin(Resource):
    @jwt_required(locations=["cookies"])
    def post(self):

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401)

        # Check if Android with user agent
        if "Android" in request.headers.get('User-Agent'):
            authenticator_attachment = "platform"
        else:
            authenticator_attachment = "cross-platform"

        registration_data, state = server.register_begin(
            {
                "id": bytes(user.id),
                "name": user.username,
                "displayName": user.firstname,
                "icon": "https://example.com/image.png",
            },
            credentials,
            user_verification="discouraged",
            authenticator_attachment=authenticator_attachment,
            resident_key="False"
        )

        #session["state"] = state
        print("\n\n\n\n")
        print(registration_data)
        print("\n\n\n\n")
        msg = Response(response=cbor.encode(registration_data))
        msg.set_cookie("fido2register", s.dumps(state, salt='fido2register'), secure=True)
        return msg

@api.route('/register/complete')
class Fido2RegisterComplete(Resource):
    @jwt_required(locations=["cookies"])
    def post(self):

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401)

        
        state = s.loads(request.cookies.get('fido2register'), salt='fido2register', max_age=60)

        data = cbor.decode(request.get_data())
        client_data = ClientData(data["clientDataJSON"])
        att_obj = AttestationObject(data["attestationObject"])
        print("clientData", client_data)
        print("AttestationObject:", att_obj)

        auth_data = server.register_complete(state, client_data, att_obj)

        # Add credential to DB
        db.session.add(Fido2Credential(attestation=auth_data.credential_data, user_id=user.id))
        db.session.commit()   

        print("REGISTERED CREDENTIAL:", auth_data.credential_data)
        msg = Response(response=cbor.encode({"status": "OK"}))
        msg.set_cookie("fido2register", "", secure=True, expires=0)
        return msg
