import speech_recognition as sr
import os
import webbrowser
import datetime
import pyttsx3
import pyautogui
import time
import requests 
import pywhatkit 
import psutil
import socket
from newsapi import NewsApiClient
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Text-to-Speech
def init_engine():
    """Initialize and configure the TTS engine"""
    engine = pyttsx3.init()
    engine.setProperty('rate', 165)
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    
    # Set British English male voice (if available)
    for voice in voices:
        if "en-gb" in voice.id.lower() and "male" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    
    return engine

def say(text: str):
    """Make JARVIS speak aloud and print text."""
    if text:
        print(f"JARVIS: {text}")
        try:
            engine = init_engine()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[TTS Error]: {e}")
            # Try alternative method
            try:
                import os
                if os.name == 'nt':  # Windows
                    os.system(f'PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\')"')
            except:
                pass

def startup():
    """Boot sequence for JARVIS"""
    lines = [
        "Initializing systems...", 
        "Loading modules...", 
        "Activating Jarvis AI engine..."
    ]
    
    for line in lines:
        say(line)
    
    # Greet based on time of day
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    c_time = datetime.datetime.now().strftime("%H:%M")
    say(f"{greeting}, sir. The current time is {c_time}. I am Jarvis, online and fully operational.")
    say("Please tell me, how may I assist you today?")

