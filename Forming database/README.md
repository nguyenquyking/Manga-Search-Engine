# Manga-Retrieval-Database

# Using embedding.py
1. Download necessary packages
2. Put folder dataset in the same directory as the script
3. Change the image_folder_path = "./dataset/blackclover/colored" to the folder path containing images needing embedded
4. Run embeddings.py
5. Run app.py for testing

# Using captioning.py
1. Download necessary packages(google, google.generativeai)
2. Set the API Key 
3. Change One Piece -> name of Comic
system_content = """You are an expert in analyzing images from One Piece Manga Comics. Your task is to provide clear and concise descriptions of the characters, actions, and scenes depicted in the images. Focus on identifying key visual elements, character names, and interactions. Ensure the descriptions are accurate, descriptive, and unambiguous to serve as meaningful representations for embedding into vectors.
"""
4. Change the input_folder to folder containing comic images needed creating caption
5. Change the output_folder to corresponding output folder
6. Run captioning.py