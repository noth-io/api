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
import time

# import config
from config import *

api = Namespace('OAuth2', description='OAuth2 API')

s = URLSafeTimedSerializer(OAUTH2_CONSENT_TOKEN_SECRET)

def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None

"""
@bp.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        session['id'] = user.id
        return redirect('/oauth/')
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []
    return render_template('home.html', user=user, clients=clients)
"""

def split_by_crlf(s):
    return [v for v in s.splitlines() if v]

"""
@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    user = current_user()
    if not user:
        return redirect('/oauth/')
    if request.method == 'GET':
        return render_template('create_client.html')
    form = request.form
    client_id = gen_salt(24)
    client = OAuth2Client(client_id=client_id, user_id=user.id)
    # Mixin doesn't set the issue_at date
    client.client_id_issued_at = int(time.time())
    if client.token_endpoint_auth_method == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)

    client_metadata = {
        "client_name": form["client_name"],
        "client_uri": form["client_uri"],
        "grant_types": split_by_crlf(form["grant_type"]),
        "redirect_uris": split_by_crlf(form["redirect_uri"]),
        "response_types": split_by_crlf(form["response_type"]),
        "scope": form["scope"],
        "token_endpoint_auth_method": form["token_endpoint_auth_method"]
    }
    client.set_client_metadata(client_metadata)
    db.session.add(client)
    db.session.commit()
    return redirect('/oauth/')
"""

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

"""
@bp.route('/userinfo')
@require_oauth('profile')
def api_me():
    return jsonify(generate_user_info(current_token.user, current_token.scope))
"""