def takeCommand():
    """Listens to user's voice and recognizes English."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 400
    recognizer.pause_threshold = 0.8
    
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, phrase_time_limit=8)
            query = recognizer.recognize_google(audio, language="en-GB")
            print(f"USER: {query}")
            return query.lower()
        except sr.UnknownValueError:
            say("Sorry sir, I didn't quite catch that. Could you please repeat?")
            return None
        except sr.RequestError as e:
            say("Network issue detected. Please check your connection.")
            print(f"[Speech Recognition Error]: {e}")
            return None

def chat_with_gpt_oss_20b(user_query):
    """Sends query to GPT-OSS-20B model via OpenRouter API."""
    if not OPENROUTER_API_KEY:
        return "I'm sorry sir, the AI service is not configured properly."
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "openai/gpt-oss-20b:free",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, a virtual assistant. "
                        "You must be polite, professional, formal, and precise in your responses. "
                        "Always follow the user's instructions carefully and clearly."
                    )
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            "temperature": 0.60,
            "max_tokens": 350,
            "top_p": 0.95
        }
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        
        response.raise_for_status()
        result = response.json()
        assistant_message = result["choices"][0]["message"]["content"]
        return assistant_message.strip()
    
    except Exception as e:
        print(f"[Jarvis GPT-OSS-20B Error]: {e}")
        return "I'm sorry sir, I am currently unable to process that request."

def get_weather(location):
    """Fetches weather information for a given location."""
    say(f"Fetching weather details for {location}")
    
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
            
            weather_report = (
                f"The current temperature in {location} is {temp} degrees Celsius. "
                f"The weather is {condition}. Humidity is at {humidity} percent, "
                f"with a wind speed of {wind_speed} kilometers per hour."
            )
            
            say(weather_report)
        else:
            say("Sorry, I couldn't retrieve the weather data.")
    
    except Exception as e:
        say("There was an error fetching the weather.")
        print(f"Error fetching weather: {e}")

def take_note(text):
    """Saves text as a note with timestamp."""
    try:
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        note_filename = "jarvis_notes.txt"
        
        with open(note_filename, "a") as file:
            file.write(f"{timestamp} - {text}\n")
        
        say("I've made a note of that.")
        print(f"Note saved: {text}")
    
    except Exception as e:
        say("Sorry, I couldn't save the note.")
        print(f"Error saving note: {e}")

def get_news(query="latest"):
    """Fetches latest news headlines."""
    say(f"Fetching the latest news about {query}")
    
    try:
        top_headlines = newsapi.get_top_headlines(q=query, language='en', country='us')
        
        if top_headlines["status"] == "ok" and top_headlines["totalResults"] > 0:
            articles = top_headlines["articles"][:5]
            for i, article in enumerate(articles, start=1):
                title = article["title"]
                say(f"News {i}: {title}")
        else:
            say("Sorry, I couldn't find any recent news on that topic.")
    
    except Exception as e:
        say("There was an error fetching the news.")
        print(f"Error: {e}")

def get_ip_details():
    """Fetches public and local IP addresses."""
    try:
        public_ip = requests.get("https://api.ipify.org").text
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return public_ip, local_ip
    except Exception as e:
        return None, None

def my_location():
    """Fetches current location using IP-based geolocation."""
    try:
        response = requests.get("https://ipinfo.io/json").json()
        city = response.get("city", "Unknown")
        state = response.get("region", "Unknown")
        country = response.get("country", "Unknown")
        return city, state, country
    except Exception as e:
        return None, None, None

def take_screenshot():
    """Captures screenshot and saves it."""
    try:
        say("By what name do you want to save the screenshot?")
        name = takeCommand()
        
        if not name:
            name = f"screenshot_{int(time.time())}"
        
        save_path = os.path.join(os.getcwd(), "Screenshots")
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, f"{name}.png")
        
        img = pyautogui.screenshot()
        img.save(file_path)
        
        say(f"Screenshot saved successfully as {name}.png in the Screenshots folder.")
    
    except Exception as e:
        say("Sorry, I was unable to take a screenshot.")
        print(f"Error: {e}")

def main():
    """Main control loop for Jarvis Assistant"""
    say("Main function initialized and ready, sir.")
    
    while True:
        query = takeCommand()
        
        if not query or query.strip() == "":
            continue
        
        query = query.lower().strip()
        
        # Open Websites
        sites = [
            ["youtube", "https://www.youtube.com"],
            ["wikipedia", "https://www.wikipedia.com"],
            ["google", "https://www.google.com"],
            ["github", "https://github.com"],
            ["facebook", "https://www.facebook.com"],
            ["instagram", "https://www.instagram.com"],
            ["twitter", "https://twitter.com"],
            ["linkedin", "https://www.linkedin.com"],
            ["reddit", "https://www.reddit.com"],
            ["netflix", "https://www.netflix.com"],
            ["amazon", "https://www.amazon.com"],
            ["gmail", "https://mail.google.com"],
            ["stackoverflow", "https://stackoverflow.com"],
            ["discord", "https://discord.com"],
            ["spotify", "https://www.spotify.com"],
            ["slack", "https://slack.com"],
            ["zoom", "https://zoom.us"],
            ["quora", "https://www.quora.com"],
            ["yahoo", "https://www.yahoo.com"],
            ["bing", "https://www.bing.com"],
            ["duckduckgo", "https://duckduckgo.com"],
            ["pinterest", "https://www.pinterest.com"],
            ["twitch", "https://www.twitch.tv"],
            ["ebay", "https://www.ebay.com"],
            ["imdb", "https://www.imdb.com"],
            ["medium", "https://medium.com"],
            ["tumblr", "https://www.tumblr.com"],
            ["wordpress", "https://wordpress.com"],
            ["salesforce", "https://www.salesforce.com"],
            ["adobe", "https://www.adobe.com"],
            ["canva", "https://www.canva.com"],
            ["dropbox", "https://www.dropbox.com"],
            ["trello", "https://trello.com"],
            ["notion", "https://www.notion.so"],
            ["airtable", "https://airtable.com"],
            ["asana", "https://asana.com"],
            ["hubspot", "https://www.hubspot.com"],
            ["bitbucket", "https://bitbucket.org"],
            ["heroku", "https://www.heroku.com"],
            ["digitalocean", "https://www.digitalocean.com"],
            ["netlify", "https://www.netlify.com"],
            ["vercel", "https://vercel.com"],
            ["glitch", "https://glitch.com"],
            ["codepen", "https://codepen.io"],
            ["jsfiddle", "https://jsfiddle.net"],
            ["replit", "https://replit.com"],
            ["codecademy", "https://www.codecademy.com"],
            ["coursera", "https://www.coursera.org"],
            ["edx", "https://www.edx.org"],
            ["udemy", "https://www.udemy.com"],
            ["khan academy", "https://www.khanacademy.org"],
            ["lynda", "https://www.lynda.com"],
            ["skillshare", "https://www.skillshare.com"],
            ["pluralsight", "https://www.pluralsight.com"],
            ["treehouse", "https://teamtreehouse.com"],
            ["udacity", "https://www.udacity.com"],
            ["futurelearn", "https://www.futurelearn.com"],
            ["alison", "https://alison.com"],
            ["openlearn", "https://www.open.edu/openlearn/"],
            ["saylor academy", "https://www.saylor.org"],
            ["academic earth", "https://academicearth.org"],
            ["mit opencourseware", "https://ocw.mit.edu"],
            ["stanford online", "https://online.stanford.edu"],
            ["harvard online learning", "https://online-learning.harvard.edu"],
            ["yale open courses", "http://oyc.yale.edu"],
            ["princeton open courseware", "https://ocw.princeton.edu"],
            ["caltech open courseware", "http://ocw.caltech.edu"],
            ["berkeley open courseware", "https://bcourses.berkeley.edu/courses/1497516/pages/berkeley-open-course-library"],
            ["oxford podcasts", "http://podcasts.ox.ac.uk"],
            ["cambridge podcasts", "http://www.cam.ac.uk/research/news/podcasts"],
            ["bbc", "https://www.bbc.com"],
            ["cnn", "https://www.cnn.com"],
            ["the verge", "https://www.theverge.com"],
            ["techcrunch", "https://techcrunch.com"],
            ["wired", "https://www.wired.com"],
            ["engadget", "https://www.engadget.com"],
            ["mashable", "https://mashable.com"],
            ["gizmodo", "https://gizmodo.com"],
            ["arstechnica", "https://arstechnica.com"],
            ["thenextweb", "https://thenextweb.com"],
            ["digital trends", "https://www.digitaltrends.com"],
            ["lifehacker", "https://lifehacker.com"],
            ["howtogeek", "https://www.howtogeek.com"],
            ["makeuseof", "https://www.makeuseof.com"],
            ["9to5mac", "https://9to5mac.com"],
            ["9to5google", "https://9to5google.com"],
            ["appleinsider", "https://appleinsider.com"],
            ["android authority", "https://www.androidauthority.com"],
            ["xda developers", "https://www.xda-developers.com"],
            ["the next web", "https://thenextweb.com"],
            ["venturebeat", "https://venturebeat.com"],
            ["recode", "https://www.vox.com/recode"],
            ["the information", "https://www.theinformation.com"],
            ["bloomberg", "https://www.bloomberg.com"],
            ["forbes", "https://www.forbes.com"],
            ["business insider", "https://www.businessinsider.com"],
            ["the wall street journal", "https://www.wsj.com"],
            ["the economist", "https://www.economist.com"],
            ["financial times", "https://www.ft.com"],
            ["marketwatch", "https://www.marketwatch.com"],
            ["cnbc", "https://www.cnbc.com"],
            ["nasdaq", "https://www.nasdaq.com"],
            ["yahoo finance", "https://finance.yahoo.com"],
            ["investopedia", "https://www.investopedia.com"],
            ["morningstar", "https://www.morningstar.com"],
            ["seeking alpha", "https://seekingalpha.com"],
            ["the motley fool", "https://www.fool.com"],
            ["zerodha varsity", "https://zerodha.com/varsity/"],
            ["tradingview", "https://www.tradingview.com"],
            ["etoro", "https://www.etoro.com"],
            ["robinhood", "https://robinhood.com"],
            ["coinbase", "https://www.coinbase.com"],
            ["binance", "https://www.binance.com"],
            ["kraken", "https://r.kraken.com/c/2223866/687155/10583"],
            ["bitfinex", "https://www.bitfinex.com"],
            ["bitstamp", "https://www.bitstamp.net"],
            ["gemini", "https://gemini.com"],
            ["blockfi", "https://blockfi.com"],
            ["crypto com", "https://crypto.com"],
            ["ledger", "https://www.ledger.com"],
            ["trezor", "https://trezor.io"],
            ["metamask", "https://metamask.io"],
            ["trust wallet", "https://trustwallet.com"],
            ["brave", "https://brave.com"],
            ["opera", "https://www.opera.com"],
            ["firefox", "https://www.mozilla.org/en-US/firefox/new/"],
            ["chrome", "https://www.google.com/chrome/"],
            ["edge", "https://www.microsoft.com/edge"],
            ["vivaldi", "https://vivaldi.com"],
            ["tor browser", "https://www.torproject.org/download/"],
            ["slack", "https://slack.com"],
            ["discord", "https://discord.com"],
            ["teams", "https://www.microsoft.com/en/microsoft-teams/group-chat-software"],
            ["zoom", "https://zoom.us"],
            ["skype", "https://www.skype.com"],
            ["whatsapp web", "https://web.whatsapp.com"],
            ["telegram web", "https://web.telegram.org"],
            ["signal", "https://signal.org"],
            ["line", "https://line.me/en/"],
            ["wechat", "https://www.wechat.com/en/"],
            ["viber", "https://www.viber.com/en/"],
            ["kik", "https://www.kik.com"],
            ["snapchat", "https://www.snapchat.com"],
            ["tiktok", "https://www.tiktok.com"],
            ["clubhouse", "https://www.joinclubhouse.com"],
            ["patreon", "https://www.patreon.com"],
            ["substack", "https://substack.com"],
            ["gumroad", "https://gumroad.com"],
            ["etsy", "https://www.etsy.com"],
            ["shopify", "https://www.shopify.com"],
            ["walmart", "https://www.walmart.com"],
            ["target", "https://www.target.com"],
            ["costco", "https://www.costco.com"],
            ["best buy", "https://www.bestbuy.com"],
            ["home depot", "https://www.homedepot.com"],
            ["lowe's", "https://www.lowes.com"],
            ["ikea", "https://www.ikea.com"],
            ["wayfair", "https://www.wayfair.com"],
            ["overstock", "https://www.overstock.com"],
            ["zillow", "https://www.zillow.com"],
            ["realtor", "https://www.realtor.com"],
            ["redfin", "https://www.redfin.com"],
            ["trulia", "https://www.trulia.com"],
            ["airbnb", "https://www.airbnb.com"],
            ["booking.com", "https://www.booking.com"],
            ["expedia", "https://www.expedia.com"],
            ["tripadvisor", "https://www.tripadvisor.com"],
            ["uber", "https://www.uber.com"],
            ["lyft", "https://www.lyft.com"],
            ["grubhub", "https://www.grubhub.com"],
            ["doordash", "https://www.doordash.com"],
            ["ubereats", "https://www.ubereats.com"],
            ["postmates", "https://postmates.com"],
            ["instacart", "https://www.instacart.com"],
            ["robinhood", "https://robinhood.com"],
            ["fidelity", "https://www.fidelity.com"],
            ["schwab", "https://www.schwab.com"],
            ["vanguard", "https://investor.vanguard.com"],
            ["td ameritrade", "https://www.tdameritrade.com"],
            ["e trade", "https://us.etrade.com/home"],
            ["ally invest", "https://www.ally.com/invest/"],
            ["interactive brokers", "https://www.interactivebrokers.com"],
            ["merrill edge", "https://www.merrilledge.com"],
            ["charles schwab", "https://www.schwab.com"],
            ["jpmorgan chase", "https://www.chase.com"],
            ["bank of america", "https://www.bankofamerica.com"],
            ["wells fargo", "https://www.wellsfargo.com"],
            ["citibank", "https://www.citi.com"],
            ["us bank", "https://www.usbank.com"],
            ["pnc bank", "https://www.pnc.com"],
            ["capital one", "https://www.capitalone.com"],
            ["td bank", "https://www.td.com"],
            ["bb&t", "https://www.bbt.com"],
            ["suntrust", "https://www.suntrust.com"],
            ["ally bank", "https://www.ally.com"],
            ["discover bank", "https://www.discover.com"],
            ["synchrony bank", "https://www.synchronybank.com"],
            ["american express", "https://www.americanexpress.com"],
            ["chase bank", "https://www.chase.com"],
            ["barclays", "https://www.barclays.co.uk"],
            ["hsbc", "https://www.hsbc.co.uk"],
            ["lloyds bank", "https://www.lloydsbank.com"],
            ["natwest", "https://www.natwest.com"],
            ["rbs", "https://www.rbs.co.uk"],
            ["santander", "https://www.santander.co.uk"],
            ["standard chartered", "https://www.sc.com"],
            ["ubs", "https://www.ubs.com"],
            ["credit suisse", "https://www.credit-suisse.com"],
            ["deutsche bank", "https://www.db.com"],
            ["ing", "https://www.ing.com"],
            ["bbva", "https://www.bbva.com"],
            ["societe generale", "https://www.societegenerale.com"],
            ["uni credit", "https://www.unicreditgroup.eu/en.html"],
            ["intesa sanpaolo", "https://www.intesasanpaolo.com"],
            ["caixa bank", "https://www.caixabank.com"],
            ["abn amro", "https://www.abnamro.com"],
            ["rabobank", "https://www.rabobank.com"],
            ["kbc bank", "https://www.kbc.com"],
            ["bnp paribas", "https://group.bnpparibas"],
            ["credit agricole", "https://www.credit-agricole.com"],
            ["natixis", "https://www.natixis.com"],
            ["societe generale", "https://www.societegenerale.com"],
            ["allianz", "https://www.allianz.com"],
            ["axa", "https://www.axa.com"],
            ["zurich insurance", "https://www.zurich.com"],
            ["metlife", "https://www.metlife.com"],
            ["prudential", "https://www.prudential.com"],
            ["aig", "https://www.aig.com"],
            ["chubb", "https://www.chubb.com"],
            ["travelers", "https://www.travelers.com"],
            ["liberty mutual", "https://www.libertymutual.com"],
            ["progressive", "https://www.progressive.com"],
            ["geico", "https://www.geico.com"],
            ["state farm", "https://www.statefarm.com"],
            ["farmers insurance", "https://www.farmers.com"],
            ["nationwide", "https://www.nationwide.com"],
            ["allstate", "https://www.allstate.com"],
            ["esurance", "https://www.esurance.com"],
            ["the general", "https://thegeneral.com"],
            ["direct line", "https://www.directline.com"],
            ["aviva", "https://www.aviva.com"],
            ["legal & general", "https://www.legalandgeneral.com"],
            ["prudential uk", "https://www.pru.co.uk"],
            ["hiscox", "https://www.hiscox.co.uk"],
            ["bupa", "https://www.bupa.com"],
            ["aetna", "https://www.aetna.com"],
            ["cigna", "https://www.cigna.com"],
            ["anthem", "https://www.anthem.com"],
            ["humana", "https://www.humana.com"],
            ["kaiser permanente", "https://healthy.kaiserpermanente.org"],
            ["centene", "https://www.centene.com"],
            ["mckesson", "https://www.mckesson.com"],
            ["cardinal health", "https://www.cardinalhealth.com"],
            ["amerisourcebergen", "https://www.amerisourcebergen.com"],
            ["walgreens boots alliance", "https://www.walgreensbootsalliance.com"],
            ["cvs health", "https://www.cvshealth.com"],
            ["rite aid", "https://www.riteaid.com"],
            ["express scripts", "https://www.express-scripts.com"],
            ["optumrx", "https://www.optumrx.com"],
            ["humana pharmacy solutions", "https://pharmacysolutions.humana.com"],
        ]
        
        site_opened = False
        for site in sites:
            if f"open {site[0]}" in query:
                say(f"Opening {site[0]}, sir.")
                webbrowser.open(site[1])
                site_opened = True
                break
        
        if site_opened:
            continue
        
        # Commands
        if "hi jarvis" in query or "hello jarvis" in query:
            say("Good day, sir. How may I assist you?")
        
        elif "who are you" in query or "introduce yourself" in query:
            say("I am Jarvis, your personal virtual assistant — designed to serve you with precision and courtesy, sir.")
        
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
        
        elif "ip address" in query:
            public_ip, local_ip = get_ip_details()
            if public_ip or local_ip:
                say(f"Sir, your public IP is {public_ip}, and your local IP is {local_ip}.")
            else:
                say("Apologies sir, I couldn't retrieve your IP addresses.")
        
        elif "where am i" in query or "current location" in query:
            city, state, country = my_location()
            if city and state and country:
                say(f"Sir, you are currently in {city}, {state}, {country}.")
            else:
                say("I'm sorry sir, I couldn't detect your current location.")
        
        elif "take screenshot" in query:
            take_screenshot()
        
        elif "make a note" in query or "take a note" in query:
            say("What should I note down, sir?")
            note_text = takeCommand()
            if note_text:
                take_note(note_text)
        
        elif "quit" in query or "stop" in query or "exit" in query:
            say("Shutting down systems. Have a great day, sir.")
            break
        
        else:
            # Fallback to GPT
            print("Command not recognized. Asking GPT-OSS-20B...")
            response = chat_with_gpt_oss_20b(query)
            if response:
                say(response)

if __name__ == '__main__':
    startup()

    main()
