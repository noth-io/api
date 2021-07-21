from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import Blueprint
from flask import current_app as app

# Blueprint Configuration
login_bp = Blueprint(
    'login_bp', __name__
    )

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@login_bp.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    if username != "jdoe":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@login_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
