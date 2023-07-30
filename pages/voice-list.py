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



# Streamlit app
def main():
    st.title("Text-to-Speech API Demo")

    # Fetch the DataFrame with voice data
    df = pd.DataFrame(voice_data)

    # Create a new column with the voice name and language combined
    df["voice_with_language"] = df["value"] + " - " + df["languageCode"]

    # Voice selection with both voice name and languageCode
    selected_voice_with_lang = st.selectbox("Select a voice", df["voice_with_language"])

    # Extract the voice value (without languageCode) from the selected option
    voice = selected_voice_with_lang.split(" - ")[0]

    # Text input
    text = st.text_area("Enter your text here", "Madonna tacchina!!")

    # Multiselect for filtering languageCode
    selected_language_codes = st.multiselect("Filter languageCode", df["languageCode"].unique())

    # Filter the DataFrame based on selected languageCode values
    filtered_df = df[df["languageCode"].isin(selected_language_codes)]
    
    # Display the filtered DataFrame

    markers_df = AgGrid(
        filtered_df,
        reload_data=False,
        editable=True,
        theme="streamlit",
        data_return_mode=DataReturnMode.AS_INPUT,
        update_mode=GridUpdateMode.MODEL_CHANGED,
    )

if __name__ == "__main__":
    main()