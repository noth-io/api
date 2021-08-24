from flask import Flask, jsonify, request, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt, set_access_cookies
from flask import Blueprint
from flask import current_app as app
from flask_restx import Namespace, Resource, fields
from database.models import db, User, Fido2Credential
import datetime
# import config
from config import *

api = Namespace('Token exchange', description='Token exchange authentication API')

@api.route('')
class TokenExchange(Resource):
    @jwt_required()
    def get(self):

        # Check token type and step
        if get_jwt().get("type") == "register" and get_jwt().get("step") == 4 :
        
            # Check identity in DB
            current_identity = get_jwt_identity()
            user = User.query.filter_by(username=current_identity).first()
            if not user:
                abort(401, 'invalid user')

            # Generate session token
            additional_claims = {"type": "session", "loa": 3}
            session_token = create_access_token(identity=user.username, additional_claims=additional_claims)
            message = { "authenticated": True, "session_token": session_token }
            msg = Response(response=json.dumps(message), status=200, mimetype="application/json")
            set_access_cookies(msg, session_token)
            msg.set_cookie("authenticated", "true", secure=True, domain=AUTHENTICATED_COOKIE_DOMAIN)
            msg.set_cookie("username", user.username, secure=True, domain=AUTHENTICATED_COOKIE_DOMAIN)
            
        else:
            abort(401, "token can't be echanged")

        return msg
