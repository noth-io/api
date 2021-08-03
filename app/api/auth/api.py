from flask_restx import Api
from flask_restx import Namespace, Resource, fields
from flask import Blueprint
from .methods import api as methods
from .sequences import api as sequences

# Init API
blueprint = Blueprint('Auth Objects API', __name__, url_prefix='/auth')
api = Api(blueprint,
    title='Noth auth objects API',
    version='1.0',
    description='Noth auth objects API documentation',
    doc='/doc')

# Add namescapes
api.add_namespace(methods, path='/methods')
api.add_namespace(sequences, path='/sequences')