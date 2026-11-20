import pyttsx3
import os
import time
import keyboard
import pyautogui
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

instruction = ( 
    "You are THOZHAN, a friendly assistant who helps a student build projects. "
    "You can see the student's screen in each message. "
    "Guide them with numbered steps, one step at a time. "
    "Use simple English and simple Python code. "
    "If you see an error on the screen, explain that exact error and how to fix it."
    "If the student asks for a short answer, keep it to one or two sentences. "
) 

if os.path.exists("project.txt"):
    with open("project.txt", "r", encoding="utf-8") as f:
        project_info = f.read()
    instruction = instruction + "\n\nThe student's current project:\n" + project_info
    print("Project info loaded.")
else:
    print("No project.txt found. Running without project info.")

if os.path.exists("history.txt"):
    with open("history.txt", "r", encoding="utf-8") as f:
        old_chat = f.read()
    if old_chat.strip() != "":
        old_chat = old_chat[-3000:]
        instruction = instruction + "\n\nEarlier conversation with the student (for context only):\n" + old_chat
        print("Past history loaded.")

def make_chat():
    return client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(system_instruction=instruction),
    )

def speak(text):
    clean = text.replace("*", "").replace("#", "").replace("`", "")
    clean = clean[:600]
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    engine.say(clean)
    engine.runAndWait()

chat = make_chat()

print("THOZHAN is ready.")
print("Commands: quit = exit, new = start a fresh chat")

while True:
    question = input("\nYou: ")
    command = question.strip().lower()

    if command == "":
        continue
    if command == "quit":
        print("Bye!")
        break
    if command == "new":
        chat = make_chat()
        print("Started a fresh chat.")
        continue

    print("Switch to your screen and press Ctrl+Shift+X to send...")
    keyboard.wait("ctrl+shift+x")

    img = pyautogui.screenshot()
    print("Screen captured! Thinking...")

    answer = None
    for attempt in range(1, 5):
        try:
            response = chat.send_message([img, question])
            answer = response.text
            break
        except Exception as e:
            print("Attempt", attempt, "failed. Retrying in 5 seconds...")
            last_error = e
            if "429" in str(e):
                break
            time.sleep(5)

        print() 
    if answer:
        print("THOZHAN:", answer)
        with open("history.txt", "a", encoding="utf-8") as f:
            f.write("You: " + question + "\n")
            f.write("THOZHAN: " + answer + "\n\n")
        speak(answer)
    else:
        print("Still failing. Last error:", last_error)