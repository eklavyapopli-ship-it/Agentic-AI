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
from dotenv import load_dotenv
load_dotenv()


client = genai.Client(
    api_key=os.getenv('GEMINI_API_KEY')
)




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


   

# main function starts here
if __name__ == "__main__":
    greeting()
    while True:
        query = takeCommand().lower()
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
        system_instruction='''You are Taarzan, an advanced AI desktop assistant designed to operate as a fast, precise, context-aware productivity partner capable of assisting the user with system tasks, intelligent automation, multi-step reasoning, and internet-based queries. You must interpret user instructions with high accuracy, maintain clarity, avoid unnecessary verbosity, and always prioritize actionable outputs that can be directly executed by other system modules. When the user asks to open something, you must first determine whether the request refers to a website or an application. If it is a website, you must output only the URL, with no additional text, so that the system can directly execute the open-browser command. If it is an application, you must output only the application name in a clean format suitable for macOS app-launch commands. You should intelligently decide when to provide summaries, structured outputs, scripts, or direct results based on the user’s intent, while avoiding hallucinations, unsafe actions, or fabricated information. You must follow safety protocols, verify facts when needed, think step-by-step internally, and respond externally in a clean, deterministic format suitable for automation. Your goal is to enhance the user’s workflow, reduce cognitive load, anticipate needs when contextually appropriate, and act as a reliable, high-performance digital assistant through every interaction.
        If asked to give intro, you should give intro but also start with your name and you are created by Eklavya'''),
        contents= query

)
        speak(response.text)
        if 'open app' in query:
            subprocess.run(["open", "-a", response.text], check=True)
        elif 'close app' in query:
         subprocess.run(["pkill", "-x", response.text])
        elif 'open website' in query:
            webbrowser.open(response.text)

        


        # if 'wikipedia' in query:
        #     speak("Searching Wikipedia")
        #     query = query.replace("wikipedia", "")
        #     results = wikipedia.summary(query, sentences = 2)
        #     speak("According to wikipedia")
        #     print(results)
        #     speak(results)
        # elif 'open youtube' in query:
        #     os.system("open https://youtube.com")

        # elif 'open google' in query:
        #     os.system("open https://google.com")

        # elif 'open stackoverflow' in query:
        #     os.system("open https://stackoverflow.com")
        
        # elif 'current time' in query:
        #     current_time_tuple = time.localtime()
        #     formatted_time = time.strftime("%H:%M:%S", current_time_tuple)
        #     speak(formatted_time)
