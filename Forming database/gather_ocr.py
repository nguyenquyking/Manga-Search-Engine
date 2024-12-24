import os
import json

def process_ocr_results(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            input_path = os.path.join(input_folder, filename)

            # Read the JSON file
            with open(input_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Initialize a counter for output files
            i = 0

            # Process each "text" field
            for item in data:
                text = item.get("text", "")
                if isinstance(text, str):
                    # Convert text to lowercase and strip to one line
                    processed_text = text.lower().replace("\n", " ")

                    # Define the output file path
                    output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_{i}.txt")

                    # Write the processed text to the output file
                    with open(output_path, 'w', encoding='utf-8') as output_file:
                        output_file.write(processed_text)

                    # Increment the counter
                    i += 1

# Define the folder paths
input_folder = 'ocr_result/bukonohero/grayscale'
output_folder = 'ocr_text/bukonohero/grayscale'

# Process the OCR results
process_ocr_results(input_folder, output_folder)

print("Processing complete. Check the output folder for the text files.")