from __future__ import print_function, absolute_import, unicode_literals
from flask_restx import Namespace, Resource, fields
from flask import Blueprint, jsonify, json
from flask import current_app as app
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.client import ClientData
from fido2.server import Fido2Server
from fido2.ctap2 import AttestationObject, AuthenticatorData, AttestedCredentialData
from fido2 import cbor
from flask import Flask, session, request, redirect, abort, Response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt, set_access_cookies
from database.models import db, User, Fido2Credential
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# import config
from config import *

api = Namespace('Fido2Authentication', description='Fido 2 authentication API')

# Fido 2 variables
rp = PublicKeyCredentialRpEntity(FIDO2_RP, FIDO2_NAME)
server = Fido2Server(rp)
credentials = []
s = URLSafeTimedSerializer(FIDO2STATE_SECRET)

fido2_level = 3
fido2_step = 3

@api.route('/begin')
class Fido2AuthenticationBegin(Resource):
    @jwt_required()
    def post(self):

        # Check if correct authentication step
        if get_jwt().get("nextstep") != fido2_step:
            abort(400)

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        # Check if Android with user agent
        if "Android" in request.headers.get('User-Agent'):
            authenticator_attachment = "platform"
        else:
            authenticator_attachment = "cross-platform"

        # Get credential from DB
        user_creds = Fido2Credential.query.filter_by(user_id=user.id).all()
        print(user_creds)
        if not user_creds:
            abort(401, 'no fido2 credential registered')
        for cred in user_creds:
            credentials.append(AttestedCredentialData(cred.attestation))

        auth_data, state = server.authenticate_begin(credentials,user_verification="discouraged",authenticator_attachment=authenticator_attachment)
        #print(state)
        #session["state"] = state
        #print(session)
        print("\n\n\n\n")
        print(auth_data)
        print("\n\n\n\n")

        msg = Response(response=cbor.encode(auth_data))
        msg.set_cookie("fido2auth", s.dumps(state, salt='fido2auth'), secure=True)

        return msg


@api.route('/complete')
class Fido2AuthenticationComplete(Resource):
    @jwt_required()
    def post(self):

        # Check if correct authentication step
        if get_jwt().get("nextstep") != fido2_step:
            abort(400)
            
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401)

        # Get credential from DB
        user_creds = Fido2Credential.query.filter_by(user_id=user.id).all()
        if not user_creds:
            abort(404)
        for cred in user_creds:
            credentials.append(AttestedCredentialData(cred.attestation))

        print(request.get_data())
        data = cbor.decode(request.get_data())
        credential_id = data["credentialId"]
        client_data = ClientData(data["clientDataJSON"])
        auth_data = AuthenticatorData(data["authenticatorData"])
        signature = data["signature"]
        print("clientData", client_data)
        print("AuthenticatorData", auth_data)

        state = s.loads(request.cookies.get('fido2auth'), salt='fido2auth', max_age=60)

        server.authenticate_complete(
            state,
            credentials,
            credential_id,
            client_data,
            auth_data,
            signature,
        )

        # Define new auth state
        #state = get_jwt().get("state")
        #newstate = state | fido2_authstate

        #additional_claims = {"state": newstate}
        #access_token = create_access_token(identity=current_identity, additional_claims=additional_claims)
        #return jsonify(access_token=access_token)
        
        ### TEMPORARY
        # Generate session token
        additional_claims = {"type": "session", "loa": 3}
        session_token = create_access_token(identity=user.username, additional_claims=additional_claims)
        message = { "authenticated": True, "session_token": session_token }
        msg = Response(response=json.dumps(message), status=200, mimetype="application/json")
        set_access_cookies(msg, session_token)
        msg.set_cookie("authenticated", "true", secure=True, domain=AUTHENTICATED_COOKIE_DOMAIN)
        msg.set_cookie("username", user.username, secure=True, domain=AUTHENTICATED_COOKIE_DOMAIN)
        msg.set_cookie("fido2auth", "", secure=True, expires=0)

        return msg