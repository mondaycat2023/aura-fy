import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit.components.v1 as components
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv

load_dotenv() # This loads the .env file

# Now we read from the environment variables, not hardcoded strings
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REDIRECT_URI = "http://127.0.0.1:8501"

# --- 2. THE UI STYLING ---
def set_vibe_style(hex_color):
    st.markdown(f"""
        <style>
        /* 1. Main Background */
        .stApp {{
            background: linear-gradient(135deg, {hex_color} 0%, #1a1a1a 100%);
            transition: background 1s ease-in-out;
            color: white;
        }}
        
        /* 2. Title Text */
        h1 {{
            color: white !important;
            text-shadow: 0px 4px 12px rgba(0,0,0,0.5);
        }}
        
        /* 3. Input Box Styling (The Fix!) */
        .stTextInput input {{
            color: #000000 !important;        /* Text is always Black */
            background-color: #ffffff !important; /* Box is always White */
            border-radius: 10px;
        }}
        
        /* 4. Input Label (The text "Enter your vibe") */
        .stTextInput label {{
            color: white !important;
            font-weight: bold;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. THE APP UI ---
st.title("🍌 Aura-fy Your Vibe")
st.markdown("### *AI-Powered Mood & Music Visualizer*")

# Initialize session state for the input box if it doesn't exist
if 'mood_input' not in st.session_state:
    st.session_state.mood_input = ""

# A helper function to clear the input
def clear_text():
    st.session_state.mood_input = ""

# We use columns to put the inputs and buttons side-by-side
col1, col2 = st.columns([3, 1])

with col1:
    # Notice we bind the value to session_state.mood_input
    mood = st.text_input("Enter your vibe:", key="mood_input")

with col2:
    # Add some spacing so the buttons align
    st.write("") 
    st.write("") 
    # The buttons
    if st.button("🔄 Reset", on_click=clear_text):
        pass # The on_click function handles the clearing

# We only run logic if there is text in the mood box
if mood:
    
    # --- A. AI COLOR GENERATION ---
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        prompt = f"You are a color theorist. What hex color code represents the mood: '{mood}'? Reply with ONLY the hex code (e.g., #ff0000). Do not write any other text."
        
        response = model.generate_content(prompt)
        color_text = response.text.strip()
        
        match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}', color_text)
        if match:
            color = match.group(0)
        else:
            color = "#555555"
            
    except Exception as e:
        color = "#333333"

    set_vibe_style(color)
    # (Removed the st.success bar here per your request)

    # --- B. SPOTIFY CONNECTION ---
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="user-library-read"
        ))
        
        results = sp.search(q=mood, limit=10, type='track')
        
        if len(results['tracks']['items']) > 0:
            st.subheader(f"🎧 Soundtrack for: {mood}")
            
            track_options = {}
            for track in results['tracks']['items']:
                label = f"{track['name']} - {track['artists'][0]['name']}"
                track_options[label] = track['id']
            
            selected_label = st.radio(
                "Select a track to play:", 
                options=list(track_options.keys())
            )
            
            if selected_label:
                selected_track_id = track_options[selected_label]
                st.markdown("---")
                embed_url = f"https://open.spotify.com/embed/track/{selected_track_id}"
                components.iframe(embed_url, height=80)
                
        else:
            st.warning(f"Couldn't find songs for '{mood}'. Try adding a genre name!")

    except Exception as e:
        st.error(f"Spotify Error: {e}")