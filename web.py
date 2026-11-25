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
        model="gemini-flash-lite-latest",
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
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>THOZHAN</title>
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Segoe UI", Arial, sans-serif;
  background: #eef2f7;
  display: flex;
  justify-content: center;
}
#app {
  width: 100%;
  max-width: 760px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: white;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.08);
}
header {
  padding: 16px 20px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
}
header h1 { margin: 0; font-size: 22px; letter-spacing: 2px; }
header p { margin: 4px 0 0 0; font-size: 13px; opacity: 0.85; }
#box {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #f8fafc;
}
.msg {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 16px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 15px;
}
.you {
  align-self: flex-end;
  background: #4f46e5;
  color: white;
  border-bottom-right-radius: 4px;
}
.bot {
  align-self: flex-start;
  background: white;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 4px;
}
#status {
  padding: 0 20px;
  height: 22px;
  font-size: 13px;
  color: #64748b;
  background: #f8fafc;
}
#bar {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #e2e8f0;
  align-items: center;
}
#q {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #cbd5e1;
  border-radius: 24px;
  font-size: 15px;
  outline: none;
}
#q:focus { border-color: #4f46e5; }
button {
  border: none;
  border-radius: 20px;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
}
.main { background: #4f46e5; color: white; }
.main:hover { background: #4338ca; }
.soft { background: #e2e8f0; color: #1e293b; }
.soft:hover { background: #cbd5e1; }
#tools {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 0 16px 12px 16px;
  font-size: 13px;
  color: #475569;
}
</style>
</head>
<body>
<div id="app">
  <header>
    <h1>THOZHAN</h1>
    <p>Your screen-aware AI friend. Press Ctrl+Shift+X to show me your screen.</p>
  </header>
  <div id="box"></div>
  <div id="status"></div>
  <div id="bar">
    <input type="text" id="q" placeholder="Ask THOZHAN...">
    <button class="soft" onclick="listen()">🎤</button>
    <button class="main" onclick="send()">Send</button>
  </div>
  <div id="tools">
    <button class="soft" onclick="newChat()">New chat</button>
    <label><input type="checkbox" id="voice" checked> Voice</label>
  </div>
</div>
<script>
var waiting = false;

function addMsg(text, who) {
  var box = document.getElementById("box");
  var div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

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
  var status = document.getElementById("status");
  var text = q.value;
  if (text.trim() == "") { return; }

  waiting = true;
  addMsg(text, "you");
  status.innerText = "THOZHAN is thinking...";
  q.value = "";

  try {
    var res = await fetch("/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: text})
    });
    var data = await res.json();
    addMsg(data.answer, "bot");
    if (document.getElementById("voice").checked) { speak(data.answer); }
  } catch (err) {
    addMsg("Could not reach the server. Is web.py still running?", "bot");
  }

  status.innerText = "";
  waiting = false;
}

async function newChat() {
  window.speechSynthesis.cancel();
  await fetch("/new", {method: "POST"});
  document.getElementById("box").innerHTML = "";
  addMsg("Fresh chat started. How can I help?", "bot");
}

document.getElementById("q").addEventListener("keydown", function(e) {
  if (e.key == "Enter") { send(); }
});

addMsg("Hi! I'm THOZHAN. Ask me anything, or press Ctrl+Shift+X first so I can see your screen.", "bot");
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