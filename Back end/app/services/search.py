import json
import math
import os
import string
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
import pytz
import re

class SearchEngine:
    def __init__(self, index_path, stopwords_path):
        # Load the index.json file
        with open(index_path, "r", encoding="utf-8") as f:
            self.index = json.load(f)
            print("Index loaded successfully.")

        # Load Vietnamese stop words from file
        with open(stopwords_path, "r", encoding="utf-8") as f:
            self.english_stop_words = [line.strip() for line in f if line.strip()]

    def compute_tf_idf_in_query(self, term, frequency):
        """Compute the TF-IDF value of a term in the query."""
        if term in self.index:
            idf = self.index[term]["idf"]
            return (1 + math.log(frequency)) * idf
        return 0

    def compute_query_vector(self, word_frequencies):
        """
        Compute and normalize TF-IDF values for all query terms.
        Returns a dictionary of normalized TF-IDF values.
        """
        # First pass: calculate raw TF-IDF values
        query_vector = {}
        vector_magnitude = 0.0

        for word, freq in word_frequencies.items():
            tf_idf = self.compute_tf_idf_in_query(word, freq)
            query_vector[word] = tf_idf
            vector_magnitude += tf_idf * tf_idf

        # Normalize the vector if it's not zero
        if vector_magnitude > 0:
            vector_magnitude = math.sqrt(vector_magnitude)
            for word in query_vector:
                query_vector[word] /= vector_magnitude

        return query_vector 
    
    def get_document_details(self, doc_id):  # ocr_result_onepiece_colored_1
        # if linux then change the path \ to /
        if os.name == 'posix':
            doc_id = doc_id.replace('\\', '/')
        """Retrieve all necessary document details for the UI."""
        print(f"Processing doc_id: {doc_id}")
        # Standardize the doc_id
        json_path = doc_id + ".json"
        json_path = "app\\database\\" + json_path
        file_path = json_path
        print(f"File path: {file_path}")
        if os.path.exists(file_path):
            print(f"Found File path: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                doc_data = json.load(f)
                # Ensure the file contains a list of objects
                if isinstance(doc_data, list):
                    sentences = []
                    for item in doc_data:
                        # Extract the "text" field and replace '\n' with a space
                        text = str(item.get("text", "")).replace("\n", " ").strip()
                        if text:  # Only include non-empty text
                            sentences.append(text)
                    # Join all sentences into a single content
                    content = ". ".join(sentences)
                
                    # Extract all required fields
                    return {
                        'postId': doc_id,
                        'sentences': f"{content}",
                    }
        return None

    def search(self, query, top_k=10):
        """Process the query and return formatted results for the UI."""
        # Remove AND, OR, '|' from the query
        query = query.replace("AND", "").replace("OR", "").replace("|", "")
        
        # Initialize NOT list
        not_list = []
        
        # Process NOT operators first
        not_pattern = r'-("([^"]*)"|\S+)'
        not_matches = re.finditer(not_pattern, query)
        
        # Extract NOT terms and remove them from query
        for match in not_matches:
            term = match.group(1)
            if term.startswith('"') and term.endswith('"'):
                # Handle quoted phrase
                not_list.append(term[1:-1])
            else:
                # Handle single word
                not_list.append(term)
            query = query.replace(match.group(0), '', 1)  # Remove the NOT term from query
        
        print(f"NOT list: {not_list}")  # Debug print
        print(f"Cleaned query: {query}")  # Debug print

        # Find all quoted phrases
        quote_pattern = r'"([^"]*)"'
        phrases = re.findall(quote_pattern, query)
        print(f"Quoted phrases: {phrases}")

        # Remove the quoted phrases from the query for separate processing
        query = re.sub(quote_pattern, '', query)
        print(f"Processed query after removing phrases: {query}")

        # Tokenize and clean the query
        tokens = word_tokenize(query.lower())
        tokens = [word.strip() for word in tokens 
                 if word.strip() not in self.english_stop_words 
                 and word.strip() not in string.punctuation]
        
        # Tokenize each phrase and add to the query tokens
        for phrase in phrases:
            phrase_tokens = word_tokenize(phrase.lower())
            phrase_tokens = [word.strip() for word in phrase_tokens 
                             if word.strip() not in self.english_stop_words 
                             and word.strip() not in string.punctuation]
            tokens.extend(phrase_tokens)
        
        print(f"Processed tokens: {tokens}")

        # Calculate word frequencies
        word_frequencies = {}
        for word in tokens:
            word_frequencies[word] = word_frequencies.get(word, 0) + 1

        # Compute normalized query vector
        normalized_query_vector = self.compute_query_vector(word_frequencies)

        current_docs = {}  # Document scores

        # Calculate scores using pre-computed normalized query vector
        for word, normalized_tf_idf_query in normalized_query_vector.items():
            if word not in self.index:
                continue

            for doc in self.index[word]["documents"]:
                doc_id = doc["id"]
                tf_idf_doc = doc["tf-idf"]
                current_docs[doc_id] = current_docs.get(doc_id, 0) + (normalized_tf_idf_query * tf_idf_doc)

        # For each phrase, get the document_details of each current_doc to determine whether each contain the phrase, if contain add 1 to the score
        for phrase in phrases:
            for doc_id in current_docs.keys():
                doc_details = self.get_document_details(doc_id) # ocr_result_onepiece_colored_1
                if doc_details:
                    contents = doc_details['sentences']
                    postId = doc_details['postId']
                    if phrase in contents or phrase in postId:
                        current_docs[doc_id] += 1

        # Remove documents containing NOT terms
        for term in not_list:
            for doc_id in list(current_docs.keys()):  # Use list() to avoid runtime modification issues
                doc_details = self.get_document_details(doc_id)
                if doc_details:
                    contents = doc_details['sentences']
                    postId = doc_details['postId']
                    if term in contents or term in postId:
                        del current_docs[doc_id]

        # Sort documents by score
        sorted_docs = sorted(current_docs.items(), key=lambda x: x[1], reverse=True)

        # Get top K results with full details
        results = []
        print(f"Top {top_k} results:")
        for doc_id, score in sorted_docs[:top_k]:
            doc_details = self.get_document_details(doc_id)
            # doc_details["score"] = score
            if doc_details:
                results.append(doc_details)
        print(f"Results: {results}")
        return results