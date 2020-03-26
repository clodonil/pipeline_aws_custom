from flask import Flask, flash,Blueprint, jsonify
from flask_restplus import Api
from resources.Hello import Hello
from config import *



app = Blueprint('api', __name__)
api = Api(app)

# Route
api.add_resource(Hello, '/Hello')

