import google.generativeai as genai
import os

# API key from environment
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

genai.configure(api_key=GOOGLE_API_KEY)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
