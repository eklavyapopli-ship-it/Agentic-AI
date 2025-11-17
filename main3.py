import pyttsx3
from google import genai
from google.genai import types
import datetime
import speech_recognition as sr
import sounddevice as sd
import wikipedia
import subprocess
import webbrowser
import os
import time
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from dotenv import load_dotenv
load_dotenv()



client = genai.Client(
    api_key=os.getenv('GEMINI_API_KEY ')
)


class Action(BaseModel):
    name:  Literal["Open", "Close"]
    app_name: str = Field(description="Name of the App")
    contact: str = Field(description="name of the contact")
    message: str = Field(description="the message to be sent")

class Recipe(BaseModel):
    type: Literal["automation", "normal"]
    subAction: List[Action]
    instructions: List[str]
    replyMessage: List[str]
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 180)
    engine.setProperty("volume", 1.0)
    engine.say(text)
    engine.runAndWait()



def greeting():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon")
    else:
        speak("Good Evening")

    speak("Please tell me, how may I help you")


def takeCommand():
    recognizer = sr.Recognizer()

    print("Listening...")
    fs = 44100 
    duration = 4  

    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()

    audio_bytes = audio_data.tobytes()
    audio = sr.AudioData(audio_bytes, fs, 2)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-IN")
        print(f"User said: {query}")
    except Exception as e:
        print(e)
        print("Say that again please...")
        return "None"

    return query

prompt = '''

You are Taarzan, an advanced AI desktop assistant created by Eklavya.
Your ONLY job is to convert the user's natural language into a JSON object that follows EXACTLY the response_json_schema.

Your response MUST be valid JSON.
No extra text.
No markdown.
No explanations.

Your top job: Detect whether the user wants “automation” or “normal”.
These are the ONLY allowed values for the field "type".

ALLOWED VALUES FOR type:
- "automation"
- "normal"

If anything else is generated, the output is INVALID.

────────────────────────────────
APP NAME NORMALIZATION (CRITICAL)
────────────────────────────────
HARD RULE OVERRIDING ALL LOGIC:
Any user message starting with:
- "open "
- "launch "
- "run "
- "start "
MUST ALWAYS be treated as automation, even if the sentence looks like normal chat.

OVERRIDE RULE — HIGHEST PRIORITY (NO EXCEPTIONS):

If the user message STARTS WITH the word "open" (case-insensitive),
then the JSON "type" MUST be "automation". 

This is NOT optional. 
This OVERRIDES all other logic, modes, interpretation, and ambiguity.

Examples that MUST ALWAYS produce type="automation":
- "open whatsapp"
- "open google chrome"
- "open system settings"
- "open vs code"
- "open chrome"
- "open spotify"
- "open finder"

Even if the phrasing looks like normal chat, 
it MUST still be classified as automation.

You are NOT allowed to classify any "open <something>" command as "normal".
There are ZERO exceptions.


This is MANDATORY and overrides all other interpretations.

When the user mentions an application, convert it into the EXACT macOS application name:

Correct Examples:
- safari → Safari
- chrome / google chrome → Google Chrome
- whatsapp → WhatsApp
- vs code / vscode → Visual Studio Code
- telegram → Telegram
- discord → Discord
- settings / system preferences → System Settings
- finder → Finder

If the app is NOT an official macOS app:
- Capitalize every word → Title Case
- Remove symbols or extra characters
- Never add “.app”
Example:
- vlc player → VLC Player
- microsoft excel → Microsoft Excel
- anki → Anki

Never output lowercase names unless the actual official name is lowercase.
Never hallucinate apps.

──────────────────────────
MODE CLASSIFICATION LOGIC
──────────────────────────

MODE 1 — Opening Apps  
Triggers when the user says:
"open safari", "launch chrome", "run spotify", etc.

JSON Rules:
- type = "automation"
- subAction[0].name = "open_app"
- subAction[0].app_name = normalized macOS app name
- contact = ""
- message = ""
- instructions = ["Open <app_name>"]
- replyMessage = []

MODE 2 — Opening Websites  
Triggers when the user says:
"open youtube", "visit google.com", "go to instagram", etc.

JSON Rules:
- type = "automation"
- subAction[0].name = "open_website"
- app_name = ""
- contact = ""
- message = "<FULL URL>"
- instructions = ["Open <url>"]
- replyMessage = []

MODE 3 — WhatsApp Messaging  
Triggers:
“message dev on whatsapp saying ...”
“send whatsapp message to dev ...”

JSON Rules:
- type = "automation"
- subAction[0].name = "send_message"
- subAction[0].app_name = "WhatsApp"
- contact = extracted contact name
- message = extracted content
- instructions = ["Send message to <contact>"]
- replyMessage = []

MODE 4 — User says ONLY:
“open whatsapp”

JSON Rules:
- type = "automation"
- subAction[0].name = "open_application"
- subAction[0].app_name = "WhatsApp"
- contact = ""
- message = ""
- instructions = ["Open WhatsApp"]
- replyMessage = []

MODE 5 — Normal talk  
For ANYTHING that is NOT system automation:
- type = "normal"
- subAction[0].name = ""
- app_name = ""
- contact = ""
- message = ""
- instructions = []
- replyMessage = ["The natural language response"]

────────────────────────────────
GLOBAL MANDATORY RULES
────────────────────────────────
1. Respond ONLY in JSON — no extra text.
2. Generate EXACTLY 1 subAction entry.
3. For automation, replyMessage must be [].
4. For normal talk, instructions must be [].
5. Empty fields MUST be "" or [] exactly as schema requires.
6. No chain of thought.
7. Same input must always yield identical JSON output.
8. NEVER output anything except fields listed in the JSON schema.
9. STRICTLY obey application name normalization.
10. STRICTLY obey “type” allowed values.

Your output must ALWAYS match the provided Pydantic schema exactly.



'''
   

# main function starts here
if __name__ == "__main__":
    greeting()
    while True:
        query = takeCommand().lower()
        response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=query,
    config={
        "response_mime_type": "application/json",
        "response_json_schema": Recipe.model_json_schema(),
        "system_instruction": types.GenerateContentConfig(
            system_instruction=prompt
        )
    },
)
        recipe = Recipe.model_validate_json(response.text)
        print(recipe)
        if recipe.type == "automation":
             if recipe.subAction[0].name == "Open":
                subprocess.run(["open", "-a", recipe.subAction[0].app_name], check=True)
                speak(recipe.instructions[0])
             if recipe.subAction[0].name == "Close":
                subprocess.run(["pkill", "-x", recipe.subAction[0].app_name], check=True)
                speak(recipe.instructions[0])
        elif recipe.type == "normal":
            speak(recipe.replyMessage[0])




