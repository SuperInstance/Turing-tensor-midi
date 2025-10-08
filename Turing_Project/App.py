import speech_recognition as sr
import os
import webbrowser
import openai
import subprocess
import datetime
import pyaudio
import pyttsx3  # Importing pyttsx3 for voice
import cv2
import tkinter as tk
import threading
from PIL import Image, ImageTk
from newsapi import NewsApiClient
import requests 
import pywhatkit 
import wikipedia
import psutil
import time
from geopy.geocoders import Nominatim
from geopy.geocoders import * 
import pyjokes
import pyautogui
import sys
import subprocess
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer, QTime, QDate
import socket
from geopy.distance import geodesic


# Initialize NewsAPI (Replace with your actual API key)
newsapi = NewsApiClient(api_key='4c27f298feef4f588a754227e16c0a92')













# Initialize pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level

def say(text):
    """Function to make JARVIS speak"""
    engine.say(text)
    engine.runAndWait()



   

def startup():
    say("Initializing Jarvis")
    say("Starting all systems applications")
    say("Installing and checking all drivers")
    say("Caliberating and examining all the core processors")
    say("Checking the internet connection")
    say("Wait a moment sir")
    say("All drivers are up and running")
    say("All systems have been activated")
    say("Now I am online")
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<=12:
        say("Good Morning")
    elif hour>12 and hour<18:
        say("Good afternoon")
    else:
        say("Good evening")
    c_time = datetime.datetime.now().strftime("%H:%M")
    say(f"Currently it is {c_time}")
    say("I am Jarvis. Online and ready sir. Please tell me how may I help you")
    






