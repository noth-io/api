from __future__ import print_function, absolute_import, unicode_literals
from flask import Blueprint, jsonify, json
from flask import current_app as app
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.client import ClientData
from fido2.server import Fido2Server
from fido2.ctap2 import AttestationObject, AuthenticatorData, AttestedCredentialData
from fido2 import cbor
from flask import Flask, session, request, redirect, abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from database.models import db, User, Fido2Credential

# Blueprint Configuration
fido2_register_bp = Blueprint(
    'fido2_register_bp', __name__
    )

rp = PublicKeyCredentialRpEntity("localhost", "Demo server")
server = Fido2Server(rp)

credentials = []

@fido2_register_bp.route("/begin", methods=["POST"])
@jwt_required()
def register_begin():

    # Check identity in DB
    current_identity = get_jwt_identity()
    user = User.query.filter_by(username=current_identity).first()
    if not user:
        abort(401)

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
    #print(json.loads(registration_data))
    #print(json.loads(cbor.encode(registration_data)))

    #data = {}
    #data["state"] = state
    #data["registration_data"] = cbor.encode(registration_data)
    #print(data)
    #print(cbor.encode(registration_data).decode('utf-8'))
    return cbor.encode(registration_data)
    #return jsonify(data)
    #return  '{} {}'.format(cbor.encode(registration_data), state)

@fido2_register_bp.route("/complete", methods=["POST"])
@jwt_required()
def register_complete():

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
    return cbor.encode({"status": "OK"})
