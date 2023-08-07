import streamlit as st
import soundfile as sf
import numpy as np
import os

def resample_audio(input_audio, input_sample_rate, target_sample_rate):
    # Load the input audio file
    audio, orig_sample_rate = sf.read(input_audio)
    
    # Calculate the resampling ratio
    resample_ratio = target_sample_rate / orig_sample_rate
    
    # Resample the audio using soundfile
    resampled_audio = np.interp(
        np.arange(0, len(audio), resample_ratio),
        np.arange(0, len(audio)),
        audio.T
    ).T
    
    # Save the resampled audio as WAV
    output_dir = "./API"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "converted.wav")
    sf.write(output_path, resampled_audio, target_sample_rate)
    
    return output_path

def main():
    st.title("Audio Resampling App")
    
    # Upload an audio file
    audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])
    
    # Input sample rate
    input_sample_rate = st.number_input("Input Sample Rate", value=44100, step=1)
    
    # Convert and resample audio
    if audio_file is not None:
        st.audio(audio_file, format="audio/wav")
        
        if st.button("Resample and Save"):
            output_path = resample_audio(audio_file, input_sample_rate, target_sample_rate=48000)
            st.success(f"Audio resampled and saved as 'converted.wav' in .API directory.")
    
if __name__ == "__main__":
    main()
