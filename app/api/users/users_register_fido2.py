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

# import config
from config import *

api = Namespace('Fido 2 Register', description='Fido 2 register API')

# Fido 2 variables
rp = PublicKeyCredentialRpEntity(FIDO2_RP, FIDO2_NAME)
server = Fido2Server(rp)
credentials = []

@api.route('/fido2/begin')
class Fido2RegisterBegin(Resource):
    @jwt_required()
    def post(self):

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401)

        print("test")
        registration_data, state = server.register_begin(
            {
                "id": bytes(user.id),
                "name": user.username,
                "displayName": user.firstname,
                "icon": "https://example.com/image.png",
            },
            credentials,
            user_verification="discouraged",
            authenticator_attachment="cross-platform",
            resident_key="True"
        )

        session["state"] = state
        print("\n\n\n\n")
        print(registration_data)
        print("\n\n\n\n")
        return Response(response=cbor.encode(registration_data))

@api.route('/fido2/complete')
class Fido2RegisterComplete(Resource):
    @jwt_required()
    def post(self):

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401)

        data = cbor.decode(request.get_data())
        client_data = ClientData(data["clientDataJSON"])
        att_obj = AttestationObject(data["attestationObject"])
        print("clientData", client_data)
        print("AttestationObject:", att_obj)

        auth_data = server.register_complete(session["state"], client_data, att_obj)

        # Add credential to DB
        db.session.add(Fido2Credential(attestation=auth_data.credential_data, user_id=user.id))
        db.session.commit()   

        print("REGISTERED CREDENTIAL:", auth_data.credential_data)
        return Response(response=cbor.encode({"status": "OK"}))
