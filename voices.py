import requests
import streamlit as st
from api import AUTHORIZATION, X_USER_ID

url = "https://play.ht/api/v1/getVoices"

headers = {
    "accept": "application/json",
    "AUTHORIZATION": AUTHORIZATION,
    "X-USER-ID": X_USER_ID,
}

response = requests.get(url, headers=headers)

voices = response.json()["voices"]

voices_names = [voice["name"] for voice in voices]

# Create a drop-down menu
voices_select = st.selectbox("Select the voice:", voices_names)

# Print the selected voice
st.write(voices_select)
