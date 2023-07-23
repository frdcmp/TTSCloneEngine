import mutagen
import streamlit as st

# Get the path to the audio file
audio_file_path = "./input/API-audio.wav"

# Create a mutagen object
audio_file = mutagen.File(audio_file_path)

# Create a Streamlit text input widget for the title tag
title = st.text_input("Enter the title of the audio file:")

# Convert the string to a Frame instance
title_frame = mutagen.id3.TextFrame(encoding=3, text=title)

# Set the title tag
audio_file["title"] = title_frame

# Save the audio file with the new metadata
audio_file.save()

# Display a message confirming that the metadata has been added
st.write("Metadata added successfully!")

# Create a Streamlit table to visualize the metadata
metadata_table = st.table(audio_file.tags)
