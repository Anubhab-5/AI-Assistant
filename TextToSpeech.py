import asyncio
import pygame
import edge_tts
import os
import random
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US")

# ✅ Initialize pygame mixer only once
def init_audio():
    if not pygame.mixer.get_init():
        pygame.mixer.init()

# ✅ Asynchronous function to generate and save speech
async def TextToAudioFile(text):
    file_path = "Data/speech.mp3"

    if os.path.exists(file_path):
        os.remove(file_path)

    communicate = edge_tts.Communicate(text, AssistantVoice, pitch="+5Hz", rate="+11%")
    await communicate.save(file_path)

# ✅ Function to play the generated speech file
def PlayAudio():
    try:
        init_audio()
        pygame.mixer.music.load("Data/speech.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error in PlayAudio: {e}")

    finally:
        pygame.mixer.quit()

# ✅ Function to manage TTS execution safely
def TTS(Text):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(TextToAudioFile(Text))  # ✅ Non-blocking execution
    else:
        asyncio.run(TextToAudioFile(Text))  # ✅ Runs if no active event loop
    PlayAudio()

# ✅ Function to manage long text responses
def TextToSpeech(Text):
    Data = str(Text).split(".")

    responses = [
        "The rest of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "You’ll find more details on the chat screen, sir."
    ]

    if len(Data) > 4 and len(Text) >= 300:
        TTS(". ".join(Data[:2]) + ". " + random.choice(responses))
    else:
        TTS(Text)

# ✅ Testing the TTS function
if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the text: "))
