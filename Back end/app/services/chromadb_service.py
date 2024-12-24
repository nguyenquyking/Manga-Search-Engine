import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
from app.main.settings import Config
from PIL import Image
import numpy as np
import os

class ChromaDBService:
    def __init__(self):
        self.db_path = Config.CHROMA_DB_PATH
        self.embedding_function = OpenCLIPEmbeddingFunction()
        self.data_loader = ImageLoader()
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.visual_collection = self.client.get_or_create_collection(
            name='multimodal_collection',
            embedding_function=self.embedding_function,
            data_loader=self.data_loader,
        )


        self.caption_collection = self.client.get_or_create_collection(
            name='caption_collection',
            embedding_function=self.embedding_function,
            data_loader=self.data_loader,
        )

        self.ocr_collection = self.client.get_or_create_collection(
            name='ocr_collection',
            embedding_function=self.embedding_function,
            data_loader=self.data_loader,
        )

    def store_initial_vector(self, user_id, initial_vector):
        # Determine user folder path
        user_folder_path = os.path.join(self.db_path, 'user', str(user_id))
        initial_vector_file_path = os.path.join(user_folder_path, "initial_vector_embedding.npy")

        if not os.path.exists(user_folder_path):
            raise FileNotFoundError(f"User folder for ID {user_id} does not exist.")

        # Store the query vector directly in a NumPy file
        np.save(initial_vector_file_path, initial_vector)  # Save the embedding directly as a .npy file

    def store_result_vectors(self, user_id, result_vectors):
        # Determine user folder path
        user_folder_path = os.path.join(self.db_path, 'user', str(user_id))
        result_vector_file_path = os.path.join(user_folder_path, "result_vector_embedding.npy")

        if not os.path.exists(user_folder_path):
            raise FileNotFoundError(f"User folder for ID {user_id} does not exist.")

        # Store the result vectors directly in a NumPy file
        np.save(result_vector_file_path, result_vectors)  # Save the result embeddings directly as a .npy file

    def store_mode(self, user_id, mode):
        # Determine user folder path
        user_folder_path = os.path.join(self.db_path, 'user', str(user_id))
        mode_file_path = os.path.join(user_folder_path, "mode.txt")

        if not os.path.exists(user_folder_path):
            raise FileNotFoundError(f"User folder for ID {user_id} does not exist.")
        
        # Store the mode in a text file
        with open(mode_file_path, 'w') as f:
            f.write(mode)  # Write the mode to the file

    def get_result(self, caption, top_k, user_id):
        self.store_mode(user_id, '2')
        try:
            # Generate embedding for the final_caption text
            final_caption_embedding = self.embedding_function([caption])  # Pass as a list
            # print('Final caption embedding first:', final_caption_embedding[0])
            self.store_initial_vector(user_id, final_caption_embedding[0])
        except Exception as e:
            # print(f"Error generating embedding for the text: {e}")
            return {'error': str(e)}
        try:
            # Query visual and caption collections
            results_visual = self.visual_collection.query(query_texts=[caption], n_results=top_k, include=['distances', 'embeddings'])
            results_caption = self.caption_collection.query(query_texts=[caption], n_results=top_k, include=['distances', 'embeddings'])
            # Consolidate results
            consolidated = consolidate_results(results_visual, results_caption, top_k)

            # Extract embeddings from top-k results and store them
            result_vectors = [embedding for _, (_, embedding) in consolidated.items()]
            self.store_result_vectors(user_id, result_vectors)

            return consolidated
        except Exception as e:
            print(f"Error querying collections: {e}")
            return {'error': str(e)}
        
    def get_result_one_image_no_text(self, image_path, image_captions, top_k, user_id):
        # 1 at first line, image_path at second line
        self.store_mode(user_id, '1' + '\n' + image_path)
        try:
            # Generate embedding for the final_caption text
            final_caption_embedding = self.embedding_function([image_captions])  # Pass as a list
            self.store_initial_vector(user_id, final_caption_embedding[0])
        except Exception as e:
            print(f"Error generating embedding for the text: {e}")
            return {'error': str(e)}
        
        # Open and process the image to convert it into an array
        img = Image.open(image_path).convert("RGB")
        img_array = np.array(img)
        
        # print('Image array shape:', img_array.shape)

        try:
            # Pass the image array to the query method
            results_visual = self.visual_collection.query(query_images=[img_array], n_results=top_k, include=['distances', 'embeddings'])
            results_caption = self.caption_collection.query(query_texts=image_captions, n_results=top_k, include=['distances', 'embeddings'])
            # Consolidate results
            consolidated = consolidate_results(results_visual, results_caption, top_k)

            # Extract embeddings from top-k results and store them
            result_vectors = [embedding for _, (_, embedding) in consolidated.items()]
            self.store_result_vectors(user_id, result_vectors)

            return consolidated
        except Exception as e:
            print(f"Error querying collections: {e}")
            return {'error': str(e)}
    
    def refine_result(self, user_id, selections, top_k):
        # Retrieve the stored result vectors for the user
        result_vector_file_path = os.path.join(self.db_path, 'user', str(user_id), "result_vector_embedding.npy")
        result_vectors = np.load(result_vector_file_path)
        # print('Result vector first:', result_vectors[0])

        # Retrieve the stored initial vector for the user
        initial_vector_file_path = os.path.join(self.db_path, 'user', str(user_id), "initial_vector_embedding.npy")
        initial_vector = np.load(initial_vector_file_path)
        final_caption_embedding = initial_vector
        # print('Final caption embedding:', final_caption_embedding)

        # Ensure the embedding is a plain list of floats
        if isinstance(final_caption_embedding, list) and isinstance(final_caption_embedding[0], np.ndarray):
            final_caption_embedding = final_caption_embedding[0].tolist()  # Flatten
            print('yes case 1')
        elif isinstance(final_caption_embedding, np.ndarray):
            final_caption_embedding = final_caption_embedding.tolist()
            print('yes case 2')

        # Convert to numpy array for further calculations
        initial_vector = np.array(final_caption_embedding)
        # print('Initial vector:', initial_vector)
        # Collect positive (unticked) and negative (ticked) vectors
        positive_vectors = []
        negative_vectors = []  # Collect all negative vectors

        for i, selection in enumerate(selections):
            if not selection:
                positive_vectors.append(np.array(result_vectors[i]))
            else:
                negative_vectors.append(np.array(result_vectors[i]))
        
        # Calculate the refined query vector using the interactive search function
        new_query_vector = vector_for_interactive_search(
            initial_query=initial_vector,
            positive_vectors=positive_vectors,
            negative_vectors=negative_vectors
        )
        # print('New query vector:', new_query_vector)
        # Store the new query vector
        self.store_initial_vector(user_id, new_query_vector)

        results_visual = None
        results_caption = None

        # Load the mode
        mode_file_path = os.path.join(self.db_path, 'user', str(user_id), "mode.txt")
        with open(mode_file_path, 'r') as f:
            mode = f.read().strip()
        if mode.split('\n')[0] == '1':
            # Load the image_path from the mode file
            image_path = mode.split('\n')[1]
            # Open and process the image to convert it into an array
            img = Image.open(image_path).convert("RGB")
            img_array = np.array(img)
            # Query both databases
            results_visual = self.visual_collection.query(query_images=[img_array], n_results=top_k, include=['distances', 'embeddings'])
            results_caption = self.caption_collection.query(query_embeddings=[new_query_vector.tolist()], n_results=top_k, include=['distances', 'embeddings'])
        elif mode == '2':
            # Query both databases with the refined query vector
            results_visual = self.visual_collection.query(query_embeddings=[new_query_vector.tolist()], n_results=top_k, include=['distances', 'embeddings'])
            results_caption = self.caption_collection.query(query_embeddings=[new_query_vector.tolist()], n_results=top_k, include=['distances', 'embeddings'])

        # Consolidate results from both queries
        consolidated_results = consolidate_results(results_visual, results_caption, top_k)
        # Store the consolidated results in the database
        result_vectors = [embedding for _, (_, embedding) in consolidated_results.items()]
        self.store_result_vectors(user_id, result_vectors)

        return consolidated_results

