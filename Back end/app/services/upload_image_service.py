import os
from werkzeug.utils import secure_filename


class ImageService:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder

    def save_image(self, image):
        filename = image.filename
        filename = secure_filename(filename)
        filepath = os.path.join(self.upload_folder, filename)
        image.save(filepath)
        return filepath
    
    def image_exists(self, filename):
        filepath = os.path.join(self.upload_folder, filename)
        return os.path.exists(filepath)