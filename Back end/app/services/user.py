import os
import random
import numpy as np

class UserService:
    def __init__(self, user_folder):
        self.user_folder = user_folder

    def register_user(self):
        try:
            while True:
                # Generate a random positive number
                user_id = random.randint(1, 10**9)

                # Create the folder path
                user_path = os.path.join(self.user_folder, str(user_id))

                # Try to create the folder
                try:
                    os.makedirs(user_path, exist_ok=False)  # Raise an error if the folder already exists

                    # Create initial files inside the folder
                    initial_vector_file = os.path.join(user_path, "initial_vector_embedding.npy")
                    result_vector_file = os.path.join(user_path, "result_vector_embedding.npy")
                    mode_file = os.path.join(user_path, "mode.txt")

                    with open(initial_vector_file, 'w') as f:
                        f.write("")  # Create an empty file or add initial content

                    with open(result_vector_file, 'w') as f:
                        f.write("")  # Create an empty file or add initial content

                    with open(mode_file, 'w') as f:
                        f.write("")

                    # Return the user ID if successful
                    return user_id
                except FileExistsError:
                    # If the folder exists, generate a new number and retry
                    continue
        except Exception as e:
            # Log the error (optional) and return -1 in case of failure
            print(f"Error creating user folder: {e}")
            return -1