from flask_restplus import reqparse, abort, Api, Resource


parser = reqparse.RequestParser()
parser.add_argument('payload', type=str, required=True, location='json')

class Status(Resource):
    def get(self):
        msg = {"status":'success', 'message': 'online'}
        return msg, 201

