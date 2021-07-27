import os
from flask import Flask, redirect
from database.models import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
# oauth
from oauth2 import config_oauth
from api.oauth2.oauth2 import bp as oauth2_bp

# import api
from api.authentication.api import blueprint as authentication_api
from api.users.api import blueprint as users_api
# import config
from config import *

app = Flask(__name__, static_url_path="")
app.debug = True

# CORS
CORS(app, supports_credentials=True)

# Secret key for sessions
app.secret_key = SESSION_SECRET_KEY
#app.config['SESSION_COOKIE_SAMESITE'] = "None"
#app.config['SESSION_COOKIE_SECURE'] = "True"
app.config['SESSION_COOKIE_HTTPONLY'] = False

# DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%s:%s@%s/%s' % (DB_USER, DB_PASSWORD, DB_URL, DB_NAME)
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)

# OAUTH2
app.config["OAUTH2_JWT_ENABLED"] = OAUTH2_JWT_ENABLED
app.config["OAUTH2_JWT_ISS"] = OAUTH2_JWT_ISS
app.config["OAUTH2_JWT_KEY"] = OAUTH2_JWT_KEY
app.config["OAUTH2_JWT_ALG"] = OAUTH2_JWT_ALG



# Setup the Flask-JWT-Extended extension
jwt_secret_key = os.urandom(32)
app.config["JWT_SECRET_KEY"] = "changeme"
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(authentication_api)
app.register_blueprint(users_api)
app.register_blueprint(oauth2_bp)


@app.route("/")
def index():    
    return redirect("/index.html")

