from flask_restful import Resource
from app.services.user import UserService
import os
from app.main.settings import Config

USER_FOLDER = os.path.abspath(os.path.join(Config.CHROMA_DB_PATH, 'user'))
USER_ROUTE = '/register-user'

class User(Resource):
    def __init__(self):
        self.user_service = UserService(USER_FOLDER)

    def post(self):
        try:
            # Call the user_service's register_user function
            user_id = self.user_service.register_user()
            return {'message': 'User registered successfully', 'user_id': user_id}, 201
        except Exception as e:
            return {'message': f'Error registering user: {str(e)}'}, 500