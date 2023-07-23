import streamlit as st
from gtts import gTTS
import os

def text_to_speech(text, language_code, output_folder):
    tts = gTTS(text, lang=language_code)
    output_file = os.path.join(output_folder, "output.mp3")
    tts.save(output_file)
    return output_file

def main():
    st.title("Text-to-Speech App with gTTS")

    # User input text box
    user_input = st.text_area("Enter text:", "Type your text here...")

    # Language selection
    languages = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "nl": "Dutch",
        "pt": "Portuguese",
        "ru": "Russian",
        "zh-cn": "Chinese (Simplified)",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "hi": "Hindi",
        # Add more languages and their codes here
    }
    selected_language = st.selectbox("Select Language:", list(languages.keys()), format_func=lambda x: languages[x])

    # Button to trigger the conversion
    if st.button("Convert to Speech"):
        # Create the output folder if it doesn't exist
        output_folder = "./tts"
        os.makedirs(output_folder, exist_ok=True)

        # Convert text to speech and save the output file
        output_file = text_to_speech(user_input, selected_language, output_folder)
        st.success("Text-to-speech conversion successful!")
        st.audio(output_file)

if __name__ == "__main__":
    main()
