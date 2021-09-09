import time
from flask import Flask, jsonify, request, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, jwt_manager
from flask import Blueprint
from flask import current_app as app
from flask_restx import Namespace, Resource, fields, reqparse
from database.models import db, AuthSequence
from werkzeug.security import gen_salt

api = Namespace('Auth Sequences', description='Authentication Sequences CRUD API')

@api.route('')
class AuthSequences(Resource):
    # Get all Sequences
    def get(self):
        sequences = AuthSequence.query.all()
        response = []
        for sequence in sequences:
            response.append(sequence.json())
        return response