import time
from flask import Blueprint, request, session, abort, Response, make_response, render_template, redirect, jsonify, json
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from database.models import db, User, OAuth2Client
from oauth2 import authorization, require_oauth, generate_user_info
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, decode_token, get_jwt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import base64
# import config
from config import *

api = Namespace('OAuth2', description='OAuth2 API')
s = URLSafeTimedSerializer(OAUTH2_CONSENT_TOKEN_SECRET)

@api.route('/authorize')
class AuthorizationEndpoint(Resource):
    @jwt_required(locations=["cookies", "headers"], optional=True)
    def get(self):

        # Check if JWT provided
        if not get_jwt():
            # If no, redirect to login UI
            msg = {
                "message": "login_required",
                "target": request.url,
            }
            response = make_response(redirect("%s/login/%s" % (NOTH_UI_URL, base64.urlsafe_b64encode(json.dumps(msg).encode()).decode())))
            return response
            
        # Check identity in DB
        current_identity = get_jwt_identity()
        print(current_identity)
        user = User.query.filter_by(username=current_identity).first()
        if not user:
            abort(401, 'invalid user')

        consent_token = request.cookies.get('consentToken')

        if consent_token:

            try:
                token = s.loads(consent_token, salt='consent', max_age=OAUTH2_CONSENT_LIFETIME)
                if token["authorize_request"] != request.full_path:
                    response = Response(response=json.dumps({ "message": "invalid consent token" }), status=400, mimetype="application/json")
                    response.set_cookie("consentToken", "", secure=True, expires=0)
                    return response
            except SignatureExpired as error:
                response = Response(response=json.dumps({ "message": "consent token expired" }), status=400, mimetype="application/json")
                response.set_cookie("consentToken", "", secure=True, expires=0)
                return response

            response = authorization.create_authorization_response(grant_user=user)
            response.set_cookie("consentToken", "", secure=True, expires=0)
            return response

        else:
            try:
                grant = authorization.validate_consent_request(end_user=user)
            except OAuth2Error as error:
                abort(400, dict(error.get_body()))
            
            msg = {
                "message": "consent_required",
                "authorize_request": request.full_path,
                "client_name": grant.client.client_name,
                "scopes": grant.request.scope.split(),
                "consent_token_lifetime": OAUTH2_CONSENT_LIFETIME
            }

            token = s.dumps(msg, salt='consent')
            #msg["consent_token"] = token
            response = make_response(redirect("%s%s/%s" % (NOTH_UI_URL, OAUTH2_CONSENT_UI_PATH, base64.urlsafe_b64encode(json.dumps(msg).encode()).decode())))
            response.set_cookie('consentToken', token, secure=True, max_age=OAUTH2_CONSENT_LIFETIME)
            return response

            # set cookie with token
            #return redirect("%s%s/%s" % (NOTH_UI_URL, OAUTH2_CONSENT_UI_PATH, base64.urlsafe_b64encode(json.dumps(msg).encode()).decode()))
            #return jsonify(msg)

@api.route('/token')
class TokenEndpoint(Resource):
    def post(self):
        return authorization.create_token_response()

@api.route('/userinfo')
class UserinfoEndpoint(Resource):
    @require_oauth('profile')
    def get(self):
        return jsonify(generate_user_info(current_token.user, current_token.scope))