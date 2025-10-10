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
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# ------------------ GLOBAL FLAGS ------------------ #
active = False  # Whether Turing is active
running = True  # Whether Turing  should keep listening

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
        print(f"\n🧠 Turing: {text}\n")
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
    say(f"{greeting}, sir. The current time is {c_time}. Turing is online and fully operational.")
    print("\n🎧 Passive listening mode started — say 'Turing' to wake me up.\n")

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
    say("Turing online and ready, sir.")
    
    # Predefined website shortcuts
    sites =[
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
    
    while active:
        query = takeCommand()
        if not query:
            continue

        # Deactivation hotwords
        if any(kw in query for kw in ["thank you Turing", "go to idle Turing", "sleep Turing"]):
            say("Understood, sir. Going to standby mode.")
            active = False
            break

        # Shutdown hotwords
        if any(kw in query for kw in ["stop Turing", "shutdown Turing", "exit", "quit"]):
            say("Understood, sir. Shutting down completely.")
            active = False
            running = False
            break

        # --- Website Shortcut Handling ---
        site_opened = False
        for site in sites:
            if f"open {site[0]}" in query:
                say(f"Opening {site[0]}, sir.")
                webbrowser.open(site[1])
                site_opened = True
                break
        if site_opened:
            continue

        # --- Other Commands ---
        if "hi Turing" in query or "hello Turing" in query:
            say("Good day, sir. How may I assist you?")
        elif "who are you" in query or "introduce yourself" in query:
            say("I am Turing, your personal AI assistant — designed to serve you with precision and courtesy, sir.")
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
        print("🎧 Turing is passively listening... (say 'Turing' to activate)")
        while running:
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                phrase = recognizer.recognize_google(audio, language="en-GB").lower()
                if "Turing" in phrase and not active:
                    active = True
                    say("Yes sir?")
                    main_active_loop()
                elif any(word in phrase for word in ["stop Turing", "shutdown Turing"]):
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
    if not OPEN_API_KEY:
        return "I'm sorry sir, the AI service is not configured properly."

    headers = {
        "Authorization": f"Bearer {OPEN_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Turing, a polite, intelligent, British AI assistant. "
                    "Always address the user as 'sir' and respond formally but naturally."
                ),
            },
            {"role": "user", "content": user_query},
        ],
        "temperature": 0.6,
        "max_tokens": 300,
    }

    try:
        response = requests.post("OPEN",
                                 headers=headers, data=json.dumps(payload), timeout=20)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e1:
        print(f"[GPT-OSS Error]: {e1}")
        try:
            payload["model"] = "mistralai/mistral-7b-instruct:free"
            response = requests.post("OPEN",
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
        say("Turing offline. Goodbye, sir.")

if __name__ == '__main__':
    main()
