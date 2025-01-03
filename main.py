import json
import streamlit as st
import requests  # Import requests for API calls

BACK_END_URL = " https://badger-prepared-iguana.ngrok-free.app"
REGISTER_USER_API_URL = "/register-user"
SET_API_KEY_API_URL = "/set-api-key"
DELETE_USER_DATA_API_URL = "/delete-user"

st.set_page_config(page_title="Manga Retrieval", page_icon=":material/edit:")

if "back_end_url" not in st.session_state:
    st.session_state.back_end_url = BACK_END_URL

# Call backend API to register user and store the ID
if "session_state_id_turn" not in st.session_state:
    try:
        response = requests.post(st.session_state.back_end_url + REGISTER_USER_API_URL)
        if response.status_code == 201:
            st.session_state.session_state_id_turn = response.json().get("user_id")
        else:
            st.error(f"Error registering user: {response.json().get('message')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the server: {e}")

@st.cache_resource
def get_img():
    print("Loading images...")
    with open('./assets/img_map.json', 'r') as f:
        index = json.load(f)
    return index

index = get_img()

st.session_state.index = index

sidebar_pg = f"""
<style>
[data-testid="stSidebarNav"] {{
border-radius: 20px;
padding: 10px 0px;
background-color: white;
margin: 10px;
}}
[data-testid="stSidebarNavSeparator"] {{
padding: 0px;
margin: 0px 10px;
}}
[data-testid="stSidebarUserContent"] {{
border-radius: 20px;
padding: 10px;
background-color: white;
margin: 5px;
}}
[data-testid="stSidebarCollapseButton"] {{
border-radius: 5px;
background-color: white;
}}
</style>
"""
st.markdown(sidebar_pg, unsafe_allow_html=True)
# Sidebar input for API key
st.sidebar.title("Gemini API 🔑")

# Initialize session state for the button visibility
if "send_button_visible" not in st.session_state:
    st.session_state.send_button_visible = False

# Initialize session state for storing the old API key
if "previous_api_key" not in st.session_state:
    st.session_state.previous_api_key = ""

# Text input for API key
api_key = st.sidebar.text_input(
    "Enter Key",
    value='',
    type="password",
    help="You can enter your Gemini API key here"
)

# Determine button visibility based on whether the new API key is different from the old one
st.session_state.send_button_visible = api_key.strip() != st.session_state.previous_api_key.strip()

# Render the "Send" button if input is provided
if st.session_state.send_button_visible:
    button_clicked = st.sidebar.button("Send")

    # Logic when button is clicked
    if button_clicked:
        try:
            # Call backend API to store the API key
            payload = {
                "api_key": api_key,
                "user_id": st.session_state.session_state_id_turn
            }
            response = requests.post(st.session_state.back_end_url + SET_API_KEY_API_URL, json=payload)
            
            if response.status_code == 200:
                st.sidebar.success("API key sent successfully!")
                st.session_state.previous_api_key = api_key
            else:
                st.sidebar.error(f"Error setting API key: {response.json().get('message')}")
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Error connecting to the server: {e}")

        st.session_state.send_button_visible = False  # Hide button after click

# Sidebar with horizontal layout
with st.sidebar:
    # Create two columns
    col1, col2 = st.columns([1, 2])  # Adjust width ratios as needed

    # First column with two rows
    with col1:
        st.text("")  # First row: Empty or placeholder
        st.text("")  
        st.text("Top Results")  # Second row: Add label

    # Second column with one row
    with col2:
        st.session_state.top_k = st.text_input(" ", value="10")  # Store in session_state

scene_search = st.Page("multimodal_search.py", title="Scene Search", icon="🔍")
dialogue_search = st.Page("dialogue_search.py", title="Dialogue Search", icon="💬")

# JavaScript to detect tab closure and send `user_id` to the backend
js_code = f"""
<script>
    window.addEventListener("beforeunload", function (event) {{
        const data = {{
            user_id: {st.session_state.session_state_id_turn}
        }};
        
        fetch("{st.session_state.back_end_url}{DELETE_USER_DATA_API_URL}", {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify(data),
            // Using keepalive to ensure the request completes even if the page is unloading
            keepalive: true
        }}).catch(error => console.error('Error:', error));
    }});
</script>
"""

# # Embed the JavaScript in the Streamlit app
# st.components.v1.html(js_code)

pg = st.navigation([scene_search, dialogue_search])
pg.run()