from flask_restful import Resource, reqparse
from app.services.set_api_key_service import SetApiKeyService
import os
from app.main.settings import Config

USER_FOLDER = os.path.abspath(os.path.join(Config.CHROMA_DB_PATH, 'user'))
SET_API_KEY_ROUTE = '/set-api-key'

class SetApiKey(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        # Add the api_key and user_id argument to the parser
        self.parser.add_argument('api_key', type=str, location='json', required=True, help='API key is required')
        self.parser.add_argument('user_id', type=str, location='json', required=True, help='User ID is required')
        self.api_key_service = SetApiKeyService(USER_FOLDER)

    def post(self):
        args = self.parser.parse_args()
        api_key = args['api_key']
        user_id = args['user_id']

        try:
            self.api_key_service.set_api_key(user_id, api_key)
            return {'message': 'API key set successfully'}, 200
        except Exception as e:
            return {'message': str(e)}, 500