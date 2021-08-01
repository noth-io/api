from flask import Flask, jsonify, request, abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import Blueprint
from flask import current_app as app
from flask_restx import Namespace, Resource, fields
from database.models import db, User

api = Namespace('Init', description='Init authentication API')

init_level = 0
init_step = 0

@api.route('')
class InitAuthentication(Resource):
    def post(self):
        # TODO check if cookie/header with identity

        additional_claims = {"type": "authentication", "target_level": 3, "nextstep": 1, "current_level": init_level}
        auth_token = create_access_token(identity='', additional_claims=additional_claims)
        return jsonify(auth_token=auth_token)