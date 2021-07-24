from flask_restx import Api
from flask_restx import Namespace, Resource, fields
from flask import Blueprint
from .users_crud import api as users_crud
from .users_verify import api as users_verify

# Init API
blueprint = Blueprint('Users API', __name__, url_prefix='/users')
api = Api(blueprint,
    title='Noth users API',
    version='1.0',
    description='Noth users API documentation',
    doc='/doc')

# Add namescapes
api.add_namespace(users_crud, path='/')
api.add_namespace(users_verify, path='/')