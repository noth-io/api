from flask_restx import Api
from flask_restx import Namespace, Resource, fields
from flask import Blueprint
from .mail import api as mail
from .username import api as username

# Init API
blueprint = Blueprint('Authentication API', __name__, url_prefix='/authentication')
api = Api(blueprint,
    title='Noth authentication API',
    version='1.0',
    description='Noth authentication API documentation',
    doc='/doc')

# Add namescapes
api.add_namespace(username, path='/username')
api.add_namespace(mail, path='/mail')