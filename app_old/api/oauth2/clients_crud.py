import time
from flask import Flask, jsonify, request, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, jwt_manager
from flask import Blueprint
from flask import current_app as app
from flask_restx import Namespace, Resource, fields, reqparse
from database.models import db, OAuth2Client, User
from werkzeug.security import gen_salt

api = Namespace('Clients', description='OAuth2 Clients CRUD API')

@api.route('')
class Clients(Resource):
    # Get all Clients for authenticated user
    @jwt_required(locations=["cookies", "headers"])
    def get(self):
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        clients = OAuth2Client.query.filter_by(user_id=user.id)
        response = []
        for client in clients:
            response.append(client.json())

        resp = Response(response=json.dumps(response, default=str), status=200, mimetype="application/json")
        return resp

    # Create client
    @jwt_required(locations=["cookies", "headers"])
    def post(self):
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        # Parse and check request
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('client_name', location='json', required=True)
        parser.add_argument('client_uri', location='json', required=True)
        parser.add_argument('grant_types', type=list, location='json', required=True)
        parser.add_argument('redirect_uris', type=list, location='json', required=True)
        parser.add_argument('response_types', type=list, location='json', required=True)
        parser.add_argument('scope', location='json', required=True)
        parser.add_argument('token_endpoint_auth_method', location='json', required=True)

        # Build client object
        client_metadata = parser.parse_args()
        client_id = gen_salt(24)
        client = OAuth2Client(client_id=client_id, user_id=user.id)
        client.client_id_issued_at = int(time.time())
        if client.token_endpoint_auth_method == 'none':
            client.client_secret = ''
        else:
            client.client_secret = gen_salt(48)
        client.set_client_metadata(client_metadata)

        # Insert into DB
        db.session.add(client)
        db.session.commit()

        return client.json_with_secret()

@api.route('/<id>')
class SingleClient(Resource):
    # Delete client
    @jwt_required(locations=["cookies", "headers"])
    def delete(self, id):
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        # Get client from DB
        client = OAuth2Client.query.filter_by(id=id, user_id=user.id).first()
        if not client:
            abort(404, 'client not found')
        
        # Delete user in DB
        db.session.delete(client)
        db.session.commit()

        msg = { "message": "client successfully deleted" }
        return msg
   
    # Update client
    @jwt_required(locations=["cookies", "headers"])
    def put(self, id):
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        # Parse and check request
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('id', location='json', required=True)
        parser.add_argument('client_id', location='json', required=True)
        parser.add_argument('client_id_issued_at', location='json', required=True)
        parser.add_argument('client_name', location='json', required=True)
        parser.add_argument('client_uri', location='json', required=True)
        parser.add_argument('grant_types', type=list, location='json', required=True)
        parser.add_argument('redirect_uris', type=list, location='json', required=True)
        parser.add_argument('response_types', type=list, location='json', required=True)
        parser.add_argument('scope', location='json', required=True)
        parser.add_argument('token_endpoint_auth_method', location='json', required=True)
        parser.add_argument('enabled', location='json', required=True)

        # Get client from DB
        client = OAuth2Client.query.filter_by(id=id, user_id=user.id).first()
        if not client:
            abort(404, 'client not found')

        # Build client object
        client_metadata = parser.parse_args()
        client_enabled = client_metadata['enabled']
        client_metadata.pop('id')
        client_metadata.pop('client_id')
        client_metadata.pop('client_id_issued_at')
        client_metadata.pop('enabled')
  
        client.set_client_metadata(client_metadata)
        print(client_enabled)
        client.enabled = bool(client_enabled)

        print(client)
        # Update in DB
        db.session.commit()

        return client.json()

    # Get client
    @jwt_required(locations=["cookies", "headers"])
    def get(self, id):
        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        # Get client from DB
        client = OAuth2Client.query.filter_by(id=id, user_id=user.id).first()
        if not client:
            abort(404, 'client not found')
        
        return client.json()