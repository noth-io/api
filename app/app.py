"""Initialize Flask app."""
from flask import Flask
from api.fido2 import routes
import os

app = Flask(__name__, static_url_path="")
app.secret_key = os.urandom(32)  # Used for session.
app.register_blueprint(routes.fido2_bp)

if __name__ == "__main__":
    print(__doc__)
    app.run(ssl_context="adhoc", debug=False)
