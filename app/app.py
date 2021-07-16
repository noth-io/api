import os
from flask import Flask, redirect
from api.fido2 import routes
from models import db, User

def create_app():
    app = Flask(__name__, static_url_path="")
    app.debug = True

    # Secret key for sessions
    app.secret_key = os.urandom(32)

    # DB
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(routes.fido2_bp)

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