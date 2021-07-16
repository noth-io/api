"""Initialize Flask app."""
from flask import Flask
from api.fido2 import routes

app = Flask(__name__, instance_relative_config=False)
app.register_blueprint(routes.fido2_bp)

if __name__ == "__main__":
    print(__doc__)
    app.run(ssl_context="adhoc", debug=False)
