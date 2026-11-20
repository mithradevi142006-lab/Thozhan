import os
import time
import keyboard
import pyautogui
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

instruction = (
    "You are THOZHAN, a friendly assistant who helps a student build projects. "
    "Guide them with numbered steps, one step at a time. "
    "Use simple English and simple Python code. "
    "A screenshot is attached only when the student has captured their screen. "
    "When a screenshot is attached, it shows the student's screen. "
    "If no screenshot is attached, just reply to the message and do not talk about the screen. "
    "If the student asks for a short answer, keep it to one or two sentences. "
)

if os.path.exists("project.txt"):
    with open("project.txt", "r", encoding="utf-8") as f:
        instruction = instruction + "\n\nThe student's current project:\n" + f.read()

if os.path.exists("history.txt"):
    with open("history.txt", "r", encoding="utf-8") as f:
        old_chat = f.read()
    if old_chat.strip() != "":
        old_chat = old_chat[-3000:]
        instruction = instruction + "\n\nEarlier conversation with the student (for context only):\n" + old_chat


def make_chat():
    return client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(system_instruction=instruction),
    )


chat = make_chat()

app = Flask(__name__)

latest_img = None


def capture():
    global latest_img
    latest_img = pyautogui.screenshot()
    print("Screen captured!")


keyboard.add_hotkey("ctrl+shift+x", capture)

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>THOZHAN</title>
<style>
body { font-family: Arial; max-width: 700px; margin: 30px auto; }
#box { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; white-space: pre-wrap; }
input[type=text] { width: 60%; padding: 8px; }
button { padding: 8px; }
</style>
</head>
<body>
<h1>THOZHAN</h1>
<div id="box"></div>
<div id="status"></div>
<br>
<input type="text" id="q" placeholder="Ask THOZHAN...">
<button onclick="send()">Send</button>
<button onclick="newChat()">New chat</button>
<label><input type="checkbox" id="voice" checked> Voice</label>
<button onclick="listen()">🎤 Speak</button>
<script>
var waiting = false;

function speak(text) {
  var clean = text.replace(/[*#`]/g, "").slice(0, 600);
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(clean);
  window.speechSynthesis.speak(u);
}

function listen() {
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  var status = document.getElementById("status");
  if (!SR) {
    status.innerText = "This browser has no speech recognition. Use Chrome or Edge.";
    return;
  }
  var rec = new SR();
  rec.lang = "en-IN";
  rec.onstart = function() {
    status.innerText = "Listening... speak now";
  };
  rec.onresult = function(e) {
    document.getElementById("q").value = e.results[0][0].transcript;
    status.innerText = "";
  };
  rec.onerror = function(e) {
    status.innerText = "Mic error: " + e.error;
  };
  rec.onend = function() {
    if (status.innerText.startsWith("Listening")) { status.innerText = ""; }
  };
  rec.start();
}

async function send() {
  if (waiting) { return; }
  var q = document.getElementById("q");
  var box = document.getElementById("box");
  var status = document.getElementById("status");
  var text = q.value;
  if (text.trim() == "") { return; }

  waiting = true;
  box.innerText += "You: " + text + "\\n\\n";
  status.innerText = "THOZHAN is thinking...";
  q.value = "";

  var res = await fetch("/ask", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question: text})
  });
  var data = await res.json();

  status.innerText = "";
  box.innerText += "THOZHAN: " + data.answer + "\\n\\n";
  if (document.getElementById("voice").checked) { speak(data.answer); }
  box.scrollTop = box.scrollHeight;
  waiting = false;
}

async function newChat() {
  window.speechSynthesis.cancel();
  await fetch("/new", {method: "POST"});
  document.getElementById("box").innerText = "";
}

document.getElementById("q").addEventListener("keydown", function(e) {
  if (e.key == "Enter") { send(); }
});
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return PAGE


@app.route("/ask", methods=["POST"])
def ask():
    global latest_img
    question = request.json["question"]
    print("Screenshot attached:", latest_img is not None)
    if latest_img is not None:
        content = [latest_img, question]
        latest_img = None
    else:
        content = question

    answer = None
    last_error = None
    for attempt in range(1, 5):
        try:
            response = chat.send_message(content)
            answer = response.text
            break
        except Exception as e:
            last_error = e
            print("Attempt", attempt, "failed:", str(e)[:150])
            if "429" in str(e):
                break
            time.sleep(5)

    if answer is None:
        answer = "Still failing. Last error: " + str(last_error)
    else:
        with open("history.txt", "a", encoding="utf-8") as f:
            f.write("You: " + question + "\n")
            f.write("THOZHAN: " + answer + "\n\n")

    return jsonify({"answer": answer})


@app.route("/new", methods=["POST"])
def new_chat():
    global chat
    chat = make_chat()
    return jsonify({"ok": True})


app.run(port=5000)