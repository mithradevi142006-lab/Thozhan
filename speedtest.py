import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

models = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
]

for name in models:
    start = time.time()
    try:
        client.models.generate_content(model=name, contents="Say hi")
        print(name, "-> OK in", round(time.time() - start, 1), "seconds")
    except Exception as e:
        print(name, "-> FAILED in", round(time.time() - start, 1), "seconds:", str(e)[:100])