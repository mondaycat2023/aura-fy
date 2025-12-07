import google.generativeai as genai

# Paste your key here
GEMINI_API_KEY = "AIzaSyDpE707D2uulWoMRl8XEZWcZ31_GKp18Ng"

genai.configure(api_key=GEMINI_API_KEY)

print("Searching for available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found available model: {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")