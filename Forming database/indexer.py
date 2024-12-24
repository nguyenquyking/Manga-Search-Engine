from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import word_tokenize
import pandas as pd
import string
import os
import json

# Load Vietnamese stop words from file
with open('./english-stopwords.txt', 'r', encoding='utf-8') as f:
    english_stop_words = [line.strip() for line in f if line.strip()]

def fetch_corpus(folder_path):
    # List to store extracted documents
    corpus = []

    # Loop through all JSON files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):  # Process only JSON files
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                
                # Ensure the file contains a list of objects
                if isinstance(data, list):
                    sentences = []
                    for item in data:
                        # Extract the "text" field and replace '\n' with a space
                        text = str(item.get("text", "")).replace("\n", " ").strip()
                        if text:  # Only include non-empty text
                            sentences.append(text)
                    # Join all sentences into a single content
                    content = ". ".join(sentences)
                    # Create identifier for the document by change file_path to appropriate format
                    doc_id = file_path.replace('./','').replace('/','_').replace('.json','')
                    # Combine all fields into a single document
                    document = f"{doc_id}. {content}"
                    # Append the document to the corpus
                    corpus.append(document)
    
    return corpus

def fetch_corpus_big_folder(folder_path):
    # A big corpus of small corpus
    bigcorpus = []
    # There are many subfolders in the folder_path, in each subfolder, there are many subfolders, in each subfolder, there are many json files, loop to get each small subfolder
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            # Get the folder path
            cur_folder_path = os.path.join(root, dir)
            # Get all the subfolders in the folder_path
            for subroot, subdirs, subfiles in os.walk(cur_folder_path):
                for subdir in subdirs:
                    # Get the folder path
                    sub_folder_path = os.path.join(subroot, subdir)
                    # Get the corpus of the small folder
                    print('Fetching corpus from:', sub_folder_path)
                    corpus = fetch_corpus(sub_folder_path)
                    # Get all the values from the corpus to the bigcorpus
                    for i in range(len(corpus)):
                        bigcorpus.append(corpus[i])
    
    return bigcorpus

def store_index(dense_matrix, feature_names, idf_values, corpus, file_path):
    # Create a dictionary to hold the index
    index = {}

    # Loop through the feature names (terms) and the dense matrix
    for term_idx, term in enumerate(feature_names):
        term_dict = {
            "idf": idf_values[term_idx],  # Add the IDF value of the term
            "documents": []  # List to store document-specific data
        }

        # Loop through the documents for the current term
        for doc_idx, tfidf_value in enumerate(dense_matrix[:, term_idx]):
            if tfidf_value > 0:  # Only store non-zero TF-IDF values
                doc_id = corpus[doc_idx].split(".")[0]  # Extract the postId as document ID
                term_dict["documents"].append({"id": doc_id, "tf-idf": tfidf_value})

        # Only add terms with at least one non-zero TF-IDF value
        if term_dict["documents"]:
            index[term] = term_dict

    # Store the index in a JSON file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=4)

# Tokenizer function for English text
def english_tokenizer(text):
    tokens = word_tokenize(text.lower())  # Tokenize and lowercase
    tokens = [word for word in tokens 
              if word not in english_stop_words and word not in string.punctuation]
    return tokens

# Path to the big folder
folder_path = "./ocr_result"
# Fetch the corpus from the folder
corpus = fetch_corpus_big_folder(folder_path)

# Initialize TfidfVectorizer with custom tokenizer
vectorizer = TfidfVectorizer(tokenizer=english_tokenizer, preprocessor=None, sublinear_tf=True)

# Fit and transform the corpus
X = vectorizer.fit_transform(corpus)
# Convert the sparse matrix to a dense array
dense_matrix = X.toarray()
# Get feature names (vocabulary)
feature_names = vectorizer.get_feature_names_out()
# Create a DataFrame for better visualization
df = pd.DataFrame(dense_matrix, columns=feature_names)
# Display the DataFrame
print(df)

# Get the IDF values for each feature name
idf_values = vectorizer.idf_
# Create a DataFrame for the IDF values
df_idf = pd.DataFrame({'Feature': feature_names, 'IDF': idf_values})
print("IDF Values:")
print(df_idf)

# Store the index in a JSON file
store_index(dense_matrix, feature_names, idf_values, corpus, "index.json")