from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from app.services.upload_image_service import ImageService

UPLOAD_FOLDER = 'D:/Manga-Search-Engine images_received'
UPLOAD_IMAGE_ROUTE = '/upload-image'

class UploadImage(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, location='files', required=True, help='Image file is required')
        self.image_service = ImageService(UPLOAD_FOLDER)

    def post(self):
        args = self.parser.parse_args()
        image = args['file']

        if image:
            filepath = self.image_service.save_image(image)
            return {'message': 'Image uploaded successfully', 'image_path': filepath}, 201
        else:
            return {'message': 'No image provided'}, 400
        

# For testing:
# curl -X POST -F "image=@/path/to/your/image.jpg" http://localhost:5000/upload-image