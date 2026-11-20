# THOZHAN - Screen-Aware AI Assistant

THOZHAN ("friend" in Tamil) is an AI assistant that can see my screen while I work and guide me through my projects step by step. I built it to stop the loop of copying code, pasting errors, and describing my screen to an AI chat by hand.

## Features
- Sees my screen using screenshots and the Gemini API
- Hotkey capture (Ctrl+Shift+X) and automatic capture every 5 seconds
- Ask by typing or by speaking (browser speech recognition)
- Answers are shown on screen and read aloud
- Remembers the conversation and my project (project.txt)
- Saves chat history and loads recent history on the next run
- Two versions: terminal (thozhan.py) and web page (web.py)
- Retries on busy-server errors and stops quickly on quota errors

## Tech stack
Python, Flask, Google Gemini API (google-genai), pyautogui, keyboard, pyttsx3, HTML/JavaScript (Web Speech API)

## How it works
1. The screen is captured with pyautogui.
2. The screenshot and my question are sent to a Gemini model.
3. The answer is shown in the terminal or web page and spoken aloud.

## Setup
1. Install the libraries:
   python -m pip install -r requirements.txt
2. Get a free Gemini API key from https://aistudio.google.com/apikey
3. Copy .env.example to .env and put your key inside it.
4. Write a few lines about your current project in project.txt.

## Run
Web version:
   python web.py
Then open http://127.0.0.1:5000 in Chrome or Edge.

Terminal version:
   python thozhan.py

## Notes
- Tested on Windows. It runs on your own computer because it captures your screen.
- Free Gemini keys have small daily limits per model. If you see a 429 error, change the model name in the code.
- The screenshot is sent to Gemini to answer your question, so avoid asking while private information is visible.

## What I learned
Working with an AI API (rate limits, retries, model changes), screen capture, hotkeys, speech input and output, and building a small Flask web app.