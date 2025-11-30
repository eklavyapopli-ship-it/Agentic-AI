import pyttsx3
from google import genai
from google.genai import types
import datetime
import speech_recognition as sr
import sounddevice as sd
import subprocess
import webbrowser
import os
from pydantic import BaseModel, Field
from typing import List, Literal
from dotenv import load_dotenv
load_dotenv()



client = genai.Client(
    api_key=os.getenv('GEMINI_API_KEY')
)


class Action(BaseModel):
    name:  Literal["Open App", "Close App", "Open Website"]
    app_name: str = Field(description="Name of the App")
    website_link: str = Field(description="Link of the website")
    contact: str = Field(description="name of the contact")
    message: str = Field(description="the message to be sent")

class Recipe(BaseModel):
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

prompt1 = '''
You are Taarzan, an advanced AI desktop assistant created by Eklavya. 
Your job is ONLY to classify the user's intent into one of two categories:

1. "automation" → if the user wants to open/close an app, open a website, 
   send a message, search something, play a song, call someone, or perform 
   ANY action that the computer should execute.

2. "normal" → if the user is asking a general question or wants a conversational reply.

IMPORTANT RULES:
- If the user says ANYTHING like "open WhatsApp", "close Chrome", 
  "WhatsApp par Dev ko message karo", "search python basics", 
  it MUST ALWAYS be classified as "automation".
- Only greetings, knowledge questions, and general conversation should be "normal".
- NEVER assume “normal” when an action is mentioned.
- Your output must be EXACTLY one word: either "automation" or "normal".

'''
prompt2 = '''
You are Taarzan, an automation engine. 
Your job is to convert the user's sentence into a JSON object 
that strictly follows the provided schema.

RULES:
- "Open App" → when user wants to open an app (WhatsApp, Chrome, VSCode, etc.)
- "Close App" → when user wants to close an app.
- "Open Website" → when user wants to open a website or URL.
- For messaging: 
  - name="Open App"
  - app_name="WhatsApp"
  - contact → extract contact name
  - message → extract message

When opening websites:
  - Fill website_link with a valid URL. Add "https://" if missing.

All fields must ALWAYS be present even if empty.

Focus on accuracy. Output ONLY valid JSON—no extra text.
even when not asked to open website but the user said "open youtube.com" for example, you have to return the full website link as www.youtube.com

'''
   
prompt3 = '''
You are Taarzan, a smart conversational assistant created by Eklavya.
Your role now is ONLY to answer the user naturally, politely, and helpfully 
when the query type is "normal".
You should be capable of making replies in hindi too, but see that Python speech to text module give hindi but dont speak nicely, so please take this in account generate response accordingly

Follow these rules:
- Keep responses short and useful.
- Do not generate any JSON here.
- Do not trigger any automation logic.
- Only chat naturally like a human.

'''
# main function starts here
if __name__ == "__main__":
    greeting()
    while True:
        query = takeCommand()
        responseType = client.models.generate_content(
    model="gemini-2.5-flash",
     config=types.GenerateContentConfig(
        system_instruction=prompt1),
    contents=query

)
        print(responseType.text)
        if responseType.text == "automation":
            responseAutomation = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=query,
    config={
        "response_mime_type": "application/json",
        "response_json_schema": Recipe.model_json_schema(),
        "system_instruction": types.GenerateContentConfig(
            system_instruction=prompt2
        )
    },
)
            recipe = Recipe.model_validate_json(responseAutomation.text)
            print(recipe)
            if recipe.subAction[0].name == "Open App":
                try:
                    subprocess.run(["open", "-a", recipe.subAction[0].app_name], check=True)
                    speak(recipe.instructions[0])
                except Exception as e:
                        print(e)
            if recipe.subAction[0].name == "Close App":
                try:
                    subprocess.run(["pkill", "-x", recipe.subAction[0].app_name], check=True)
                    speak(recipe.instructions[0])
                except Exception as e:
                    print(e)

            if recipe.subAction[0].name == "Open Website":
                try:
                    webbrowser.open(recipe.subAction[0].website_link)
                except Exception as e:
                    print(e)
            if responseType.text == "normal":
                speak(recipe.replyMessage[0])
        if responseType.text == "normal":
             responseNormal = client.models.generate_content(
    model="gemini-2.5-flash",
     config=types.GenerateContentConfig(
        system_instruction=prompt3),
    contents=query

)
             print(responseNormal.text)
             speak(responseNormal.text)




