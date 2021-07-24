from flask import Flask, jsonify, request, abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import Blueprint
from flask import current_app as app
from flask_restx import Namespace, Resource, fields
from database.models import db, User

api = Namespace('Init', description='Init authentication API')

@api.route('')
class InitAuthentication(Resource):
    def post(self):
        # TODO check if cookie/header with identity

        additional_claims = {"state": 0, "authstep": 1}
        access_token = create_access_token(identity='', additional_claims=additional_claims)
        return jsonify(access_token=access_token)