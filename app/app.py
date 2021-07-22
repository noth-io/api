import os
from flask import Flask, redirect
from api.authenticate import username, fido2 as fido2_authenticate
from api.register import fido2 as fido2_register
from models import db, User
from flask_jwt_extended import JWTManager
from fido2.webauthn import PublicKeyCredentialRpEntity
from fido2.server import Fido2Server

def create_app():
    app = Flask(__name__, static_url_path="")
    app.debug = True

    # Secret key for sessions
    app.secret_key = os.urandom(32)
    #jwt_secret_key = os.urandom(32)

    # DB
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(User(username="jdoe", email="jdoe@example.com", firstname="John", surname="Doe"))
        db.session.commit() 

    # Setup the Flask-JWT-Extended extension
    jwt_secret_key = os.urandom(32)
    app.config["JWT_SECRET_KEY"] = "changeme"
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(username.username_bp, url_prefix='/api/authenticate/')
    app.register_blueprint(fido2_authenticate.fido2_authenticate_bp, url_prefix='/api/authenticate/fido2')
    app.register_blueprint(fido2_register.fido2_register_bp, url_prefix='/api/register/fido2')

    @app.route("/")
    def index():    
        return redirect("/index.html")

    return app 


def setup_database(app):
    with app.app_context():
        db.create_all()
    db.session.add(User(username="Flask", email="example@example.com"))
    db.session.commit()   


if __name__ == '__main__':
    app = create_app()

    # Because this is just a demonstration we set up the database like this.
    #if not os.path.isfile('example.sqlite'):
    #  setup_database(app)

    #print(__doc__)
    #app.run(ssl_context="adhoc")