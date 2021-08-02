from flask import Flask, jsonify, request, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt, set_access_cookies
from flask import Blueprint
from flask import current_app as app
from flask_restx import Namespace, Resource, fields
from database.models import db, User
import datetime
api = Namespace('Username', description='Username authentication API')

username_level = 1
username_step = 1

@api.route('')
class UsernameAuthentication(Resource):
    @jwt_required()
    def post(self):

        # Check if correct authentication step
        if get_jwt().get("nextstep") != username_step:
            abort(400)
        
        # Get username from request
        username = request.json.get("username", None)

        # Check identity in DB
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(401, 'invalid user')

        # Calculate new auth level
        old_level = get_jwt().get("current_level")
        new_level = old_level | username_level
        print(new_level)

        # If target level reached (todo : convert to function)
        if get_jwt().get("target_level") == new_level:
            # Generate session token
            additional_claims = {"type": "session", "loa": 1}
            session_token = create_access_token(identity=user.username, additional_claims=additional_claims)
            message = { "authenticated": True, "session_token": session_token }
            msg = Response(response=json.dumps(message), status=200, mimetype="application/json")
            set_access_cookies(msg, session_token)
            msg.set_cookie("authenticated", "true", secure=True)

        else:
            additional_claims = {"type": "authentication", "target_level": get_jwt().get("target_level"), "nextstep": 2, "current_level": new_level}
            auth_token = create_access_token(identity=user.username, additional_claims=additional_claims)
            msg = { "authenticated": False, "auth_token": auth_token }

        return msg
