import json
import time
import streamlit as st
import os
import requests
from PIL import Image
from io import BytesIO
import base64

# Backend API endpoint
BACKEND_API_URL = "/search-dialouge"  # Update with your backend URL
# Backend API for getting images
GET_IMAGE_API = "/get-image"

background_img = st.session_state.index["app_background6"]
sidebar_img = st.session_state.index["app_background2"]

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
background-image: url(https://images2.alphacoders.com/740/thumb-1920-740460.png);
background-size: cover;
background-repeat: no-repeat;
}}
[data-testid="stHeader"] {{
background: rgba(0, 0, 0, 0);
}}
[data-testid="stToolbar"] {{
right: 2rem;
}}
# [data-testid="stSidebar"] {{
# background-image: url('data:image/png;base64,{sidebar_img}');
# background-size: center;
# }}
[data-testid="stMainBlockContainer"]{{
border: 15px solid white;
border-radius: 20px;
padding: 5px;
background-color: white;
margin: 20px 0px;
box-shadow": "0 0 10px rgba(0,0,0,0.5)
}}
[data-testid="stSidebarCollapsedControl"] {{
border-radius: 5px;
background-color: white;
}}
[class="stColumn st-emotion-cache-1vsvu9j eiemyj2"] {{
margin: auto;
}}
[class="stColumn st-emotion-cache-1vj2wxa eiemyj2"] {{
padding: 7px;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)
col1, col2 = st.columns([1, 3])
with col1:
    st.image('./assets/app_logo3.png', width=200)
with col2:
    st.title("💬 Dialogue Search")  # Add the title to the second row


st.info("Type a **dialogue** you want to search or pick one of these suggestions:")


# Suggestions for quick search
suggestions = [
    "He's going to punch right through the island!!!",
    "I was just curious about my old house. That's all.",
    "We won't let something like that happen again!",
]

# Layout: Suggestion boxes
cols = st.columns(len(suggestions))  # Creates dynamic columns for each suggestion

# Handle clicks on suggestions
for idx, suggestion in enumerate(suggestions):
    with cols[idx]:
        if st.button(suggestion):
            st.session_state.chosen_suggestion = suggestion

# Search bar
query = st.text_input("Dialogue:", value=st.session_state.get("chosen_suggestion", ""))

# Function to call the backend API
@st.cache_resource
def search_dialogue_api(query, top_k=10):
    try:
        payload = {"text": query, "top_k": top_k}
        response = requests.post(st.session_state.back_end_url + BACKEND_API_URL, json=payload)
        
        if response.status_code == 200:
            return response.json()  # Return the search results as JSON
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to the backend: {e}")
        return []

# Function to fetch an image from the backend
@st.cache_resource
def fetch_image_from_backend(image_path):
    try:
        response = requests.get(f"{st.session_state.back_end_url + GET_IMAGE_API}/{image_path}", stream=True)
        if response.status_code == 200:
            # Load the image from response content
            return Image.open(BytesIO(response.content))
        else:
            st.error(f"Failed to fetch image: {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching image: {e}")
    return None

# Search button logic
if st.button("Search") or st.session_state.get("chosen_suggestion"):
    if query:
        st.session_state.chosen_suggestion = query
        start = time.time()
        # Call the API
        ocr_results = search_dialogue_api(query=query, top_k=int(st.session_state.get("top_k", 10)))
        st.write(f"Search took {time.time() - start} seconds.")

        # Display results
        if ocr_results:
            st.subheader(f"Top {int(st.session_state.get('top_k', 10))} Results")
            columns_per_row = 3
            for row_start in range(0, len(ocr_results), columns_per_row):
                cols = st.columns(columns_per_row)
                for col, ocr_result in zip(cols, ocr_results[row_start:row_start + columns_per_row]):
                    # Extract details
                    manga = ocr_result["manga"]
                    page_type = ocr_result["page_type"]
                    page_number = ocr_result["page_number"]
                    text = ocr_result["text"]

                    # Construct the image path
                    image_path = os.path.join(manga, page_type, f"{page_number}.png").replace("\\", "/")

                    # Fetch the image from the backend
                    image = fetch_image_from_backend(image_path)

                    # Display result
                    with col:
                        if image:
                            st.image(image, caption=f"{manga} - {page_type} - {page_number}")
                        else:
                            st.warning(f"Image not found: {image_path}")
        else:
            st.warning("No results found.")
    else:
        st.warning("Please enter a query to search.")