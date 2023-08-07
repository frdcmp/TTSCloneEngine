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

def get_voice_values():
    url = "https://play.ht/api/v1/getVoices"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices_data = response.json().get("voices", [])
        return voices_data
    else:
        raise ValueError("Failed to fetch voice data from the API.")

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

def save_to_excel(voices_data, filename):
    df = pd.DataFrame(voices_data)
    df.to_excel(filename, index=False)

def load_from_excel(filename):
    return pd.read_excel(filename)

def save_to_favourites(voice_data, filename):
    df = pd.DataFrame(voice_data)
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    df = df.sort_values(by=["languageCode"]).reset_index(drop=True)  # Sort by language code
    df.to_excel(filename, index=False)

# Streamlit app
def main():
    st.title("Text-to-Speech API")

    tab1, tab2, tab3 = st.tabs(["Voice", "TTS", "SSML"])

    with tab1:

        excel_voices = "./temp/voices.xlsx"
        excel_favourites = "./temp/favourites.xlsx"


        with st.expander("API command", expanded = False):
            update_button = st.button("Update Voice List from API")

            #Update Voices Database Button
            if update_button:
                st.write("Fetching voice data from the API...")
                voice_data = get_voice_values()
                save_to_excel(voice_data, excel_voices)
                st.write("Voice list updated!")


        with st.expander("Shows favourite voices only", expanded = True):
            #FAVOURITES?
            show_favorites = st.checkbox("Favourites", value=True)
            
            if show_favorites:
                df = load_from_excel(excel_favourites)
            else:
                df = load_from_excel(excel_voices)


        #Create a voiceID
        df["voiceID"] = df["value"] + " - " + df["name"] + " - " + df["languageCode"] + " - " + df["gender"]

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


        with st.expander("Voice Samples List", expanded = True):
            columns_to_select = ['languageCode', 'name', 'gender', 'voiceType', 'service', 'isKid', 'value']
            visualize_df = filtered_df[columns_to_select]
            st.data_editor(visualize_df)


            col1, col2 = st.columns(2)
            with col1:
                # Save to Favourites Button
                save_favourites_button = st.button("Save to favourites")

            with col2:
                # Remove from Favourites Button
                remove_favourites_button = st.button("Remove from favourites")

        st.divider()

        # Voice selection with both voice name, languageCode, and gender
        selected_voiceID = st.selectbox("Select a voice", filtered_df["voiceID"])

        # Extract the voice value (without languageCode and gender) from the selected option
        voice = selected_voiceID.split(" - ")[0]

        if save_favourites_button:
            selected_voice_row = df[df["voiceID"] == selected_voiceID]
            save_to_favourites(selected_voice_row, excel_favourites)
            st.success("Voice saved to favourites!")


        if remove_favourites_button:
            df_favourites = load_from_excel(excel_favourites)
            df_favourites = df_favourites[df_favourites["voiceID"] != selected_voiceID]
            df_favourites.to_excel(excel_favourites, index=False)
            st.success("Voice removed from favourites!")
            st.experimental_rerun()


        # Get the value of the "sample" column for the selected voice
        selected_voice = df.loc[df["value"] == voice, "sample"].values[0]


        with st.expander("Audio Sample", expanded = True):
            # Display the "sample" value for the selected voice
            st.audio(selected_voice)
            st.write(selected_voice)


    with tab2:
        # Text input
        text = st.text_area("Enter your text here", "Madonna tacchina!!")


        tts_button = st.button("TTS", type="primary", use_container_width=True)
        refresh_button = st.button("Refresh", use_container_width=True)
        
        # Button for TTS
        if tts_button:
            output_text = tts(text, "API-audio", voice)
            output_text, audio_file_path = url()
            st.write(output_text)

            # Display the audio file
            st.audio(audio_file_path)

        # Button for Download and Play
        if refresh_button:
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