import time
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)
from flask import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    fido2credential = db.relationship("Fido2Credential")

    def json (self):
        json = {}
        json['id'] = self.id
        json['username'] = self.username
        json['email'] = self.email
        json['firstname'] = self.firstname
        json['lastname'] = self.lastname
        json['confirmed'] = self.confirmed
        return json

    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.username
    

class Fido2Credential(db.Model):
    __tablename__ = 'fido2credential'
    id = db.Column(db.Integer, primary_key=True)
    attestation = db.Column(db.LargeBinary, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '%s' % self.attestation

class OAuth2Client(db.Model, OAuth2ClientMixin):

    ##### ON DELETE CASCADE !!! DONT WORK
    
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')

    def json(self):
        json = {}
        json['id'] = self.id
        json['client_id'] = self.client_id
        json['client_id_issued_at'] = self.client_id_issued_at
        json['client_name'] = self.client_name
        json['client_uri'] = self.client_uri
        json['grant_types'] = self.grant_types
        json['redirect_uris'] = self.redirect_uris
        json['response_types'] = self.response_types
        json['scope'] = self.scope
        json['token_endpoint_auth_method'] = self.token_endpoint_auth_method
        return json

    def json_with_secret(self):
        json = {}
        json['id'] = self.id
        json['client_id'] = self.client_id
        json['client_id_issued_at'] = self.client_id_issued_at
        json['client_secret'] = self.client_secret
        json['client_name'] = self.client_name
        json['client_uri'] = self.client_uri
        json['grant_types'] = self.grant_types
        json['redirect_uris'] = self.redirect_uris
        json['response_types'] = self.response_types
        json['scope'] = self.scope
        json['token_endpoint_auth_method'] = self.token_endpoint_auth_method
        return json


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')
