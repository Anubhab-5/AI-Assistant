# Import required libraries
from AppOpener import close, open as appopen  # Open and close applications
from webbrowser import open as webopen  # Open URLs in a web browser
from pywhatkit import search, playonyt  # Google search and YouTube playback
from dotenv import dotenv_values  # Manage environment variables
from bs4 import BeautifulSoup  # Parse HTML content
from rich import print  # Styled console output
from groq import Groq  # AI chatbot functionalities
import webbrowser  # Open URLs
import subprocess  # Run system commands
import requests  # Make HTTP requests
import keyboard  # Handle keyboard actions
import asyncio  # Asynchronous programming
import os  # OS-level functionalities

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")  # Retrieve Groq API key

# Define user-agent for web requests
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq AI client
client = Groq(api_key=GroqAPIKey)

# Predefined responses
professional_responses = [
    "Your satisfaction is my priority. Let me know if you need more help!",
    "I'm here for any additional queries or support. Feel free to ask."
]

# Chatbot messages storage
messages = []

# System message for AI chatbot
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'Assistant')}. You're an experienced content writer for generating text-based content."}]

# Function to perform a Google search
def GoogleSearch(Topic):
    search(Topic)
    return True

# Function to generate AI content and save it to a file
def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(['notepad.exe', File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768", messages=SystemChatBot + messages, max_tokens=2048, temperature=0.7, stream=True
        )
        Answer = "".join(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)
        messages.append({"role": "assistant", "content": Answer})
        return Answer.replace("</s>", "")

    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)
    file_path = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    OpenNotepad(file_path)
    return True

# Function to search on YouTube
def YouTubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={Topic}")
    return True

# Function to play a YouTube video
def PlayYoutube(query):
    playonyt(query)
    return True

# Function to open an application or a related webpage
def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            return [link.get('href') for link in BeautifulSoup(html, 'html.parser').find_all('a', {'jsname': 'UWckNb'})]

        def search_google(query):
            response = sess.get(f"https://www.google.com/search?q={query}", headers={"User-Agent": useragent})
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            webopen(extract_links(html)[0])
        return True

# Function to close an application
def CloseApp(app):
    if "chrome" not in app:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

# Function to execute system-level commands
def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
        "lock": lambda: keyboard.press_and_release("win + l")
    }
    for key, action in actions.items():
        if command.lower() in key:
            action()
            return True
    return False

# Asynchronous function to translate and execute user commands
async def TranslateAndExecute(commands: list[str]):
    tasks = []
    mapping = {
        "open ": OpenApp,
        "close ": CloseApp,
        "play ": PlayYoutube,
        "content ": Content,
        "google search ": GoogleSearch,
        "youtube search ": YouTubeSearch,
        "system ": System
    }
    
    for command in commands:
        for prefix, func in mapping.items():
            if command.startswith(prefix):
                tasks.append(asyncio.to_thread(func, command.removeprefix(prefix)))
                break
        else:
            print(f"No function found for: {command}")
    
    results = await asyncio.gather(*tasks)
    for result in results:
        yield result

# Asynchronous function to automate command execution
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