def takeCommand():
    """Function to take user voice input"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"USER: {query}")
            return query
        except Exception as e:
            return "Some Error Occurred. Sorry from Jarvis"




WEATHER_API_KEY = "8F87QLEGELYUCNZTSDJV3S5Q5"

def get_weather(location):
    """Fetches and reads out the weather information for a given location."""
    say(f"Fetching weather details for {location}")
    
    # Construct API request URL
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}?key={WEATHER_API_KEY}&unitGroup=metric"

    try:
        response = requests.get(url)
        weather_data = response.json()

        if "days" in weather_data:
            today_weather = weather_data["days"][0]
            temp = today_weather["temp"]
            condition = today_weather["conditions"]
            humidity = today_weather["humidity"]
            wind_speed = today_weather["windspeed"]

            weather_report = (f"The current temperature in {location} is {temp} degrees Celsius. "
                              f"The weather is {condition}. Humidity is at {humidity} percent, "
                              f"with a wind speed of {wind_speed} kilometers per hour.")

            say(weather_report)
            print(weather_report)

        else:
            say("Sorry, I couldn't retrieve the weather data.")
            print("Error: Invalid response from weather API.")

    except Exception as e:
        say("There was an error fetching the weather.")
        print(f"Error fetching weather: {e}")




def take_note(text):
    """
    Saves the given text as a note with a timestamp.
    :param text: The text to be saved in the note.
    """
    try:
        # Get current date and time
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Define note file
        note_filename = "jarvis_notes.txt"

        # Write to file
        with open(note_filename, "a") as file:
            file.write(f"{timestamp} - {text}\n")

        say("I've made a note of that.")
        print(f"Note saved: {text}")

    except Exception as e:
        say("Sorry, I couldn't save the note.")
        print(f"Error saving note: {e}")






def get_news(query="latest"):
    """Fetches and reads out the latest news headlines based on the given query."""
    say(f"Fetching the latest news about {query}")

    # Get top headlines
    top_headlines = newsapi.get_top_headlines(q=query, language='en', country='us')

    if top_headlines["status"] == "ok" and top_headlines["totalResults"] > 0:
        articles = top_headlines["articles"][:5]  # Get top 5 news articles
        for i, article in enumerate(articles, start=1):
            title = article["title"]
            say(f"News {i}: {title}")
            print(f"News {i}: {title}")  # Print the news in the console
    else:
        say("Sorry, I couldn't find any recent news on that topic.")

def search_youtube(query):
    """Uses the YouTube search URL to search for the query"""
    search_url = f"https://www.youtube.com/results?search_query={query}"
    print(f"Searching YouTube for: {query}")
    
    # Open the YouTube search page with the query
    webbrowser.open(search_url)
    
    # Let Jarvis speak the search result
    say(f"Searching YouTube for {query}")

def tell_me(topic):
    """
    Fetches a brief summary of the given topic from Wikipedia.
    :param topic: A string representing the topic to search for.
    :return: First 500 characters from Wikipedia if successful, otherwise an error message.
    """
    try:
        summary = wikipedia.summary(topic, sentences=2)  # Fetch a short summary
        say(summary)  # Let JARVIS read it out
        print(summary)  # Display in console
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        say("There are multiple results for this topic. Please be more specific.")
        print(f"Disambiguation error: {e}")
    except wikipedia.exceptions.PageError:
        say("I couldn't find any information on that topic.")
        print("No Wikipedia page found for the given topic.")
    except Exception as e:
        say("Sorry, I ran into an error while searching Wikipedia.")
        print(f"An error occurred: {e}")

def monitor_system():
    """Fetches and displays real-time CPU and memory usage"""
    try:
        while True:
            cpu_usage = psutil.cpu_percent(interval=1)  # CPU usage in percentage
            memory_info = psutil.virtual_memory()  # Get memory stats
            memory_usage = memory_info.percent  # Memory usage in percentage
            available_memory = round(memory_info.available / (1024 * 1024 * 1024), 2)  # Convert to GB

            system_status = f"CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage}% | Available Memory: {available_memory} GB"
            
            print(system_status)  # Display in console
            say(system_status)  # Make JARVIS speak the status

            time.sleep(5)  # Adjust the refresh rate (5 seconds)

    except Exception as e:
        say("Sorry, I couldn't fetch real-time system data.")
        print(f"Error: {e}")

def get_location_details(location_name):
    """Fetches location details (city, state, country) and calculates distance from the user's location"""
    try:
        geolocator = Nominatim(user_agent="Jarvis")
        
        # Get user's current location (Manually set or use a geolocation API)
        current_location = geolocator.geocode("New Delhi, India")  # Change this to your actual location
        target_location = geolocator.geocode(location_name)

        if not target_location:
            say("Sorry, I couldn't find the location.")
            return None, None, None

        # Extract details
        current_coords = (current_location.latitude, current_location.longitude)
        target_coords = (target_location.latitude, target_location.longitude)

        # Calculate distance
        distance_km = round(geodesic(current_coords, target_coords).kilometers, 2)

        target_details = {
            "city": target_location.raw.get("address", {}).get("city", ""),
            "state": target_location.raw.get("address", {}).get("state", ""),
            "country": target_location.raw.get("address", {}).get("country", ""),
        }

        return current_coords, target_details, distance_km

    except Exception as e:
        print(f"Error fetching location: {e}")
        return None, None, None

def get_ip_details():
    """Fetches both public and local IP addresses"""
    try:
        # Fetch public IP
        public_ip = requests.get("https://api.ipify.org").text

        # Fetch local IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        return public_ip, local_ip
    except Exception as e:
        return None, None


def my_location():
    """Fetches the current location using IP-based geolocation."""
    try:
        response = requests.get("https://ipinfo.io/json").json()
        
        city = response.get("city", "Unknown")
        state = response.get("region", "Unknown")
        country = response.get("country", "Unknown")

        return city, state, country
    except Exception as e:
        return None, None, None


def take_screenshot():
    """Captures a screenshot and saves it with a user-defined or timestamped name."""
    try:
        say("By what name do you want to save the screenshot?")
        name = takeCommand().strip()  # Get user input for filename

        if not name:
            name = f"screenshot_{int(time.time())}"  # Auto-generate name if no input
        
        # Define a folder to store screenshots
        save_path = os.path.join(os.getcwd(), "Screenshots")
        os.makedirs(save_path, exist_ok=True)  # Create the folder if it doesn't exist
        
        file_path = os.path.join(save_path, f"{name}.png")

        # Capture and save screenshot
        img = pyautogui.screenshot()
        img.save(file_path)

        say(f"Screenshot saved successfully as {name}.png in the Screenshots folder.")
        print(f"Screenshot saved at: {file_path}")

    except Exception as e:
        say("Sorry, I was unable to take a screenshot.")
        print(f"Error: {e}")







