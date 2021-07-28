from flask import Blueprint, json
from flask import Flask, session, request, redirect, abort, Response, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from database.models import db, User
from flask_restx import Api
from flask_restx import Namespace, Resource, fields

# Init API
api = Namespace('Users CRUD', description='Users CRUD API')

@api.route('')
class Users(Resource):
    # Get all Users
    def get(self):
        users = User.query.all()
        response = []
        for user in users:
            response.append(user.json())

        resp = Response(response=json.dumps(response, default=str), status=200, mimetype="application/json")
        return resp

    # Create User
    def post(self):
        # Get body form data
        username = request.form['username']
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']

        # Insert in DB
        user = User(username=username, email=email, firstname=firstname, lastname=lastname)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception as error:
            if "UNIQUE constraint" in str(error):
                abort(400, 'user with this username or email is already registered')
            else:
                abort(500)

        return user.json(), 201

@api.route('/<id>')
class SingleUsers(Resource):
    # Delete User
    def delete(self, id):
        # Get user from DB
        user = User.query.filter_by(id=id).first()
        if not user:
            abort(404, 'user not found')
        
        # Delete user in DB
        db.session.delete(user)
        db.session.commit()

        msg = { "message": "user successfully deleted" }
        return msg

    # Get User
    def get(self, id):
        # Get user from DB
        user = User.query.filter_by(id=id).first()
        if not user:
            abort(404, 'user not found')
    
        return user.json()