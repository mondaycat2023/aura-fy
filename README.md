# 🍌 Aura-fy: AI-Powered Mood & Music Visualizer

**Aura-fy** is a project that turns your abstract thoughts into a multisensory experience. It uses **Google Gemini AI** to understand the "color" of your mood and **Spotify** to curate a matching soundtrack.

![Project Screenshot](https://via.placeholder.com/800x400?text=App+Screenshot+Placeholder)

## ✨ Features

* **🧠 AI Color Intelligence:** Uses Google's **Gemini 2.5 Flash** model to analyze complex text inputs (e.g., "Cyberpunk City," "Sunday Morning Coffee") and generate a mathematically perfect hex color code.
* **🎨 Dynamic UI:** The entire application interface shifts colors in real-time to match the generated "aura."
* **🎵 Spotify Jukebox:** Connects to the Spotify API to fetch 10 relevant tracks.
* **📻 Smart Player:** Features a "Jukebox Mode" that lets you preview specific songs using the official Spotify Embed widget.

## 🛠 Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **AI Model:** [Google Gemini API](https://ai.google.dev/) (Gemini 2.5 Flash)
* **Music Data:** [Spotipy](https://spotipy.readthedocs.io/) (Spotify Web API)
* **Language:** Python 3.10+

