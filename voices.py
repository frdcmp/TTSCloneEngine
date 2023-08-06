import os
import gradio as gr
import sys



# TTS
sys.path.append('./tempo/')  # Add the './API/' directory to the module search path
from api import AUTHORIZATION, X_USER_ID
import requests
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
        # Modify the list to include voice name, language code, and gender
        return [f"{voice['value']} ({voice['languageCode']} - {voice['gender']})" for voice in voices_data]
    else:
        raise ValueError("Failed to fetch voice data from the API.")

voice_values = get_voice_values()

def extract_voice_name(full_voice):
    # Extract the voice name from the format "Voice Name (Language Code - Gender)"
    return full_voice.split(" (")[0]

def load_trans_id(filename):
    try:
        with open(filename, "r") as file:
            transcription_id = file.read().strip()
            return transcription_id
    except FileNotFoundError:
        return ""

def tts(text, title, voice):
    # Extract the voice name from the selected option
    voice_name = extract_voice_name(voice)
    
    transcription_id = load_trans_id("./tempo/trans_id.txt")
    url = "https://play.ht/api/v1/convert"
    payload = {
        "content": [text],
        "voice": voice_name,  # Use the extracted voice name
        "transcriptionId": transcription_id,
        "title": title
    }
    response = requests.post(url, json=payload, headers=headers)
    transcription_id = response.json()["transcriptionId"]
    output_text = f"TTS created, the transcription ID is: {transcription_id}"
    return output_text

def url():
    transcription_id = load_trans_id("./tempo/trans_id.txt")
    response = requests.get(f"https://play.ht/api/v1/articleStatus?transcriptionId={transcription_id}", headers=headers)
    audio_url = response.json()["audioUrl"]
    output_text = f"Link to the media file: {audio_url}"

    # Download the audio file from the URL and save it to the './API' folder
    input_folder = "./API"
    os.makedirs(input_folder, exist_ok=True)
    audio_file_path = os.path.join(input_folder, "API-audio.wav")

    with requests.get(audio_url, stream=True) as response:
        response.raise_for_status()
        with open(audio_file_path, "wb") as audio_file:
            for chunk in response.iter_content(chunk_size=8192):
                audio_file.write(chunk)

    return output_text, audio_file_path

with gr.Blocks() as demo:
    # First Column
    with gr.Row():
        title = gr.Textbox(label="Enter a name for the audio file:", value="API-audio")
        voice_dropdown = gr.Dropdown(choices=voice_values, label="Select a voice", )

    # Second Column
    with gr.Row():
        text = gr.Textbox(label="Enter your text here:", lines=5, value="Madonna tacchina!!")

    # Third Column
    with gr.Row():
        output = gr.Textbox(label="Output Values")
        audio = gr.Audio(label="TTS Box")

    # Fourth Column
    with gr.Row():
        tts_button = gr.Button("TTS", variant="primary")
        tts_button.click(lambda text, title, voice: tts(text, title, extract_voice_name(voice)), inputs=[text, title, voice_dropdown], outputs=output)

    # Fifth Column
    with gr.Row():
        url_button = gr.Button("Download and Play")
        url_button.click(url, outputs=[output, audio])

demo.launch()
