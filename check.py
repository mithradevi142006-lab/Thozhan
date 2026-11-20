import pyautogui
from dotenv import load_dotenv
import os

load_dotenv()
print("Key found:", os.getenv("GEMINI_API_KEY") is not None)

img = pyautogui.screenshot()
img.save("test.png")
print("Screenshot saved as test.png")