def consolidate_results(results1, results2, top_k):
    """Consolidates results from two collections based on summed distances and includes embeddings."""
    combined_results = {}

    # Add results from the first collection
    for ids, distances, embeddings in zip(results1['ids'][0], results1['distances'][0], results1['embeddings'][0]):
        combined_results[ids] = [distances, embeddings]

    # Add results from the second collection, summing distances if the ID already exists
    for ids, distances, embeddings in zip(results2['ids'][0], results2['distances'][0], results2['embeddings'][0]):
        if ids in combined_results:
            combined_results[ids][0] += distances  # Sum distances
        else:
            combined_results[ids] = [distances, embeddings]

    # Sort results by summed distances
    sorted_results = sorted(combined_results.items(), key=lambda x: x[1][0])

    # Return the top 10 results as a dictionary
    return {k: v for k, v in sorted_results[:top_k]}

# Define the interactive_search function
def vector_for_interactive_search(initial_query, positive_vectors, negative_vectors):
    # Positive contribution
    if positive_vectors:
        positive_sum = np.sum(positive_vectors, axis=0)
        positive_component = 0.75 * (positive_sum / len(positive_vectors))
    else:
        positive_component = 0

    # Negative contribution
    if negative_vectors:
        negative_sum = np.sum(negative_vectors, axis=0)
        negative_component = 0.25 * (negative_sum / len(negative_vectors))
    else:
        negative_component = 0

    # Calculate the new query vector
    new_query = initial_query + positive_component - negative_component
    return new_query