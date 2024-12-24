import os
from app.main.settings import Config

class SetApiKeyService:
    def __init__(self, user_folder):
        self.user_folder = user_folder

    def set_api_key(self, user_id, api_key):
        try:
            user_path = os.path.join(self.user_folder, str(user_id))
            api_key_file = os.path.join(user_path, "api_key.txt")

            Config.GEMINI_API_KEY = api_key
            print('API Key:', Config.GEMINI_API_KEY)

            with open(api_key_file, 'w') as f:
                f.write(api_key)

        except Exception as e:
            print(f"Error setting API key: {e}")
            raise e