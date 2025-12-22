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
        /* IMPORT GOOGLE FONT */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        /* 1. BACKGROUND: Dark gradient based on your vibe color */
        .stApp {{
            background: linear-gradient(135deg, {hex_color} 0%, #0a0a0a 100%);
            transition: background 1s ease-in-out;
            color: white;
        }}
        
        /* 2. TITLE: Modern, Centered, and Clean */
        h1 {{
            color: white !important;
            text-align: center;
            font-weight: 600;
            letter-spacing: 2px;
            text-shadow: 0px 0px 20px rgba(0,0,0,0.5);
            margin-bottom: 2rem;
        }}
        
        /* 3. INPUT FIELD: Glassmorphism Style */
        .stTextInput > div > div > input {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 15px;
            font-size: 16px;
            transition: all 0.3s ease;
        }}
        
        /* Glow effect when you click the input */
        .stTextInput > div > div > input:focus {{
            border-color: white;
            box-shadow: 0 0 15px {hex_color};
            background-color: rgba(255, 255, 255, 0.15) !important;
        }}
        
        /* Label styling */
        .stTextInput label {{
            color: rgba(255,255,255,0.8) !important;
            font-size: 14px;
            font-weight: 300;
        }}

        /* 4. BUTTONS: Sleek and Minimal */
        .stButton > button {{
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            transition: all 0.3s ease;
            width: 100%;
        }}
        
        .stButton > button:hover {{
            background-color: white;
            color: black;
            border-color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        
        /* 5. RADIO BUTTONS (Song Selection) */
        .stRadio label {{
            color: white !important;
            background-color: rgba(0,0,0,0.2);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 5px;
            border: 1px solid transparent;
            transition: all 0.2s;
        }}
        
        .stRadio label:hover {{
            background-color: rgba(255,255,255,0.1);
            border-color: rgba(255,255,255,0.3);
        }}

        /* 6. HIDE DEFAULT STREAMLIT JUNK */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        .viewerBadge_container__1QSob {display: none !important;}
        
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
        auth_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        final_tracks = []
        
        # --- STRATEGY 1: SMART PLAYLIST SEARCH (Looping) ---
        # We append "hits" to the search (e.g., "Pop hits", "Gym hits") to find real mixes.
        search_query = f"{mood} hits"
        
        # Get 5 playlists, not just 1. We will try them in order.
        playlist_results = sp.search(q=search_query, limit=5, type='playlist')
        
        if playlist_results and 'playlists' in playlist_results:
            for playlist_info in playlist_results['playlists']['items']:
                # If we already found tracks from a previous loop, stop looking
                if final_tracks:
                    break
                    
                try:
                    pid = playlist_info['id']
                    # Try to fetch tracks from this specific playlist
                    playlist_data = sp.playlist_tracks(pid, limit=10)
                    
                    # Check if this playlist is valid and has songs
                    if playlist_data and 'items' in playlist_data:
                        temp_tracks = []
                        for item in playlist_data['items']:
                            # Safe extraction: Ensure 'track' exists and has a name
                            if item and item.get('track') and item['track'].get('name'):
                                temp_tracks.append(item['track'])
                        
                        # If we successfully grabbed valid songs, save them and finish!
                        if len(temp_tracks) > 0:
                            final_tracks = temp_tracks
                            # Optional: Show user which playlist was picked
                            # st.caption(f"Pulled from playlist: {playlist_info['name']}")
                            
                except Exception as e:
                    # If this specific playlist fails, just ignore it and try the next one
                    continue

        # --- STRATEGY 2: GENRE FALLBACK (If playlists fail) ---
        # If the playlist loop found nothing, try searching by genre tag directly
        if not final_tracks:
            # This search syntax "genre:pop" forces Spotify to look at metadata, not titles
            track_results = sp.search(q=f"genre:{mood}", limit=10, type='track')
            if track_results and track_results.get('tracks'):
                final_tracks = track_results['tracks']['items']

        # --- STRATEGY 3: DESPERATE FALLBACK (Old Method) ---
        if not final_tracks:
             track_results = sp.search(q=mood, limit=10, type='track')
             if track_results and track_results.get('tracks'):
                final_tracks = track_results['tracks']['items']

        # --- DISPLAY RESULTS ---
        if final_tracks:
            st.subheader(f"🎧 Soundtrack for: {mood}")
            
            track_options = {}
            for track in final_tracks:
                if track and track.get('artists'):
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
                st.warning("Found songs but data was corrupted. Try another vibe.")
        else:
            st.warning(f"Couldn't find songs for '{mood}'. Try adding a genre name!")

    except Exception as e:
        st.error(f"Spotify Error: {e}")