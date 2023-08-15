import os
import requests
import streamlit as st
import sys
import pandas as pd
import subprocess
import wave
import shutil

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

# Functions for Voice
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


# Function for TTS
def load_trans_id(filename):
    try:
        with open(filename, "r") as file:
            transcription_id = file.read().strip()
            return transcription_id
    except FileNotFoundError:
        return ""

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


# Function for Cloning
def get_audio_files(folder_path):
    audio_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3') or f.endswith('.wav')]
    return audio_files

def get_model_files(folder_path):
    model_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.pth'):
                model_files.append(os.path.relpath(os.path.join(root, file), folder_path))
    return model_files

def get_index_files(folder_path):
    index_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.index'):
                index_files.append(os.path.relpath(os.path.join(root, file), folder_path))
    return index_files

def get_voice_values():
    url = "https://play.ht/api/v1/getVoices"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices_data = response.json().get("voices", [])
        return voices_data
    else:
        raise ValueError("Failed to fetch voice data from the API.")



# Streamlit app
def main():
    st.title("TTS Clone Engine")

    tab1, tab2, tab3, tab4 = st.tabs(["Voice", "TTS", "Cloning", "Settings"])


####### Tab 1: Select the TTS voice
    with tab1:
        st.header("Select the TTS voice")
        excel_voices = "./temp/voices.xlsx"
        excel_favourites = "./temp/favourites.xlsx"

        


        with st.expander("Filter voices and show favourites", expanded = True):

            #with col1:
                #title = st.text_input("Project name", "API-audio")

            #FAVOURITES?
            show_favorites = st.checkbox("Favourites", value=True)
            
            if show_favorites:
                df = load_from_excel(excel_favourites)
            else:
                df = load_from_excel(excel_voices)


            #Create a voiceID
            df["voiceID"] = df["value"] + " - " + df["name"] + " - " + df["languageCode"] + " - " + df["gender"]

            col1, col2 = st.columns(2)

            with col2:
                # Create a multiselect box for filtering voices by gender
                selected_genders = st.multiselect("Filter by Gender", df["gender"].unique(), ['Male', 'Female'])
            with col1:
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


        # Initialize a session state to keep track of the selected index
        if 'voice_index' not in st.session_state:
            st.session_state.voice_index = 0




        # Voice selection with both voice name, languageCode, and gender
        selected_voiceID = st.selectbox("Select a voice", filtered_df['voiceID'], index=st.session_state.voice_index)


        if st.button("Next", use_container_width=True) and st.session_state.voice_index < len(filtered_df) - 1:
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





####### Tab 2: Select the TTS voice
    with tab2:
        st.header("Generate the TTS")
        col1, col2 = st.columns([1,3])

        with col1:
            
            title = st.text_input("Name the audio file", "API-audio")
            
            refresh_button = st.button("Refresh", use_container_width=True)
        with col2:    
            # Text input
            text = st.text_area("Enter your text here", "Madonna tacchina!!")
        
        tts_button = st.button("TTS", type="primary", use_container_width=True)


        



####### Tab x: Resampling the voice
        st.caption("")
        st.caption("Adjust TTS speed")

        # Define fixed variables
        with open('./temp/path.txt') as f:
            input_folder = f.readline().strip()
            weight_folder = f.readline().strip()

        audio_files = get_audio_files(input_folder)
        selected_file = st.selectbox("Select an audio file for resampling", audio_files)



        with st.form("Adjust TTS speed"):
            if selected_file:
                input_path = os.path.join(input_folder, selected_file)

                # Get original sample rate
                spf = wave.open(input_path, 'rb')
                original_sample_rate = spf.getframerate()
                spf.close()

                # Calculate output sample rate based on slider percentage
                slider_percentage = st.slider("Select Output Sample Rate", 50, 200, 100)
                output_sample_rate = int(original_sample_rate * slider_percentage / 100)
                
                submitted = st.form_submit_button("Convert and Save", use_container_width=True)
                # Convert and save the new audio file
                if submitted:

                    signal = open(input_path, 'rb').read()

                    # Construct the output filename with "_resampled" prefix
                    filename, file_extension = os.path.splitext(selected_file)
                    output_filename = f"{filename}_resampled{file_extension}"
                    output_path = os.path.join(input_folder, output_filename)

                    wf = wave.open(output_path, 'wb')
                    spf = wave.open(input_path, 'rb')
                    CHANNELS = spf.getnchannels()
                    swidth = spf.getsampwidth()
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(swidth)
                    wf.setframerate(output_sample_rate)
                    wf.writeframes(signal)
                    wf.close()
                    st.success(f"Audio conversion and save successful. Check './input/{output_filename}'. Output Sample Rate: {output_sample_rate} Hz.")
                    

                    #st.audio(input_path)               
                    st.audio(output_path)


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




