import time
import streamlit as st
from PIL import Image
import requests
import io
from io import BytesIO

# Backend API endpoint
BACKEND_API_URL = "http://127.0.0.1:5000/upload-image"  # Update with your backend URL
SEARCH_SCENE_API_URL = "http://127.0.0.1:5000/search-scene"
GET_IMAGE_API_URL = "http://127.0.0.1:5000/get-image"
REFINE_RESULT_API_URL = "http://127.0.0.1:5000/refine-result"

col1, col2 = st.columns([1, 3]) 
with col1:
    st.image('./assets/app_logo.png', width=200)
with col2:
    st.title("Multimodal Scene Search")
    
st.info("Type **descriptions** or upload **images** you want to search 💖")
with open('./style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)\
    
if "text_inputs" not in st.session_state:
    st.session_state.text_inputs = [""]

def add_description():
    st.session_state.text_inputs.append("")

def delete_description(index):
    if 0 <= index < len(st.session_state.text_inputs):
        st.session_state.text_inputs.pop(index)

# Render all text input fields dynamically with delete buttons
for i, text_input in enumerate(st.session_state.text_inputs):
    cols = st.columns([10, 1])  # Create two columns for text field and delete button
    with cols[0]:
        st.session_state.text_inputs[i] = st.text_input(
            label=f"Description {i+1}",
            key=f"description_{i+1}"
        )
    with cols[1]:
        # Use a button for deleting, uniquely keyed
        if st.button("🗑️", key=f"delete_{i}", on_click=delete_description, args=(i,)):
            pass

st.button("Add description", on_click=add_description)

# Image uploader
image_files = st.file_uploader(
    label="Images:",
    type=["jpg", "png", "jpeg"],
    accept_multiple_files=True)

uploaded_paths = []

# Function to upload image to the backend API
def upload_image_to_backend(image_file):
    try:
        # Convert Streamlit UploadedFile to file-like object
        file_buffer = io.BytesIO(image_file.read())
        file_buffer.name = image_file.name  # Set the name for the file
        files = {"file": (image_file.name, file_buffer, image_file.type)}
        
        # Call the API
        response = requests.post(BACKEND_API_URL, files=files)
        
        # Check for success
        if response.status_code == 201:
            # st.success(f"Image '{image_file.name}' uploaded successfully!")
            return response.json()  # Return the backend's response (e.g., saved file path)
        else:
            st.error(f"Failed to upload '{image_file.name}': {response.text}")
    except Exception as e:
        st.error(f"Error uploading image '{image_file.name}': {e}")
    return None

# Process uploaded images
if image_files:
    for image_file in image_files:
        response = upload_image_to_backend(image_file)
        if response:
            uploaded_paths.append(response.get("image_path"))  # Collect the saved paths if provided

# Session State Initialization
if "results" not in st.session_state:
    st.session_state.results = []

if "selected_images" not in st.session_state:
    st.session_state.selected_images = []

if "query_vector" not in st.session_state:
    st.session_state.query_vector = None

# Function to call the search-scene API
@st.cache_resource
def call_search_scene_api(image_paths, text_inputs, top_k):
    payload = {
        "user_id": st.session_state.get("session_state_id_turn", 0),
        "image_path": image_paths,
        "text": text_inputs,
        "top_k": top_k
    }
    try:
        response = requests.post(SEARCH_SCENE_API_URL, json=payload)
        if response.status_code == 200:
            return response.json()["results"]
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Failed to call API: {e}")
    return []

def call_refine_result_api(user_id, selections, top_k):
    payload = {
        "user_id": user_id,
        "selections": selections,
        "top_k": top_k
    }
    try:
        response = requests.post(REFINE_RESULT_API_URL, json=payload)
        if response.status_code == 200:
            return response.json()["results"]
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Failed to call API: {e}")
    return []

# Function to fetch an image from the backend
@st.cache_resource
def fetch_image_from_backend(image_path):
    try:
        response = requests.get(f"{GET_IMAGE_API_URL}/{image_path}", stream=True)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            st.error(f"Failed to fetch image: {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching image: {e}")
    return None

if st.button("Search"):
    results = {}

    if len(image_files) == 0 and not any(st.session_state.text_inputs):
        st.warning("Please upload an image or provide a description.")
        st.stop()

    start = time.time()
    results = call_search_scene_api(image_paths=uploaded_paths, text_inputs=st.session_state.text_inputs, top_k=10)
    st.write(f"Search took {time.time() - start} seconds.")
    
    if results:
        # Store results in session state
        st.session_state.results = results
        st.session_state.selected_images = [False] * len(results)

# Display results
if "results" in st.session_state and st.session_state.results:
    col_subheader, col_button = st.columns([3, 1])
    with col_subheader:
        st.subheader("Search Results")
    with col_button:
        refine_disabled = not any(st.session_state.get("selected_images", []))
        if st.button("Refine Results", disabled=refine_disabled):
            print('images selected:', st.session_state.selected_images)
            st.session_state.results = call_refine_result_api(st.session_state.get("session_state_id_turn", 0), st.session_state.get("selected_images", []), 10)
            st.session_state.selected_images = [False] * len(st.session_state.results)

    columns_per_row = 3

    for row_start in range(0, len(st.session_state.results), columns_per_row):
        cols = st.columns(columns_per_row)
        for col, result, idx in zip(cols, st.session_state.results[row_start:row_start + columns_per_row], range(row_start, row_start + columns_per_row)):
            image_path = f"{result['manga']}/{result['page_type']}/{result['page_number']}.png"
            image = fetch_image_from_backend(image_path)

            with col:
                if image:
                    st.session_state.selected_images[idx] = st.checkbox("Select", key=f"checkbox_{idx}", value=st.session_state.selected_images[idx])
                    st.image(image, caption=f"{result['manga']} - {result['page_type']} - {result['page_number']}")