from dotenv import load_dotenv
import os
import json
import comiq
import time

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('GEMINI_API_KEY')

# Set up your Gemini API key
comiq.set_api_key(api_key)

# Define input and output folder paths
input_folder = "./dataset/onepiece/colored"
output_folder = "./ocr_result/onepiece/colored"

start_index = 426
end_index = 1461

# Iterate through the range of image numbers
for i in range(start_index, end_index):  # Assuming 0 to 1460 inclusive
    # Construct the filename
    file_name = f"{i}.png"
    image_path = os.path.join(input_folder, file_name)
    json_file_path = os.path.join(output_folder, f"{i}.json")
    if os.path.exists(json_file_path):
        print(f'File {json_file_path} already exists. Skipping.')
        continue
    
    # Check if the file exists before processing
    if os.path.isfile(image_path):
        # Process the image with comiq.extract
        try:
            data = comiq.extract(image_path)
            # Define the output JSON file path
            
            # Write the OCR data to the JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)
            
            print(f"OCR data for {file_name} saved to {json_file_path}")
        except json.JSONDecodeError as e:
            print(f"JSON decoding failed for {file_name}: {e}")
            continue
        except Exception as e:
            print(f"An unexpected error occurred for {file_name}: {e}")
            continue
        finally:
            # Wait for 0.5 seconds before continuing to avoid rate limiting
            print(f'Waiting for 0.5 seconds...')
            time.sleep(0.5)
            print(f'Continuing...')
    else:
        print(f"File {file_name} does not exist. Skipping.")
