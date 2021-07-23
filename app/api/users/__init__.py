from __future__ import print_function, absolute_import, unicode_literals
from flask import Blueprint, jsonify
from flask import current_app as app
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.client import ClientData
from fido2.server import Fido2Server
from fido2.ctap2 import AttestationObject, AuthenticatorData, AttestedCredentialData
from fido2 import cbor
from flask import Flask, session, request, redirect, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from models import db, User, Fido2Credential

# Blueprint Configuration
users_bp = Blueprint(
    'users_bp', __name__
    )

@users_bp.route("", methods=["GET", "POST"])
#@jwt_required()
def getUsers():

    if request.method == 'GET':
        users = User.query.all()
        response = []
        for user in users:
            response.append(user.json())

        resp = Response(response=json.dumps(response, default=str), status=200, mimetype="application/json")
        return resp
    elif request.method == 'POST':
        # Get body form data
        username = request.form['username']
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']

        # Insert in DB
        user = User(username=username, email=email, firstname=firstname, surname=surname)
        db.session.add(user)
        try:
            db.session.commit()
            msg = '{"msg": "registration success"}'
            status = 201
        except Exception as error:
            if "already exists" in str(error):
                msg = '{"msg": "user with this username or email is already registered"}'
                status = 409
            else:
                msg = None
                status = 500

        resp = Response(response=msg, status=status, mimetype="application/json")
        return resp

#@users_bp.route("t", methods=["POST"])
#@jwt_required()
#def createUser():


