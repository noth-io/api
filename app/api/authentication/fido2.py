from __future__ import print_function, absolute_import, unicode_literals
from flask_restx import Namespace, Resource, fields
from flask import Blueprint, jsonify
from flask import current_app as app
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.client import ClientData
from fido2.server import Fido2Server
from fido2.ctap2 import AttestationObject, AuthenticatorData, AttestedCredentialData
from fido2 import cbor
from flask import Flask, session, request, redirect, abort, Response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from database.models import db, User, Fido2Credential

# import config
from config import *

api = Namespace('Fido2Authentication', description='Fido 2 authentication API')

# Fido 2 variables
rp = PublicKeyCredentialRpEntity(FIDO2_RP, FIDO2_NAME)
server = Fido2Server(rp)
credentials = []

fido2_authstate = 4

@api.route('/begin')
class Fido2AuthenticationBegin(Resource):
    @jwt_required()
    def post(self):

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        # Get credential from DB
        user_creds = Fido2Credential.query.filter_by(user_id=user.id).all()
        print(user_creds)
        if not user_creds:
            abort(401, 'no fido2 credential registered')
        for cred in user_creds:
            credentials.append(AttestedCredentialData(cred.attestation))

        auth_data, state = server.authenticate_begin(credentials,user_verification="discouraged")
        print(state)
        session["state"] = state
        print(session)
        print("\n\n\n\n")
        print(auth_data)
        print("\n\n\n\n")
        return Response(response=cbor.encode(auth_data))


@api.route('/complete')
class Fido2AuthenticationComplete(Resource):
    @jwt_required()
    def post(self):

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

        server.authenticate_complete(
            session.pop("state"),
            credentials,
            credential_id,
            client_data,
            auth_data,
            signature,
        )

        # Define new auth state
        state = get_jwt().get("state")
        newstate = state | fido2_authstate

        additional_claims = {"state": newstate}
        access_token = create_access_token(identity=current_identity, additional_claims=additional_claims)
        return jsonify(access_token=access_token)