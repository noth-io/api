import time
from flask import Blueprint, request, session, abort, Response
from flask import render_template, redirect, jsonify, json
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from database.models import db, User, OAuth2Client
from oauth2 import authorization, require_oauth, generate_user_info
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, decode_token, get_jwt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
# import config
from config import *

api = Namespace('OAuth2', description='OAuth2 API')

s = URLSafeTimedSerializer(OAUTH2_CONSENT_TOKEN_SECRET)

def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None



@api.route('/authorize')
class AuthorizationEndpoint(Resource):
    @jwt_required()
    def get(self):

        # Check identity in DB
        current_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        consent_token = request.headers.get('consent_token')

        if consent_token:

            try:
                token = s.loads(consent_token, salt='consent', max_age=OAUTH2_CONSENT_LIFETIME)
            except SignatureExpired as error:
                abort(400, "consent token expired")

            return authorization.create_authorization_response(grant_user=user)

        else:
            try:
                grant = authorization.validate_consent_request(end_user=user)
            except OAuth2Error as error:
                abort(400, dict(error.get_body()))
            
            msg = {
                "message": "consent_required",
                #"client": grant.client.client_name,
                #"scopes": grant.request.scope.split(),
                "consent_token_lifetime": OAUTH2_CONSENT_LIFETIME
            }

            token = s.dumps(msg, salt='consent')
            msg["consent_token"] = token

            return jsonify(msg)

@api.route('/token')
class TokenEndpoint(Resource):
    def post(self):
        return authorization.create_token_response()

@api.route('/userinfo')
class UserinfoEndpoint(Resource):
    @require_oauth('profile')
    def get(self):
        return jsonify(generate_user_info(current_token.user, current_token.scope))