####### Tab 3: Clone the voice
    with tab3:
        
        st.header("Clone the voice")

        # Fetch files for weights and logs
        model_files = get_model_files(weight_folder)
        index_files = get_index_files(weight_folder)
        inference_device = ("cuda:0")  

        if not os.path.exists(input_folder):
            st.error(f"Folder '{input_folder}' not found.")
            return
        
        audio_files = get_audio_files(input_folder)
        
        if not audio_files:
            st.error(f"No audio files (mp3 or wav) found in '{input_folder}'.")
            return
        
        selected_file = st.selectbox("Select an audio file", audio_files)
        input_path = os.path.join(input_folder, selected_file)

        # Play the source TTS
        st.audio(input_path)
        




        with st.form("Clone the voice"):
            #with st.expander("Cloning settings", expanded = True):
            model_path = st.selectbox("Select a Model Path", model_files)
            
            col1, col2 = st.columns(2)
            with col1:
                transpose_value = st.number_input("Transpose Value (-12 to 12)", min_value=-12, max_value=12, value=0)

                # Use an absolute output path
                output_path = os.path.join(os.getcwd(), "output", selected_file)

                if not os.path.exists(weight_folder):
                    st.error(f"Folder '{weight_folder}' not found.")
                    return
                
            with col2:
                method = st.selectbox("Method", ["harvest", "pm", "crepe"])

            with col1:
                with st.expander("Index Rate", expanded = True):
                    index_rate = st.slider("Index Rate", min_value=0.0, max_value=1.0, value=0.0, step=0.5, label_visibility="collapsed")
            with col2:               
                if index_rate == 0:
                    index_file_path = st.selectbox("Select a Index Path. Ignore if the index rate is null.", index_files)
                    index_file_path = ""
                else:
                    #index_file_path = st.text_input("Index File Path")
                    
                    index_file_path = st.selectbox("Select a Index Path", index_files)
                    


            submitted = st.form_submit_button("Clone", type="primary", use_container_width=True)            
            #clone_button = st.button("Clone")
            
            if submitted:
                terminal_command = [
                    "python", 
                    "modules/Retrieval-based-Voice-Conversion-WebUI/infer_cli.py",
                    str(transpose_value),
                    input_path,
                    output_path,
                    os.path.join(weight_folder, model_path),
                    index_file_path,
                    inference_device,
                    method,
                    #str(index_rate)
                ]
                subprocess.run(terminal_command)
                st.success("Cloning process started. Please check the terminal for progress.")
                st.audio(output_path)
                #st.write(terminal_command)


####### Tab 4: Settings
    with tab4:
        st.header("Settings")
        with st.expander("Change path location for weights and indexes", expanded = True):
            col1, col2 = st.columns(2)
            with col1:
                # Text inputs for input_folder and weight_folder
                new_input_folder = st.text_input("Input Folder", value=input_folder)
            with col2:
                new_weight_folder = st.text_input("Weight and Index Folder", value=weight_folder)


            # Button to save and update path.txt
            save_button = st.button("Save and Update Path", use_container_width=True)
            if save_button:
                with open('./temp/path.txt', 'w') as f:
                    f.write(new_input_folder + '\n')
                    f.write(new_weight_folder + '\n')
                st.success("Path.txt updated successfully.")

            st.divider()
            st.caption("Fetch the API voices and check for updates")
            update_button = st.button("Update Voice List from API")

            #Update Voices Database Button
            if update_button:
                st.write("Fetching voice data from the API...")
                voice_data = get_voice_values()
                save_to_excel(voice_data, excel_voices)
                st.write("Voice list updated!")



if __name__ == "__main__":
    main()