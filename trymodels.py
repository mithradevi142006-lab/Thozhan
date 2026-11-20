import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

models = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-lite-latest",
]

for name in models:
    try:
        response = client.models.generate_content(model=name, contents="Say hi")
        print(name, "-> WORKS:", response.text.strip()[:40])
    except Exception as e:
        print(name, "-> FAILED:", str(e)[:100])