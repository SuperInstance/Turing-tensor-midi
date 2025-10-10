import speech_recognition as sr
import os
import webbrowser
import datetime
import pyttsx3
import time
import requests
import pywhatkit
from newsapi import NewsApiClient
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
import threading
from dotenv import load_dotenv

# ------------------ CONFIG ------------------ #
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "4c27f298feef4f588a754227e16c0a92")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "8F87QLEGELYUCNZTSDJV3S5Q5")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# ------------------ GLOBAL FLAGS ------------------ #
active = False  # Whether Jarvis is active
running = True  # Whether Jarvis should keep listening

# ------------------ TTS ENGINE ------------------ #
def init_engine():
    engine = pyttsx3.init()
    engine.setProperty('rate', 165)
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    for voice in voices:
        if "en-gb" in voice.id.lower() and "male" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    return engine

def say(text: str):
    if text:
        print(f"\n🧠 JARVIS: {text}\n")
        try:
            engine = init_engine()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[TTS Error]: {e}")
            try:
                if os.name == 'nt':
                    os.system(
                        f'PowerShell -Command "Add-Type –AssemblyName System.Speech; '
                        f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\')"'
                    )
            except:
                pass

# ------------------ STARTUP ------------------ #
def startup():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 70)
    print("             🤖  J A R V I S   T E R M I N A L   M O D E")
    print("=" * 70)
    lines = ["Initializing systems...", "Loading modules...", "Activating voice engine..."]
    for line in lines:
        say(line)
        time.sleep(0.6)
    hour = datetime.datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    c_time = datetime.datetime.now().strftime("%H:%M")
    say(f"{greeting}, sir. The current time is {c_time}. Jarvis is online and fully operational.")
    print("\n🎧 Passive listening mode started — say 'Jarvis' to wake me up.\n")

# ------------------ SPEECH RECOGNITION ------------------ #
def takeCommand(timeout=8, limit=10):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=limit)
            query = r.recognize_google(audio, language="en-IN")
            print(f"👨🏻‍🚀 USER: {query}")
            return query.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            say("Network issue detected, sir.")
            return ""

# ------------------ ACTIVE MODE ------------------ #
def main_active_loop():
    global active, running
    say("Jarvis online and ready, sir.")
    while active:
        query = takeCommand()
        if not query:
            continue

        # Deactivation hotwords
        if any(kw in query for kw in ["thank you jarvis", "go to idle jarvis", "sleep jarvis"]):
            say("Understood, sir. Going to standby mode.")
            active = False
            break

        # Shutdown hotwords
        if any(kw in query for kw in ["stop jarvis", "shutdown jarvis", "exit", "quit"]):
            say("Understood, sir. Shutting down completely.")
            active = False
            running = False
            break

        # --- Command Handling ---
        if "hi jarvis" in query or "hello jarvis" in query:
            say("Good day, sir. How may I assist you?")
        elif "who are you" in query or "introduce yourself" in query:
            say("I am Jarvis, your personal AI assistant — designed to serve you with precision and courtesy, sir.")
        elif "what's the time" in query or "time" in query:
            hour = datetime.datetime.now().strftime("%H")
            minute = datetime.datetime.now().strftime("%M")
            say(f"Sir, the time is {hour} hours and {minute} minutes.")
        elif "news about" in query or "latest news on" in query:
            topic = query.replace("news about", "").replace("latest news on", "").strip()
            get_news(topic)
        elif "what's the weather in" in query or "weather in" in query:
            location = query.replace("what's the weather in", "").replace("weather in", "").strip()
            get_weather(location)
        elif "play on youtube" in query:
            video = query.replace("play on youtube", "").strip()
            if video:
                say(f"Playing {video} on YouTube, sir.")
                pywhatkit.playonyt(video)
            else:
                say("Please specify the video name, sir.")
        elif "search for" in query:
            term = query.replace("search for", "").strip()
            say(f"Searching for {term} on Google.")
            webbrowser.open(f"https://www.google.com/search?q={term}")
        elif "open " in query:
            site = query.replace("open", "").strip().replace(" ", "")
            url = f"https://{site}" if not site.startswith("http") else site
            say(f"Opening {site}, sir.")
            webbrowser.open(url)


        else:
            response = chat_with_gpt_oss_20b(query)
            say(response)

# ------------------ PASSIVE MODE ------------------ #
def passive_listen():
    global active, running
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎧 Jarvis is passively listening... (say 'Jarvis' to activate)")
        while running:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                phrase = recognizer.recognize_google(audio, language="en-GB").lower()
                if "jarvis" in phrase and not active:
                    active = True
                    say("Yes sir?")
                    main_active_loop()
                elif any(word in phrase for word in ["stop jarvis", "shutdown jarvis"]):
                    say("Understood, sir. Shutting down systems.")
                    running = False
                    break
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"[Passive Listen Error]: {e}")
                continue

# ------------------ HELPER FUNCTIONS ------------------ #
def chat_with_gpt_oss_20b(user_query):
    if not OPENROUTER_API_KEY:
        return "I'm sorry sir, the AI service is not configured properly."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Jarvis, a polite, intelligent, British AI assistant. "
                    "Always address the user as 'sir' and respond formally but naturally."
                ),
            },
            {"role": "user", "content": user_query},
        ],
        "temperature": 0.6,
        "max_tokens": 300,
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=headers, data=json.dumps(payload), timeout=20)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e1:
        print(f"[GPT-OSS Error]: {e1}")
        try:
            payload["model"] = "mistralai/mistral-7b-instruct:free"
            response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                     headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e2:
            print(f"[Mistral Fallback Error]: {e2}")
            return "I'm sorry sir, both AI systems are currently unavailable."

def get_weather(location):
    say(f"Fetching weather details for {location}")
    try:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}?key={WEATHER_API_KEY}&unitGroup=metric"
        data = requests.get(url).json()
        if "days" in data:
            today = data["days"][0]
            report = f"The current temperature in {location} is {today['temp']}°C. " \
                     f"Weather: {today['conditions']}. Humidity: {today['humidity']}%. Wind: {today['windspeed']} km/h."
            say(report)
        else:
            say("Sorry, I couldn't retrieve weather data, sir.")
    except Exception as e:
        say("Error fetching weather, sir.")
        print(f"[Weather Error]: {e}")

def get_news(query="latest"):
    say(f"Fetching the latest news about {query}")
    try:
        headlines = newsapi.get_top_headlines(q=query, language='en', country='us')
        if headlines["status"] == "ok" and headlines["totalResults"] > 0:
            for i, article in enumerate(headlines["articles"][:5], start=1):
                say(f"News {i}: {article['title']}")
        else:
            say("No recent news found, sir.")
    except Exception as e:
        say("Error fetching news, sir.")
        print(f"[News Error]: {e}")

# ------------------ MAIN ------------------ #
def main():
    startup()
    listener_thread = threading.Thread(target=passive_listen, daemon=True)
    listener_thread.start()
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        say("Force closing, sir.")
    finally:
        say("Jarvis offline. Goodbye, sir.")

if __name__ == '__main__':
    main()
