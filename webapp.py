import gradio as gr
import requests
import os
from pydub import AudioSegment
from api import AUTHORIZATION, X_USER_ID

# Function to save audio content to a WAV file without metadata
def save_audio_to_wav(audio_url, output_file_path):
    response = requests.get(audio_url)
    with open(output_file_path, "wb") as f:
        f.write(response.content)

# Function to convert text to speech and save the audio file
def text_to_speech(title, text):
    url = "https://play.ht/api/v1/convert"
    payload = {
        "content": [text],
        "voice": "en-US-JennyNeural",
        "transcriptionId": "-NaIQlUGAcyixhyoaSgn",
        "title": "API-audio"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "AUTHORIZATION": AUTHORIZATION,
        "X-USER-ID": X_USER_ID
    }

    response = requests.post(url, json=payload, headers=headers)
    link = response.json()["audioUrl"]

    # Save the audio file as a WAV file with the specified title
    output_file_path = os.path.join("./input", f"{title}.wav")
    save_audio_to_wav(link, output_file_path)

    return output_file_path

# Function to play the audio file
def play_audio(title):
    # Load the audio file
    audio_path = os.path.join("./input", f"{title}.wav")
    audio = AudioSegment.from_wav(audio_path)

    # Play the audio
    audio.play()

# Gradio Interface for text-to-speech conversion
iface_tts = gr.Interface(
    fn=text_to_speech,
    inputs=["title", "text"],
    outputs="text",
    live=True,
    capture_session=True,  # To allow file saving and playback in the same session
)

# Gradio Interface for playing the audio
iface_audio_playback = gr.Interface(
    fn=play_audio,
    inputs="text",
    outputs=None,
    live=True,
)

# Combine the interfaces and launch the app
gr.Interface([iface_tts, iface_audio_playback], layout="horizontal").launch()
