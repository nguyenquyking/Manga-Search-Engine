from PIL import Image
import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
import numpy as np
from tqdm import tqdm
import os

db_path="database" #add your db path here
# Initialize Chroma DB client, embedding function, and data loader

client = chromadb.PersistentClient(path=db_path)
embedding_function = OpenCLIPEmbeddingFunction()
data_loader = ImageLoader()

collection = client.get_or_create_collection(
    name='multimodal_collection',
    embedding_function=embedding_function,
    data_loader=data_loader
)

def add_images_to_collection(folder_path):
    image_files = [os.path.join(folder_path, image_name) for image_name in os.listdir(folder_path)
                   if os.path.isfile(os.path.join(folder_path, image_name))]

    for image_path in tqdm(image_files, desc="Creating Image Embeddings and Adding to DB"):
        try:
            image = np.array(Image.open(image_path))
            
            # Replace slashes with underscores and create a unique ID
            formatted_id = image_path.replace("./", "").replace("/", "_").replace("\\", "_")
            
            collection.add(
                ids=[formatted_id],
                images=[image]
            )
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

# image_folder_path = "./dataset/onepiece/colored"
# image_folder_path = "./dataset/onepiece/grayscale"  # Specify your folder path here
# image_folder_path = "./dataset/blackclover/colored"
# image_folder_path = "./dataset/blackclover/grayscale"
# image_folder_path = "./dataset/bukonohero/colored"
image_folder_path = "./dataset/bukonohero/grayscale"

add_images_to_collection(image_folder_path)