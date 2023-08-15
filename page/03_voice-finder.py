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

def get_voice_index():
    if 'voice_index' not in st.session_state:
        st.session_state.voice_index = 0
    return st.session_state.voice_index


# Streamlit app
def main():
    st.title("Find the right voice and save it")


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
        show_favorites = st.checkbox("Favourites", value=False)
        
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


    # Initialize a session state to keep track of the selected index
    if 'voice_index' not in st.session_state:
        st.session_state.voice_index = 0

    # Voice selection with both voice name, languageCode, and gender
    selected_voiceID = st.selectbox("Select a voice", filtered_df['voiceID'], index=st.session_state.voice_index)

    col1, col2 = st.columns(2)
    if col1.button("Back") and st.session_state.voice_index > 0:
        st.session_state.voice_index -= 1
    if col2.button("Next") and st.session_state.voice_index < len(filtered_df) - 1:
        st.session_state.voice_index += 1
        

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



if __name__ == "__main__":
    main()