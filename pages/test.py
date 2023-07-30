import os
import requests
import gradio as gr
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


def modify_audio_speed(audio_file, speed_percentage):
    # Load the audio file
    audio = AudioSegment.from_file(audio_file)

    # Calculate the speed factor based on the percentage
    speed_factor = speed_percentage / 100.0

    # Apply the speed adjustment without changing pitch
    audio = audio.speedup(playback_speed=speed_factor)

    # Overwrite the original file with the modified audio
    audio.export(audio_file, format="mp3")

    return audio_file, f"Speed modified: {speed_percentage}%"

def change_sample_rate(audio_file, new_sample_rate):
    # Load the audio file
    audio = AudioSegment.from_file(audio_file)

    # Set the frame rate to the desired rate without resampling
    audio = audio.set_frame_rate(new_sample_rate)

    # Overwrite the original file with the modified audio
    audio.export(audio_file, format="mp3")

    return audio_file, f"New sample rate: {new_sample_rate} Hz"

def get_voice_values():
    url = "https://play.ht/api/v1/getVoices"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices_data = response.json().get("voices", [])
        return [voice.get("value") for voice in voices_data]
    else:
        raise ValueError("Failed to fetch voice data from the API.")

voice_values = get_voice_values()

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
    print(text)
    response = requests.post(url, json=payload, headers=headers)
    transcription_id = response.json()["transcriptionId"]
    output_text = f"Transaction ID is: {transcription_id}"
    return output_text

def ssml(text, title, voice):
    transcription_id = load_trans_id("./temp/trans_id.txt")

    url = "https://play.ht/api/v1/convert"

    payload = {
        "ssml": [text],
        "voice": voice,
        "transcriptionId": transcription_id,
        "title": title
    }
    print(text)
    response = requests.post(url, json=payload, headers=headers)
    transcription_id = response.json()["transcriptionId"]
    output_text = f"Transaction ID is: {transcription_id}"
    return output_text

def url():
    transcription_id = load_trans_id("./temp/trans_id.txt")
    response = requests.get(f"https://play.ht/api/v1/articleStatus?transcriptionId={transcription_id}", headers=headers)
    audio_url = response.json()["audioUrl"]
    print(audio_url)
    output_text = f"Transaction ID is: {transcription_id}. Link to the media file: {audio_url}"

    # Download the audio file from the URL and save it to the ./API folder
    input_folder = "./API"
    os.makedirs(input_folder, exist_ok=True)
    audio_file_path = os.path.join(input_folder, "API-audio.mp3")

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
        voice = gr.Dropdown(choices=voice_values, label="Select a voice", )  # Replace the Textbox with Dropdown

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
        tts_button.click(tts, inputs=[text, title, voice], outputs=output)

        ssml_button = gr.Button("SSML", variant="primary")
        ssml_button.click(ssml, inputs=[text, title, voice], outputs=output)

    # Fifth Column
    with gr.Row():
        url_button = gr.Button("Download and Play")
        url_button.click(url, outputs=[output, audio])


    with gr.Row():
        sample_rate_input = gr.Slider(8000, 48000, value=22050, step=1000, interactive=True)
        audio_file_input = gr.Textbox(label="Input the audio file name:", value="./API/API-audio.mp3")

        audio_output = gr.Audio(label="Output Audio")
        text_output = gr.Textbox(label="Output Values")

        sample_rate_conversion = gr.Button("Convert sample rate")
        sample_rate_conversion.click(change_sample_rate, inputs=[audio_file_input, sample_rate_input], outputs=[audio_output, text_output])
    
    # Speed Slider
    with gr.Row():
        speed_slider = gr.Slider(minimum=50, maximum=200, step=5, label="Speed Percentage")

    # Speed Button
    with gr.Row():
        speed_button = gr.Button("Modify Speed")
        speed_button.click(modify_audio_speed, inputs=[audio_file_input, speed_slider], outputs=[audio_output, text_output])


demo.launch()
