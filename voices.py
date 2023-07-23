import requests
import streamlit as st

url = "https://play.ht/api/v1/getVoices"

headers = {
    "accept": "application/json",
    "AUTHORIZATION": "",
    "X-USER-ID": ""
}

response = requests.get(url, headers=headers)

voices = response.json()["voices"]

voices_names = []

for voice in voices:
    voices_names.append(voice["name"])

# Create a drop down menu
voices_select = st.selectbox("Select the voice:", voices_names)

# Print the selected voice
st.write(voices_select)
