from flask import Flask, jsonify, request, abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import Blueprint
from flask import current_app as app
from flask_restx import Namespace, Resource, fields
from database.models import db, User

api = Namespace('Username', description='Username authentication API')

username_authlevel = 1

@api.route('')
class UsernameAuthentication(Resource):
    def post(self):
        username = request.json.get("username", None)
        # Check identity in DB
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(401, 'invalid user')

        additional_claims = {"level": username_authlevel}
        access_token = create_access_token(identity=username, additional_claims=additional_claims)
        return jsonify(access_token=access_token)
