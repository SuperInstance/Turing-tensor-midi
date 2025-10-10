
# 🤖 Turing - AI Voice Assistant

> A sophisticated, JARVIS-inspired voice assistant with passive listening, natural language processing, and a British accent.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Specialties

**Turing** stands out with its unique combination of features that create a truly immersive AI assistant experience:

- **🎙️ Passive Wake Word Detection** - Always listening in the background, activates when you say "Turing"
- **🇬🇧 British Voice Personality** - Sophisticated British accent with formal, polite responses addressing you as "sir"
- **🧠 Dual-Mode Operation** - Seamlessly switches between passive listening and active command processing
- **🔄 AI System** - Uses AI model (GPT-OSS-20B) for reliability
- **📍 200+ Pre-configured Website Shortcuts** - Instant access to popular sites, educational platforms, and services
- **🌐 Real-time Information** - Live weather, news, and web search capabilities

## 🚀 Features

### Core Functionality
- ✅ **Voice Recognition** - Hands-free control using Google Speech Recognition
- ✅ **Text-to-Speech** - Natural voice responses with pyttsx3
- ✅ **Conversational AI** - Context-aware responses using OpenRouter API
- ✅ **Web Automation** - Open websites, search Google, play YouTube videos
- ✅ **News Integration** - Fetch latest headlines on any topic via NewsAPI
- ✅ **Weather Reports** - Real-time weather data for any location
- ✅ **Smart Wake/Sleep** - Energy-efficient passive listening mode

### Command Examples
```
"Turing" - Wake up the assistant
"Open YouTube" - Opens YouTube in browser
"What's the weather in London?" - Get weather report
"Play Interstellar soundtrack on YouTube" - Plays video
"News about technology" - Fetch tech news
"Search for Python tutorials" - Google search
"What's the time?" - Current time
"Thank you Turing" - Put assistant to sleep
"Shutdown Turing" - Complete shutdown
```

## 📋 Prerequisites

- **Python 3.8+**
- **Microphone** (for voice input)
- **Internet Connection** (for API calls and web search)
- **API Keys** (see configuration below)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/turing-voice-assistant.git
cd turing-voice-assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
```
speech_recognition
pyttsx3
requests
pywhatkit
newsapi-python
geopy
python-dotenv
pyaudio  # May require system-level installation
```

**For PyAudio installation issues:**
- **Windows**: `pip install pipwin && pipwin install pyaudio`
- **Linux**: `sudo apt-get install portaudio19-dev python3-pyaudio`
- **macOS**: `brew install portaudio && pip install pyaudio`

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API Key (for AI responses)
OPEN_API_KEY=your_openai_api_key_here

# NewsAPI Key (for news fetching)
NEWS_API_KEY=your_newsapi_key_here

# Visual Crossing Weather API Key
WEATHER_API_KEY=your_weather_api_key_here
```

### 4. Obtain API Keys

#### OpenRouter API (Required for AI Chat)
1. Visit [Openai.com](https://platform.openai.com/api-keys)
2. Sign up and navigate to API Keys
3. Create a new API key
4. Add credits to your account (pay-as-you-go)

#### NewsAPI (Required for News)
1. Visit [NewsAPI.org](https://newsapi.org/)
2. Register for a free account
3. Copy your API key from the dashboard

#### Visual Crossing Weather API (Required for Weather)
1. Visit [Visual Crossing Weather](https://www.visualcrossing.com/weather-api)
2. Sign up for a free account (1000 requests/day)
3. Copy your API key

## 🎮 Usage

### Basic Usage
```bash
python turing_assistant.py
```

The assistant will:
1. Initialize and greet you
2. Enter passive listening mode
3. Wait for the wake word "Turing"
4. Execute your commands
5. Return to passive mode after "Thank you Turing"

### Voice Commands Cheat Sheet

| Command | Action |
|---------|--------|
| `"Turing"` | Activate assistant |
| `"Open [website]"` | Open predefined website |
| `"Search for [query]"` | Google search |
| `"Play [video] on YouTube"` | Play YouTube video |
| `"What's the weather in [city]?"` | Get weather report |
| `"News about [topic]"` | Fetch news headlines |
| `"What's the time?"` | Current time |
| `"Who are you?"` | Assistant introduction |
| `"Thank you Turing"` | Sleep mode |
| `"Shutdown Turing"` | Complete shutdown |

## ⚙️ Configuration

### Customizing Voice Settings

Edit the `init_engine()` function:
```python
engine.setProperty('rate', 165)  # Speech rate (150-200)
engine.setProperty('volume', 1.0)  # Volume (0.0-1.0)
```

### Adding Custom Websites

Add to the `sites` list in `main_active_loop()`:
```python
sites.append(["mysite", "https://www.mywebsite.com"])
```

Then use: `"Open mysite"`

### Changing AI Model

Modify the `chat_with_gpt_oss_20b()` function:
```python
payload = {
    "model": "openai/gpt-4-turbo",  # Change model here
    "messages": [...],
    "temperature": 0.7,  # Adjust creativity (0.0-1.0)
    "max_tokens": 500,   # Adjust response length
}
```

### Adjusting Recognition Timeout

In `takeCommand()`:
```python
audio = r.listen(source, timeout=8, phrase_time_limit=10)
```

## 🏗️ Project Structure

```
turing-voice-assistant/
│
├── turing_assistant.py    # Main application file
├── .env                    # Environment variables (not in repo)
├── .env.example            # Example environment file
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── LICENSE                # MIT License
```

## 🐛 Troubleshooting

### Microphone Not Detected
```bash
# Test microphone
python -m speech_recognition
```

### TTS Not Working
The assistant automatically falls back to PowerShell TTS on Windows if pyttsx3 fails.

### API Errors
- Verify API keys in `.env` file
- Check API quota/credits
- Ensure stable internet connection

### Recognition Accuracy
- Speak clearly and at moderate pace
- Reduce background noise
- Adjust microphone sensitivity in system settings

## 📜 License

This project is licensed under the **MIT License** - see below for details:

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Inspired by JARVIS from Iron Man
- Built with [SpeechRecognition](https://github.com/Uberi/speech_recognition)
- Powered by [OpenAI](https://platform.openai.com/api-keys)
- Weather data from [Visual Crossing](https://www.visualcrossing.com/)
- News from [NewsAPI](https://newsapi.org/)

## 📞 Support

If you encounter any issues or have questions:
- Open an [Issue](https://github.com/yourusername/turing-voice-assistant/issues)
- Check existing issues for solutions
- Review the troubleshooting section above

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ by ROCKY**

*"Turing online and ready, sir."*
