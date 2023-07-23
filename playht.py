import streamlit as st
import requests
import os
from pydub import AudioSegment

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

# Check if the transcription_id has been set or not
transcription_id = ""


# Create the request payload
payload = {
    "content": [text],
    "voice": "en-US-JennyNeural",
    "title": title,
    "transcriptionId": transcription_id
}

# Make the request to the Play.ht API
url = "https://play.ht/api/v1/convert"
headers = {
    "accept": "application/json",
    "Authorization": "",
    "X-USER-ID": ""
}

if st.button("Convert to Speech"):
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()

    # Retrieve the transcription ID from the response_data if it's not set
    if not transcription_id:
        transcription_id = response_data.get("transcriptionId")

        # Save the transcription_id to session_state so that it persists between button clicks
        st.session_state.transcription_id = transcription_id

    response = requests.get(f"https://play.ht/api/v1/articleStatus?transcriptionId={transcription_id}", headers=headers)
    
    link = response.json()["audioUrl"]

    # Play the audio
    st.audio(link)

    # Save the audio file at the location ./input as a WAV file, with the name of the title
    output_file_path = os.path.join("./input", f"{title}.wav")
    save_audio_to_wav(link, output_file_path)

    st.success(f"Audio file saved at {output_file_path}")
