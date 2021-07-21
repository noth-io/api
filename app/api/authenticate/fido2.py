from __future__ import print_function, absolute_import, unicode_literals
from flask import Blueprint
from flask import current_app as app
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.client import ClientData
from fido2.server import Fido2Server
from fido2.ctap2 import AttestationObject, AuthenticatorData, AttestedCredentialData
from fido2 import cbor
from flask import Flask, session, request, redirect, abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from models import db, User, Fido2Credential

# Blueprint Configuration
fido2_authenticate_bp = Blueprint(
    'fido2_authenticate_bp', __name__
    )

rp = PublicKeyCredentialRpEntity("localhost", "Demo server")
server = Fido2Server(rp)

credentials = []


@fido2_authenticate_bp.route("/begin", methods=["POST"])
@jwt_required(optional=True)
def authenticate_begin():

    current_identity = get_jwt_identity()
    if not current_identity:
        abort(401)
    
    # GET CREDENTIALS FROM DB
    cs = Fido2Credential.query.all()
    for c in cs:
        credentials.append(AttestedCredentialData(c.attestation))
    
    if not credentials:
        abort(404)

    auth_data, state = server.authenticate_begin(credentials,user_verification="discouraged")
    print(state)
    session["state"] = state
    print(session)
    print("\n\n\n\n")
    print(auth_data)
    print("\n\n\n\n")
    return cbor.encode(auth_data)


@fido2_authenticate_bp.route("/complete", methods=["POST"])
def authenticate_complete():

    # GET CREDENTIALS FROM DB
    cs = Fido2Credential.query.all()
    for c in cs:
        credentials.append(AttestedCredentialData(c.attestation))

    if not credentials:
        abort(404)

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
    print("ASSERTION OK")
    return cbor.encode({"status": "OK"})