def main():
    while True:
        query = takeCommand().lower()  # Convert to lowercase for better matching

        # Open Websites
        sites = [["youtube", "https://www.youtube.com"],
                 ["wikipedia", "https://www.wikipedia.com"],
                 ["google", "https://www.google.com"],
                 ["chatgpt", "https://chatgpt.com"],
                 ["academic portal","academic.iitg.ac.in/online/"],
                 ["github", "https://github.com"],
                 ["facebook", "https://www.facebook.com"],
                 ["instagram", "https://www.instagram.com"],
                 ["twitter", "https://twitter.com"],
                 ["linkedin", "https://www.linkedin.com"],
                 ["reddit", "https://www.reddit.com"],
                 ["stackoverflow", "https://stackoverflow.com"],
                 ["official mail","https://outlook.office.com/mail/"],
                 ["google drive","https://drive.google.com/drive/my-drive"],
                 ["google sheets","https://docs.google.com/spreadsheets/d/12345678901234567890/edit?usp=sharing"],
                 ["effectiviology","https://www.effectiviology.com/"],
                ]

        for site in sites:
            if f"open {site[0]}" in query:
                say(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])

        # Play Music
        if "play skyfall" in query:
            musicPath = r"C:\Users\shash\OneDrive\Desktop\Skyfall.mp3"
            say("Playing skyfall")
            os.startfile(musicPath)
            print("Playing Skyfall")

        # Basic conversation with the bot
        elif "hi jarvis" in query:
            say("Hello sir")
            print("Hello Sir")

        elif "who are you" in query or "introduce yourself" in query:
            say("Allow me to introduce myself. I am Jarvis, a virtual artificial intelligence, and I'm here to assist you with a variety of tasks as best I can, 24 hours a day, 7 days a week.")
            print("Allow me to introduce myself. I am Jarvis, a virtual artificial intelligence, and I'm here to assist you with a variety of tasks as best I can, 24 hours a day, 7 days a week.")

        # Tell Time
        elif "what's the time" in query:
            hour = datetime.datetime.now().strftime("%H")
            min = datetime.datetime.now().strftime("%M")
            say(f"Sir, the time is {hour} hours and {min} minutes")
            print(f"Sir, the time is {hour} hours and {min} minutes")

        # Open Brave Browser
        elif "open brave" in query:
            brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
            say("Opening Brave browser")
            os.startfile(brave_path)
            print("Opening Brave browser")

        #to open file explorer
        elif "open file explorer" in query:
            Explorer_path = r"C:\Windows\explorer.exe"
            os.startfile(Explorer_path)
            say("Opening File Explorer")
            print("Opening file explorer")


        elif "open command prompt" in query:
            cmd_path = r"C:\Windows\System32\cmd.exe"
            os.startfile(cmd_path)
            say("Opening Command Prompt")
            print("Opening Command Preompt")


        elif " open chrome" in query:
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            os.startfile(chrome_path)
            say("Opening Chrome")
            print("Opening Chrome browser")


        elif "open notepad" in query:
            notepad_path = r"C:\Windows\system32\notepad.exe"
            os.startfile(notepad_path)
            say("Opening Notepad")
            print("Opening Notepad")


        elif "open firefox" in query:
            firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
            os.startfile(firefox_path)
            say("Opening Firefox")
            print("Opening firefox")


        elif "open task manager" in query:
            task_manager_path = r"C:\Windows\system32\taskmgr.exe"
            os.startfile(task_manager_path)
            say("Opening Task Manager")
            print("Opening Task Manager")

        elif "open system information" in query:
            system_info_path = r"C:\Windows\system32\control.exe"
            os.startfile(system_info_path)
            say("Opening System Information")
            print("Opening system information")


        elif " open settings" in query:
           settings_path = r"C:\Windows\system32\control.exe"
           os.startfile(settings_path)
           say("Opening Settings")
           print("Opening Settings")


        
        elif "open sticky notes"  in query:
            sticky_notes_path = r"C:\Windows\system32\msedge.exe"
            os.startfile(sticky_notes_path)
            say("Opening Sticky Notes")
            print("Opening Sticky Notes")
       
        elif "open vs code" in query:
            visual_studio_code_path = r"C:\Users\shash\AppData\Local\Programs\Microsoft VS Code\Code.exe"
            os.startfile(visual_studio_code_path)
            say("Opening Visual Studio Code")
            print("Opening VS Code")

        elif "news about" in query or "latest news on" in query:
          search_topic = query.replace("news about", "").replace("latest news on", "").strip()
          get_news(search_topic)
              
              
        elif "search on youtube for" in query:
            # Extract the query after "search on youtube"
            search_query = query.replace("search on youtube for", "").strip()
            say(f"Searching YouTube for {search_query}")
            
            # Construct the YouTube search URL
            search_url = f"https://www.youtube.com/results?search_query={search_query}"
            webbrowser.open(search_url)  # Open the URL in the default browser
            print(f"Searching YouTube for: {search_query}")

            # Let Jarvis speak the result
            say(f"Here are the results for {search_query} on YouTube")
   
        elif "what's the weather in" in query or "weather in" in query:
          location = query.replace("what's the weather in", "").replace("weather in", "").strip()
          get_weather(location)
       
        elif "tell me about" in query:
         topic = query.replace("tell me about", "").strip()
         tell_me(topic)
       

        elif "play on youtube" in query:
          video = query.replace("play on youtube", "").strip()
          if video:
           say(f"Okay sir, playing {video} on YouTube")
           pywhatkit.playonyt(video)
           print(f"Playing {video} on YouTube...")
          
          else:
           say("Please specify a video name to play.")

        elif "search for" in query:
         # Extract the search query after "search for"
         search_query = query.replace("search for", "").strip()
         say(f"Searching for {search_query} on Google")

         # Construct the Google search URL with the query
         search_url = f"https://www.google.com/search?client=firefox-b-d&q={search_query}"

         # Open the search URL in Firefox using subprocess
         firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
         subprocess.run([firefox_path, search_url])  # Using subprocess to pass the URL to Firefox

         # Let Jarvis speak the result
         say(f"Here are the search results for {search_query} on Google")

        elif "where is" in query:
         place = query.replace("where is", "").strip()
         current_loc, target_loc, distance = get_location_details(place)

         if target_loc:
            city = target_loc.get("city", "")
            state = target_loc.get("state", "")
            country = target_loc.get("country", "")

              # Optional: You can remove this if not needed
            if city:
               response = f"{place} is in {state} state and country {country}. It is {distance} km away from your current location."
            else:
               response = f"{state} is a state in {country}. It is {distance} km away from your current location."

            print(response)
            say(response)
         else:
           say("Sorry, I couldn't get the coordinates of the location you requested. Please try again.")


        elif "ip address" in query:
         public_ip, local_ip = get_ip_details()

         if public_ip and local_ip:
          response = f"Sir, your public IP address is {public_ip}, and your local IP address is {local_ip}."
         elif public_ip:
          response = f"Sir, your public IP address is {public_ip}."
         elif local_ip:
          response = f"Sir, your local IP address is {local_ip}."
         else:
          response = "Sorry, I couldn't fetch your IP address."

         print(response)
         say(response)

        elif "where am i" in query or "current location" in query or "where i am" in query:
         city, state, country = my_location()

         if city and state and country:
           response = f"Sir, you are currently in {city} city, which is in {state} state in {country}."
         else:
           response = "Sorry sir, I couldn't fetch your current location. Please try again."

         print(response)
         say(response)

        elif "take screenshot" in query or "take a screenshot" in query or "capture the screen" in query:
          take_screenshot()

        # Quit Jarvis
        elif "jarvis quit" in query or "quit" in query or "stop" in query or "end this conversation" in query or "this conversation is over" in query:
         say("Goodbye sir. Have a great day!")
         exit()

        # Reset Chat
        elif "reset chat" in query or "clear chat" in query:
          chatStr = ""
          say("Chat is clear now")
        
        else:
         print("Pardon")
         
         
#this time we have got a lot of updates 


#try it out 


#Does this play automatically upon running the code ?











if __name__ == '__main__':
    
    startup()
    
 #start the programs simultaneously 
    takeCommand()
    main()















