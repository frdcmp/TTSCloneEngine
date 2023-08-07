import os
import requests
import streamlit as st
import sys
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid
from st_aggrid.shared import GridUpdateMode, DataReturnMode

sys.path.append('./temp/')  # Add the './API/' directory to the module search path
from api import AUTHORIZATION, X_USER_ID
from pydub import AudioSegment

# Set Streamlit to wide mode
st.set_page_config(layout="wide")


headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "AUTHORIZATION": AUTHORIZATION,
    "X-USER-ID": X_USER_ID
}

# Function to get available voice data
def get_voice_values():
    url = "https://play.ht/api/v1/getVoices"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices_data = response.json().get("voices", [])
        return voices_data
    else:
        raise ValueError("Failed to fetch voice data from the API.")

voice_data = get_voice_values()

# Function to load transcription ID from file
def load_trans_id(filename):
    try:
        with open(filename, "r") as file:
            transcription_id = file.read().strip()
            return transcription_id
    except FileNotFoundError:
        return ""

# Function for TTS
def tts(text, title, voice):
    transcription_id = load_trans_id("./temp/trans_id.txt")
    url = "https://play.ht/api/v1/convert"
    payload = {
        "content": [text],
        "voice": voice,
        "transcriptionId": transcription_id,
        "title": title
    }
    response = requests.post(url, json=payload, headers=headers)
    transcription_id = response.json()["transcriptionId"]
    output_text = f"TTS created, the transcription ID is: {transcription_id}"
    return output_text


# Function for URL
def url():
    transcription_id = load_trans_id("./temp/trans_id.txt")
    response = requests.get(f"https://play.ht/api/v1/articleStatus?transcriptionId={transcription_id}", headers=headers)
    audio_url = response.json()["audioUrl"]
    output_text = f"Link to the media file: {audio_url}"

    # Download the audio file from the URL and save it to the './API' folder
    input_folder = "./API"
    os.makedirs(input_folder, exist_ok=True)
    audio_file_path = os.path.join(input_folder, "API-audio.mp3")

    with requests.get(audio_url, stream=True) as response:
        response.raise_for_status()
        with open(audio_file_path, "wb") as audio_file:
            for chunk in response.iter_content(chunk_size=8192):
                audio_file.write(chunk)

    return output_text, audio_file_path


def get_favorites():
    try:
        with open("./temp/favourites.txt", "r") as file:
            favorites = file.read().strip().split("\n")
            return favorites
    except FileNotFoundError:
        return []
    
# Function to save the selected voice to the "favourites.txt" file
def save_to_favorites(voiceID):
    try:
        with open("./temp/favourites.txt", "a") as file:
            file.write(voiceID + "\n")
        st.success("Voice added to favorites!")
    except Exception as e:
        st.error("Error occurred while saving the voice to favorites.")
        st.error(e)
    
# Streamlit app
def main():
    st.title("Text-to-Speech API Demo")

    # Fetch the DataFrame with voice data
    df = pd.DataFrame(voice_data)

    # Create a new column with the voice name, languageCode, and gender combined
    df["voiceID"] = df["value"] + " - " + df["languageCode"] + " - " + df["gender"]

    # Get favorited voices from the "favourites.txt" file
    favorites = get_favorites()

    tab1, tab2, tab3 = st.tabs(["Voice", "TTS", "SSML"])

    with tab1:
        st.header("Select TTS Voice")
        # Create a checkbox for "Favourites"
        show_favorites = st.checkbox("Favourites", value=False)

        col1, col2 = st.columns([1, 1])

        if show_favorites:
            # Display favorited voices in the dropdown
            selected_voice_with_lang = col1.selectbox("Select a voice", favorites)
            
        else:
            # Create a multiselect box for filtering voices by gender
            selected_genders = col1.multiselect("Filter by Gender", df["gender"].unique())

            # Create a multiselect box for filtering voices by language code
            selected_language_codes = col2.multiselect("Filter by Language Code", df["languageCode"].unique())

            # Filter the DataFrame based on the selected language codes and genders
            filtered_df = df[
                (df["languageCode"].isin(selected_language_codes)) & (df["gender"].isin(selected_genders))
            ] if (selected_language_codes and selected_genders) else df

            # Voice selection with both voice name, languageCode, and gender
            selected_voice_with_lang = st.selectbox("Select a voice", filtered_df["voiceID"])

        # Extract the voice value (without languageCode and gender) from the selected option
        voice = selected_voice_with_lang.split(" - ")[0]
        voiceID = selected_voice_with_lang
        # Get the value of the "sample" column for the selected voice
        selected_voice_sample = df.loc[df["value"] == voice, "sample"].values[0]

        # Display the "sample" value for the selected voice
        st.audio(selected_voice_sample)

        # Button to save the selected voice to favorites
        if not show_favorites:
            st.button("Save to favorites", on_click=save_to_favorites, args=(voiceID,))


    with tab2:
        # Text input
        text = st.text_area("Enter your text here", "Madonna tacchina!!")


        # Button for TTS
        if st.button("TTS", type="primary", use_container_width=True):
            output_text = tts(text, "API-audio", voice)
            st.write(output_text)
            output_text, audio_file_path = url()
            st.write(output_text)

            # Display the audio file
            st.audio(audio_file_path)

        # Button for Download and Play
        if st.button("Refresh", use_container_width=True):
            output_text, audio_file_path = url()
            st.write(output_text)

            # Display the audio file
            st.audio(audio_file_path)

    with tab3:

        # Button for SSML
        if st.button("SSML", use_container_width=True):
            output_text = ssml(text, "API-audio", voice)
            st.write(output_text)

if __name__ == "__main__":
    main()