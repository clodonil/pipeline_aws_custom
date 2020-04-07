from flask_restplus import reqparse, abort, Api, Resource
from werkzeug.datastructures import FileStorage
from tools.validates import Validate, change_yml_to_json


parser = reqparse.RequestParser()
parser.add_argument('payload', type=FileStorage, required=True, location='files')

class Validation(Resource):
    def post(self):
        args = parser.parse_args()
        filename = args['payload']
        file_yml = filename.read()
        file_json = change_yml_to_json(file_yml)
        validate = Validate()
        result = validate.check_template(file_json)

        if result['status']:
            msg = {"status":'success', 'message': 'template valido'}
            return msg, 201
        else:
            msg = {"status":'error', 'message': result['msg']}
            return msg, 401

