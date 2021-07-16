from __future__ import print_function, absolute_import, unicode_literals
from flask import Blueprint
from flask import current_app as app
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.client import ClientData
from fido2.server import Fido2Server
from fido2.ctap2 import AttestationObject, AuthenticatorData
from fido2 import cbor
from flask import Flask, session, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy

# Blueprint Configuration
fido2_bp = Blueprint(
    'fido2_bp', __name__
    )

rp = PublicKeyCredentialRpEntity("localhost", "Demo server")
server = Fido2Server(rp)

credentials = []

@fido2_bp.route("/")
def index():
    return redirect("/index.html")


@fido2_bp.route("/api/register/begin", methods=["POST"])
def register_begin():
    registration_data, state = server.register_begin(
        {
            "id": b"user_id",
            "name": "a_user",
            "displayName": "A. User",
            "icon": "https://example.com/image.png",
        },
        credentials,
        user_verification="discouraged",
        authenticator_attachment="cross-platform",
    )

    session["state"] = state
    print("\n\n\n\n")
    print(registration_data)
    print("\n\n\n\n")
    return cbor.encode(registration_data)


@fido2_bp.route("/api/register/complete", methods=["POST"])
def register_complete():
    data = cbor.decode(request.get_data())
    client_data = ClientData(data["clientDataJSON"])
    att_obj = AttestationObject(data["attestationObject"])
    print("clientData", client_data)
    print("AttestationObject:", att_obj)

    auth_data = server.register_complete(session["state"], client_data, att_obj)

    credentials.append(auth_data.credential_data)
    print("REGISTERED CREDENTIAL:", auth_data.credential_data)
    return cbor.encode({"status": "OK"})


@fido2_bp.route("/api/authenticate/begin", methods=["POST"])
def authenticate_begin():

    print(credentials)

    if not credentials:
        abort(404)

    auth_data, state = server.authenticate_begin(credentials,user_verification="discouraged")
    session["state"] = state
    print("\n\n\n\n")
    print(auth_data)
    print("\n\n\n\n")
    return cbor.encode(auth_data)


@fido2_bp.route("/api/authenticate/complete", methods=["POST"])
def authenticate_complete():
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