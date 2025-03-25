import asyncio
import json
import os
import subprocess
from time import sleep
from dotenv import dotenv_values

# Import Frontend Modules
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

# Import Backend Modules
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Good to see you {Username}. I am doing well Sir. How may I help you?'''

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# ✅ Async function to handle speech recognition
async def listen_speech():
    return await asyncio.to_thread(SpeechRecognition)

# ✅ Show default chat messages if no chats exist
def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding='utf-8')
    if len(File.read()) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

# ✅ Read chat log from JSON
def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

# ✅ Format chat logs and update the UI
def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), "w", encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

# ✅ Display chats on GUI
def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
        Data = file.read()
    if len(Data) > 0:
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(Data)

# ✅ Perform initial setup tasks
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

# ✅ Async function for main execution
async def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = await listen_speech()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")

    Decision = await asyncio.to_thread(FirstLayerDMM, Query)

    print(f"\nDecision : {Decision}\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    MergedQuery = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            await asyncio.to_thread(Automation, list(Decision))
            TaskExecution = True

    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery}, True")

        try:
            TextToSpeech("Generating Images Sir..")
            process = await asyncio.create_subprocess_exec(
                'python', r'Backend\ImageGeneration.py',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            subprocesses.append(process)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
            TextToSpeech("There is some problem in ImageGeneration.py")

    if G and R:
        SetAssistantStatus("Searching...")
        Answer = await asyncio.to_thread(RealtimeSearchEngine, QueryModifier(MergedQuery))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        await asyncio.to_thread(TextToSpeech, Answer)
        return True

    for Queries in Decision:
        if "general" in Queries:
            SetAssistantStatus("Thinking...")
            QueryFinal = Query.replace("general ", "")
            Answer = await asyncio.to_thread(ChatBot, QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            await asyncio.to_thread(TextToSpeech, Answer)
            return True
        
        if "realtime" in Queries:
            SetAssistantStatus("Searching...")
            QueryFinal = Query.replace("realtime ", "")
            Answer = await asyncio.to_thread(RealtimeSearchEngine, QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            await asyncio.to_thread(TextToSpeech, Answer)
            return True
        
        if "exit" in Queries:
            QueryFinal = "Okay, Bye!"
            Answer = await asyncio.to_thread(ChatBot, QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            await asyncio.to_thread(TextToSpeech, Answer)
            os._exit(1)

# ✅ Async function to continuously listen for commands
async def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            await MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                await asyncio.sleep(0.1)
            else:
                SetAssistantStatus("Available...")

# ✅ Start GUI in an async function
async def SecondThread():
    await asyncio.to_thread(GraphicalUserInterface)

# ✅ Run the assistant asynchronously
async def main():
    asyncio.create_task(FirstThread())  
    await SecondThread()

if __name__ == "__main__":
    asyncio.run(main())
