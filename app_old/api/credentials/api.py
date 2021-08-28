from flask_restx import Api
from flask_restx import Namespace, Resource, fields
from flask import Blueprint
from .fido2 import api as fido2

# Init API
blueprint = Blueprint('Credentials API', __name__, url_prefix='/credentials')
api = Api(blueprint,
    title='Noth credentials API',
    version='1.0',
    description='Noth credentials API documentation',
    doc='/doc')

# Add namescapes
api.add_namespace(fido2, path='/fido2')