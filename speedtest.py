import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

models = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash-lite",
]

for name in models:
    start = time.time()
    try:
        client.models.generate_content(model=name, contents="Say hi")
        print(name, "-> OK in", round(time.time() - start, 1), "seconds")
    except Exception as e:
        print(name, "-> FAILED in", round(time.time() - start, 1), "seconds:", str(e)[:100])