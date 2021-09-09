import time
from flask import Flask, jsonify, request, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, jwt_manager
from flask import Blueprint
from flask import current_app as app
from flask_restx import Namespace, Resource, fields, reqparse
from database.models import db, AuthMethod
from werkzeug.security import gen_salt

api = Namespace('Auth Methods', description='Authentication Methods CRUD API')

@api.route('')
class AuthMethods(Resource):
    # Get all Methods
    def get(self):
        methods = AuthMethod.query.all()
        response = []
        for method in methods:
            response.append(method.json())
        return response