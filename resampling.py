import os
import streamlit as st
import wave
import shutil

# Function to get audio files in a folder
def get_audio_files(folder_path):
    audio_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3') or f.endswith('.wav')]
    return audio_files

def main():
    st.title("Audio Sample Rate Converter")

    input_folder = "./input"
    output_folder = "./output"
    audio_files = get_audio_files(input_folder)
    selected_file = st.selectbox("Select an audio file", audio_files)

    if selected_file:
        input_path = os.path.join(input_folder, selected_file)

        # Get original sample rate
        spf = wave.open(input_path, 'rb')
        original_sample_rate = spf.getframerate()
        spf.close()

        # Calculate output sample rate based on slider percentage
        slider_percentage = st.slider("Select Output Sample Rate", 50, 200, 100)
        output_sample_rate = int(original_sample_rate * slider_percentage / 100)

        # Convert and save the new audio file
        if st.button("Convert and Save"):
            signal = open(input_path, 'rb').read()
            output_path = os.path.join(output_folder, selected_file)

            wf = wave.open(output_path, 'wb')
            spf = wave.open(input_path, 'rb')
            CHANNELS = spf.getnchannels()
            swidth = spf.getsampwidth()
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(swidth)
            wf.setframerate(output_sample_rate)
            wf.writeframes(signal)
            wf.close()
            st.success(f"Audio conversion and save successful. Check './output/{selected_file}'. Output Sample Rate: {output_sample_rate} Hz.")

if __name__ == "__main__":
    main()
