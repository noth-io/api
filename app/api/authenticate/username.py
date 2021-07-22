from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import Blueprint
from flask import current_app as app

# Blueprint Configuration
username_bp = Blueprint(
    'username_bp', __name__
    )

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@username_bp.route("/username", methods=["POST"])
def login():
    username = request.json.get("username", None)
    if username != "jdoe":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)
