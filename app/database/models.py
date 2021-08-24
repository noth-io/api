import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy import MetaData
from sqlalchemy.sql import func
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)
from flask import json

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=False)
    phone = db.Column(db.Unicode(255), unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    isadmin = db.Column(db.Boolean, nullable=False, default=False)

    def json (self):
        json = {}
        json['id'] = self.id
        json['username'] = self.username
        json['email'] = self.email
        json['firstname'] = self.firstname
        json['lastname'] = self.lastname
        json['phone'] = self.phone
        json['confirmed'] = self.confirmed
        json['isadmin'] = self.isadmin
        return json

    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.username
    
### AUTHENTICATION
class AuthMethods(db.Model):
    __tablename__ = 'auth_methods'

    auth_sequence_id = db.Column(db.ForeignKey('auth_sequence.id'), primary_key=True)
    auth_method_id = db.Column(db.ForeignKey('auth_method.id'), primary_key=True)
    step = db.Column(db.Integer, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    auth_method = db.relationship("AuthMethod")

    def json(self):
        json = {}
        json['id'] = self.auth_method.id
        json['name'] = self.auth_method.name
        #json['auth_method_level'] = self.auth_method.level
        #json['auth_method_enabled'] = self.auth_method.enabled
        json['step'] = self.step
        json['enabled'] = self.enabled
        return json

class AuthMethod(db.Model):
    __tablename__ = 'auth_method'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    #enabled = db.Column(db.Boolean, nullable=False, default=True)
    #level = db.Column(db.Integer, nullable=False)

    def json(self):
        json = {}
        json['id'] = self.id
        json['name'] = self.name
        #json['level'] = self.level
        #json['enabled'] = self.enabled
        return json

class AuthSequence(db.Model):
    __tablename__ = 'auth_sequence'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    loa = db.Column(db.Integer, nullable=False)
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    auth_methods = db.relationship("AuthMethods", cascade="all, delete-orphan")
    #user = db.relationship('User', backref=backref('auth_sequence', cascade='all,delete'))

    def json(self):
        json = {}
        json['id'] = self.id
        json['name'] = self.name
        json['loa'] = self.loa
        json['enabled'] = self.enabled
        json['auth_methods'] = []
        for auth_method in self.auth_methods:
            json['auth_methods'].append(auth_method.json())
        return json

### CREDENTIALS
class Fido2Credential(db.Model):
    __tablename__ = 'fido2credential'

    id = db.Column(db.Integer, primary_key=True)
    attestation = db.Column(db.LargeBinary, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())

    user = db.relationship('User', backref=backref('fido2credential', cascade='all,delete'))

    def __repr__(self):
        return '%s' % self.attestation

    def json(self):
        json = {}
        json['id'] = self.id
        json['attestation'] = self.attestation
        json['enabled'] = self.enabled
        json['user_id'] = self.user_id

        return json

### OAUTH2
class OAuth2Client(db.Model, OAuth2ClientMixin): 
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User', backref=backref('oauth2_client', cascade='all,delete'))

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
        json['enabled'] = self.enabled
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
        json['enabled'] = self.enabled
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


### OTP

class OTPCode(db.Model):
    __tablename__ = 'otp_code'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=func.now())

    user = db.relationship('User', backref=backref('otp_code', cascade='all,delete'))

    def json(self):
        json = {}
        json['id'] = self.id
        json['code'] = self.code
        json['user_id'] = self.user_id
        json['created_at'] = self.created_at

        return json