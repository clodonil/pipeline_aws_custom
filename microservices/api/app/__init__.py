from flask import Flask
from flask_restplus import Api
from config import *

app = Flask(__name__,)
app.config.from_object('config')

api = Api(app, prefix='/api/v1')

# Controllers
#from app import backend

from app.controllers.validate import *
from app.controllers.status import *
#from app.controllers.create_template import *


api.add_resource(Validation, '/validate')
api.add_resource(Status, '/status')
#ai.add_resource(Template, '/template')
#api.add_resource(Request, '/request')
#api.add_resource(Pipeline, '/pipeline')

