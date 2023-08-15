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
def url(title):
    transcription_id = load_trans_id("./temp/trans_id.txt")
    response = requests.get(f"https://play.ht/api/v1/articleStatus?transcriptionId={transcription_id}", headers=headers)
    audio_url = response.json()["audioUrl"]
    output_text = f"Link to the media file: {audio_url}"

    # Download the audio file from the URL and save it to the './input' folder
    input_folder = "./input"
    os.makedirs(input_folder, exist_ok=True)
    audio_file_path = os.path.join(input_folder, title + ".wav")

    with requests.get(audio_url, stream=True) as response:
        response.raise_for_status()
        with open(audio_file_path, "wb") as audio_file:
            for chunk in response.iter_content(chunk_size=8192):
                audio_file.write(chunk)

    return output_text, audio_file_path

def load_from_excel(filename):
    return pd.read_excel(filename)

def get_voice_index():
    if 'voice_index' not in st.session_state:
        st.session_state.voice_index = 0
    return st.session_state.voice_index

# Streamlit app
def main():
    st.title("Text-to-Speech API")

    excel_favourites = "./temp/favourites.xlsx"

    title = st.text_input("Project name", "API-audio")
    df = load_from_excel(excel_favourites)


    #Create a voiceID
    df["voiceID"] = df["value"] + " - " + df["name"] + " - " + df["languageCode"] + " - " + df["gender"]




    with st.expander("Voice Samples List", expanded = True):

        col1, col2 = st.columns(2)

        with col1:
            # Create a multiselect box for filtering voices by gender
            selected_genders = st.multiselect("Filter by Gender", df["gender"].unique(), ['Male', 'Female'])
        with col2:
            # Create a multiselect box for filtering voices by language code
            selected_language_codes = st.multiselect("Filter by Language Code", df["languageCode"].unique())

        # Filter the DataFrame based on the selected language codes and genders
        filtered_df = df[
            (df["languageCode"].isin(selected_language_codes)) & (df["gender"].isin(selected_genders))
        ] if (selected_language_codes and selected_genders) else df



        columns_to_select = ['languageCode', 'name', 'gender', 'voiceType', 'service', 'isKid', 'value']
        visualize_df = filtered_df[columns_to_select]
        st.data_editor(visualize_df)


    # Initialize a session state to keep track of the selected index
    if 'voice_index' not in st.session_state:
        st.session_state.voice_index = 0



    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("Select a voice", expanded = True):
            # Voice selection with both voice name, languageCode, and gender
            selected_voiceID = st.selectbox("", filtered_df['voiceID'], index=st.session_state.voice_index)
        

    # Extract the voice value (without languageCode and gender) from the selected option
    voice = selected_voiceID.split(" - ")[0]


    # Get the value of the "sample" column for the selected voice
    selected_voice = df.loc[df["value"] == voice, "sample"].values[0]

    with col2:
        with st.expander("Audio Sample", expanded = True):
            # Display the "sample" value for the selected voice
            st.audio(selected_voice)



    # Text input
    text = st.text_area("Enter your text here", "Madonna tacchina!!")


    tts_button = st.button("TTS", type="primary", use_container_width=True)
    refresh_button = st.button("Refresh", use_container_width=True)
    
    # Button for TTS
    if tts_button:
        output_text = tts(text, title, voice)
        output_text, audio_file_path = url(title)
        st.write(output_text)

        # Display the audio file
        st.audio(audio_file_path)

    # Button for Download and Play
    if refresh_button:
        output_text, audio_file_path = url(title)
        st.write(output_text)

        # Display the audio file
        st.audio(audio_file_path)


if __name__ == "__main__":
    main()