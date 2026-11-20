import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 170)

engine.say("Hello Mithra, I am Thozhan, your friendly assistant.")
engine.runAndWait()
print("Done speaking.")