import os
import streamlit as st
import requests
from api import AUTHORIZATION, X_USER_ID

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "AUTHORIZATION": AUTHORIZATION,
    "X-USER-ID": X_USER_ID
}

def read_transcription_id_from_file(filename):
    try:
        with open(filename, "r") as file:
            transcription_id = file.read().strip()
            return transcription_id
    except FileNotFoundError:
        return ""


def tts(text, title, voice, transcription_id):
    url = "https://play.ht/api/v1/convert"

    payload = {
        "content": [text],
        "voice": voice,
        "transcriptionId": transcription_id,
        "title": title
    }

    response = requests.post(url, json=payload, headers=headers)
    transcription_id = response.json()["transcriptionId"]
    return transcription_id


def save_audio_to_file(link, title):
    try:
        os.makedirs("./input", exist_ok=True)
        response = requests.get(link)
        if response.status_code == 200:
            filename = f"./input/{title}.mp3"  # Assuming the audio format is MP3
            with open(filename, "wb") as file:
                file.write(response.content)
            return filename
        else:
            return None
    except Exception as e:
        st.error(f"Error while saving audio file: {e}")
        return None


# Text to be converted to speech
text = st.text_input("Enter your text here:", value="Hi! I am a cool robot")
title = st.text_input("Enter a name for the audio file:", value="API-audio")
voice = st.text_input("Enter your voice here:", value="en-US-JennyNeural")


def main():

    transcription_id = read_transcription_id_from_file("trans_id.txt")

    if st.button("TTS"):
        # Call the tts function and update the transcription_id in session state
        transcription_id = tts(text, title, voice, transcription_id)
        print(transcription_id)
        response = requests.get(f"https://play.ht/api/v1/articleStatus?transcriptionId={transcription_id}", headers=headers)
        link = response.json()["audioUrl"]

        saved_filename = save_audio_to_file(link, title)
        if saved_filename:
            st.success(f"Audio file saved: {saved_filename}")
            st.audio(saved_filename)
        else:
            st.error("Failed to save audio file.")

if __name__ == "__main__":
    main()