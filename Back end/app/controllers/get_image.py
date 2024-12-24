from flask_restful import Resource
from flask import send_from_directory, send_file
from app.services.upload_image_service import ImageService
import os
from werkzeug.utils import safe_join
from app.main.settings import Config

DATASET_FOLDER = os.path.abspath(os.path.join(Config.CHROMA_DB_PATH, 'dataset'))
GET_IMAGE_ROUTE = '/get-image/<path:filename>'

class GetImage(Resource):
    def __init__(self):
        self.image_service = ImageService(DATASET_FOLDER)

    def get(self, filename):
        if self.image_service.image_exists(filename):
            # print(f'Image found: {filename}')
            path = safe_join(os.fspath(DATASET_FOLDER), os.fspath(filename))
            # print(f'Path: {path}')
            return send_from_directory(DATASET_FOLDER, filename)
        else:
            return {'message': 'Image not found'}, 404
        
# For testing:
# curl http://localhost:5000/get-image/your-image.jpg --output your-image.jpg