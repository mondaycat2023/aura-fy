import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials # <-- CHANGED THIS
import streamlit.components.v1 as components
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv

load_dotenv() # This loads the .env file
# Function to get keys from either .env (Local) or Streamlit Cloud (Deploy)
def get_key(name):
    # Try getting from os (local)
    key = os.getenv(name)
    # If not found, try getting from Streamlit secrets (cloud)
    if not key and name in st.secrets:
        key = st.secrets[name]
    return key
# Now we read from the environment variables, not hardcoded strings
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REDIRECT_URI = "https://aura-fy.streamlit.app/" 
if "streamlit.app" in st.secrets.get("REDIRECT_URL", ""):
    REDIRECT_URI = st.secrets["REDIRECT_URL"]
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
   # --- B. SPOTIFY CONNECTION ---
    try:
        # Use ClientCredentials (no login required, faster)
        auth_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # --- NEW LOGIC: SEARCH FOR PLAYLISTS FIRST ---
        search_results = sp.search(q=mood, limit=1, type='playlist')
        
        final_tracks = []
        
        # 1. Did we find a playlist?
        if search_results and search_results.get('playlists') and search_results['playlists']['items']:
            playlist_id = search_results['playlists']['items'][0]['id']
            
            # Get the actual songs from inside that playlist
            playlist_data = sp.playlist_tracks(playlist_id, limit=10)
            
            # CRITICAL CHECK: Ensure playlist_data exists before reading it
            if playlist_data and 'items' in playlist_data:
                for item in playlist_data['items']:
                    # Some playlist items are None or have no track info (e.g. local files)
                    if item and item.get('track'):
                        final_tracks.append(item['track'])
                    
        # 2. Fallback: If no playlist (or empty playlist), search for tracks directly
        if not final_tracks:
            track_results = sp.search(q=mood, limit=10, type='track')
            if track_results and track_results.get('tracks'):
                final_tracks = track_results['tracks']['items']

        # --- DISPLAY THE RESULTS ---
        if final_tracks:
            st.subheader(f"🎧 Soundtrack for: {mood}")
            
            track_options = {}
            for track in final_tracks:
                # Double check that track has artists to avoid crashes
                if track and track.get('artists'):
                    # Create a label: "Song Name - Artist"
                    artist_name = track['artists'][0]['name']
                    label = f"{track['name']} - {artist_name}"
                    track_options[label] = track['id']
            
            if track_options:
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
                st.warning("Found songs, but they had missing data. Try a different vibe!")
                
        else:
            st.warning(f"Couldn't find songs for '{mood}'. Try adding a genre name!")

    except Exception as e:
        st.error(f"Spotify Error: {e}")