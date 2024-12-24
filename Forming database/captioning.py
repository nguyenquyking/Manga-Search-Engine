from dotenv import load_dotenv
import os
import warnings
import google.generativeai as genai
from PIL import Image
import time

# Load environment variables from .env file
load_dotenv(override=True)

# System content for the generative model
system_content = """
You are an expert in analyzing images from My hero Academia Manga Comics. Your task is to provide clear and concise descriptions of the characters, actions, and scenes depicted in the images. Focus on identifying key visual elements, character names, and interactions. Ensure the descriptions are accurate, descriptive, and unambiguous to serve as meaningful representations for embedding into vectors.
"""

# Set the API key and Gemini model name directly in the code
api_key = os.getenv('GEMINI_API_KEY')  # Replace with your actual API key
model_name = "gemini-1.5-flash"

# Ensure the API key is set
if not api_key:
    raise ValueError("API_KEY must be set.")

# Configure the generative AI client
genai.configure(api_key=api_key)

# ClientFactory class to manage API clients
class ClientFactory:
    def __init__(self):
        self.clients = {}
    
    def register_client(self, name, client_class):
        self.clients[name] = client_class
    
    def create_client(self, name, **kwargs):
        client_class = self.clients.get(name)
        if client_class:
            return client_class(**kwargs)
        raise ValueError(f"Client '{name}' is not registered.")

# Register and create the Google generative AI client
client_factory = ClientFactory()
client_factory.register_client('google', genai.GenerativeModel)

client_kwargs = {
    "model_name": model_name,
    "generation_config": {
        "temperature": 0.8,
    },
    "system_instruction": system_content,
}

client = client_factory.create_client('google', **client_kwargs)

# User content for image description
user_content = """
Analyze this comic image and provide a detailed caption. Identify the names of the characters, their actions, interactions, and any notable visual elements within the scene. Keep the description concise and relevant for search applications.
"""

# Paths for input and output folders
input_folder = './dataset/blackclover/grayscale/'
output_folder = './caption/blackclover/grayscale/'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Process all images in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(input_folder, filename)
        base_name = os.path.splitext(filename)[0]
        caption_path = os.path.join(output_folder, f"{base_name}.txt")
        if os.path.exists(caption_path):
            print(f"Caption already exists for {filename}")
            continue
        try:
            # Open the image
            image = Image.open(image_path)
            
            # Generate image description
            print(f"Processing: {filename}")
            response = client.generate_content([user_content, image], stream=True)
            response.resolve()
            
            # Save caption to a text file in one line
            try:
                caption_text = " ".join(response.text.splitlines()).strip()  # Combine lines into one
                with open(caption_path, 'w') as caption_file:
                    caption_file.write(caption_text)
                print(f"Caption saved for {filename}")
            except Exception as e:
                print(f"Error saving caption for {filename}: {e}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
        finally:
            print(f'Waiting for 0.5 seconds...')
            time.sleep(0.5)
            print(f'Continuing...')

print("Caption generation completed.")