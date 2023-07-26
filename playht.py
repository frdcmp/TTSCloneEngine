import streamlit as st
import requests
import os
from pydub import AudioSegment
from api import AUTHORIZATION, X_USER_ID

# Function to save audio content to a WAV file without metadata
def save_audio_to_wav(audio_url, output_file_path):
    response = requests.get(audio_url)
    with open(output_file_path, "wb") as f:
        f.write(response.content)

# Streamlit app code
st.title("Text to Speech Conversion")

# Text to be converted to speech
title = st.text_input("Enter a name for the audio file:", value="API-audio")
text = st.text_input("Enter your text here:", value="Hi! I am a cool robot")


if st.button("TTS"):

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

    print(response.text)

if st.button("Saveand play the audio file"):
    url = "https://play.ht/api/v1/articleStatus?transcriptionId=-NaIQlUGAcyixhyoaSgn"

    headers = {
        "accept": "application/json",
        "AUTHORIZATION": AUTHORIZATION,
        "X-USER-ID": X_USER_ID
    }

    response = requests.get(url, headers=headers)

    print(response.text)
    
    link = response.json()["audioUrl"]
    st.audio(link)

    # Save the audio file at the location ./input as a WAV file, with the name of the title
    output_file_path = os.path.join("./input", f"{title}.wav")
    save_audio_to_wav(link, output_file_path)
    st.success(f"Audio file saved at {output_file_path}")