import os
import requests
import gradio as gr
import pandas as pd
import sys
sys.path.append('./temp/')  # Add the './API/' directory to the module search path
from api import AUTHORIZATION, X_USER_ID
from pydub import AudioSegment


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
        return [voice.get("value") for voice in voices_data]
    else:
        raise ValueError("Failed to fetch voice data from the API.")

voice_values = get_voice_values()



def create_dataframe(voice_values):
    df = pd.DataFrame(voice_values)
    df["language"] = df["value"].apply(lambda x: x.split("_")[0])
    df["voiceType"] = df["value"].apply(lambda x: x.split("_")[1])
    df["gender"] = df["value"].apply(lambda x: x.split("_")[2])
    return df


with gr.Blocks() as demo:
    # First Column
    with gr.Row():
        voice = gr.Dropdown(choices=voice_values, label="Select a voice", )  # Replace the Textbox with Dropdown

demo.launch()
