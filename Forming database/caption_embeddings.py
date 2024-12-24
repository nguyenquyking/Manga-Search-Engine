import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
import os
from tqdm import tqdm

# Initialize the database path and new collection name
db_path = "database"  # Same database path as before
client = chromadb.PersistentClient(path=db_path)

# Initialize the embedding function for captions using OpenCLIP
caption_embedding_function = OpenCLIPEmbeddingFunction()

# Create or get a new collection for captions
caption_collection = client.get_or_create_collection(
    name='caption_collection',
    embedding_function=caption_embedding_function
)

def add_captions_to_collection(caption_folder_path):
    """
    Add captions from a folder to the ChromaDB caption collection.

    Args:
        caption_folder_path (str): Path to the folder containing caption files.
    """
    # Get all caption files in the folder
    caption_files = [os.path.join(caption_folder_path, f) for f in os.listdir(caption_folder_path) 
                     if os.path.isfile(os.path.join(caption_folder_path, f))]

    for caption_file in tqdm(caption_files, desc="Embedding Captions and Adding to DB"):
        try:
            # Read the caption text from the file
            with open(caption_file, 'r', encoding='utf-8') as file:
                caption = file.read().strip()

            # Create a unique ID for the caption based on the file name
            formatted_id = caption_file.replace("./", "").replace("/", "_").replace("\\", "_")

            # Add the caption to the database collection
            caption_collection.add(
                ids=[formatted_id],
                documents=[caption]
            )
        except Exception as e:
            print(f"Error processing caption file {caption_file}: {e}")

# Path to the folder containing caption files
# caption_folder_path = "./caption/onepiece/colored"
# caption_folder_path = "./caption/onepiece/grayscale"
# caption_folder_path = "./caption/blackclover/colored"
caption_folder_path = "./caption/blackclover/grayscale"
# caption_folder_path = "./caption/bukonohero/colored"
# caption_folder_path = "./caption/bukonohero/grayscale"

# Add the captions to the caption collection
add_captions_to_collection(caption_folder_path)