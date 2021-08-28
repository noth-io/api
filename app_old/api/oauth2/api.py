from flask_restx import Api
from flask_restx import Namespace, Resource, fields
from flask import Blueprint
from .oauth2 import api as oauth2
from .clients_crud import api as clients

# Init API
blueprint = Blueprint('OAuth2 API', __name__, url_prefix='/oauth2')
api = Api(blueprint,
    title='OAuth2 API',
    version='1.0',
    description='OAuth2 API documentation',
    doc='/doc')

# Add namescapes
api.add_namespace(oauth2, path='/')
api.add_namespace(clients, path='/clients')