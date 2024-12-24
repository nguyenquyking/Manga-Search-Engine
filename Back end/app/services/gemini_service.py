from app.main.settings import Config
import google.generativeai as genai
from PIL import Image
import numpy as np
import time

class GeminiPrompt:
    class SystemContent:
        image_caption = """
        You are an assistant specializing in analyzing images. Your task is to generate a concise caption for the given image. Focus on identifying key subjects (e.g., names of characters, objects), their appearance, and their context. Avoid unnecessary details that do not contribute to understanding the main subject or action.
        """
        combine_search_phrases = """
        You are an assistant specializing in combining search phrases. Your task is to interpret multiple related phrases, focusing on identifying key subjects(e.g., names of characters, objects), relationships, and actions. The combined query must be concise, relevant, and meaningful for searching databases.
        """

        combine_image_captions = """
        You are an assistant specializing in combining image captions. Your task is to consolidate multiple related captions into a single, coherent caption. Focus on identifying the common themes, key characters, names of characters, their actions, and their relationships. The final caption should be concise, descriptive, and suitable for searching databases.
        """

        combine_text_image_caption = """
        You are an assistant specializing in combining textual descriptions and image analyses. Your task is to take a textual query and an image caption, identify the key characters, names of characters and their relationships, and generate a single, meaningful caption. Focus on interpreting the intent of the text query and linking it with the image subject to create a relevant and concise description for searching databases.
        """

    class UserContent:
        # image_caption = "Generate a concise caption for the following image, focusing on key subjects, name of characters, their appearance, and the context."
        @classmethod
        def image_caption(cls, img):
            return [
                "Generate a concise caption for the following image, focusing on key subjects, name of characters, their appearance, and the context.",
                img
            ]
        @classmethod
        def combine_search_phrases(cls, text_inputs):
            return f"""
            Combine the following search phrases into a single, meaningful query that clearly conveys the names of characters, relationships and actions described:
            {' '.join(text_inputs)}
            """
        @classmethod
        def combine_image_captions(cls, image_captions):
            return f"""
            Combine the following captions into a single, meaningful caption, focusing on common themes, key characters, names of characters, their actions, and relationships:
            {'. '.join(image_captions)}
            """
        @classmethod
        def combine_text_image_caption(cls, text_caption, image_caption):
            return f"""
                Combine the following textual query and image caption into a single, meaningful caption. Focus on identifying key characters, names of characters, their actions, and relationships:
                Text Query: {text_caption}
                Image Caption: {image_caption}
                """
        
class ClientFactory:
    def __init__(self):
        self.clients = {}
    def register_client(self, name, client_class):
        self.clients[name] = client_class

    def create_client(self, name, **kwargs):
        client_class = self.clients.get(name)
        if not client_class:
            raise ValueError(f"Client not found: {name}")
        return client_class(**kwargs)

class GeminiService:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL_NAME
        self.temperature = 0.7
        if not self.api_key:
            raise ValueError('GEMINI_API_KEY not set in environment variables')
        genai.configure(api_key=self.api_key) 
        self.client_factory = ClientFactory()
        self.client_factory.register_client('google', genai.GenerativeModel)

    def client_kwargs(self, system_instruction):
        return {
            'model_name': self.model_name,
            'generation_config': {
                'temperature': self.temperature
            },
            'system_instruction': system_instruction
        }

    def generate_caption(self, image_path):
        img = Image.open(image_path).convert('RGB')

        client_kwargs = self.client_kwargs(GeminiPrompt.SystemContent.image_caption)
        client = self.client_factory.create_client('google', **client_kwargs)

        user_instruction = GeminiPrompt.UserContent.image_caption(img)
        response = client.generate_content(user_instruction, stream=True)
        response.resolve()
        time.sleep(0.5)
        return response.text.strip()

    def combine_text_inputs(self, text_inputs):
        client_kwargs = self.client_kwargs(GeminiPrompt.SystemContent.combine_search_phrases)
        client = self.client_factory.create_client('google', **client_kwargs)

        user_instruction = GeminiPrompt.UserContent.combine_search_phrases(text_inputs)
        response = client.generate_content(user_instruction, stream=True)
        response.resolve()
        time.sleep(0.5)
        return response.text.strip()

    def combine_image_captions(self, image_captions):
        client_kwargs = self.client_kwargs(GeminiPrompt.SystemContent.combine_image_captions)
        client = self.client_factory.create_client('google', **client_kwargs)

        user_instruction = GeminiPrompt.UserContent.combine_image_captions(image_captions)
        response = client.generate_content(user_instruction, stream=True)
        response.resolve()
        time.sleep(0.5)
        return response.text.strip()

    def combine_text_image_caption(self, text_caption, image_caption):
        client_kwargs = self.client_kwargs(GeminiPrompt.SystemContent.combine_text_image_caption)
        client = self.client_factory.create_client('google', **client_kwargs)

        user_instruction = GeminiPrompt.UserContent.combine_text_image_caption(text_caption, image_caption)
        response = client.generate_content(user_instruction, stream=True)
        response.resolve()
        time.sleep(0.5)
        return response.text.strip()