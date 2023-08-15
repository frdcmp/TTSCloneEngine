import os
import subprocess
import streamlit as st

def get_audio_files(folder_path):
    audio_files = [f for f in os.listdir(folder_path) if f.endswith('.mp3') or f.endswith('.wav')]
    return audio_files

def get_model_files(folder_path):
    model_files = [f for f in os.listdir(folder_path) if f.endswith('.pth')]
    return model_files

def main():
    st.title("Audio File Converter and Cloner")

    input_folder = './input'
    
    if not os.path.exists(input_folder):
        st.error(f"Folder '{input_folder}' not found.")
        return
    
    audio_files = get_audio_files(input_folder)
    
    if not audio_files:
        st.error(f"No audio files (mp3 or wav) found in '{input_folder}'.")
        return
    
    selected_file = st.selectbox("Select an audio file", audio_files)
    input_path = os.path.join(input_folder, selected_file)
    
    st.audio(input_path)
    
    transpose_value = st.number_input("Transpose Value (-12 to 12)", min_value=-12, max_value=12, value=0)
    
    # Use an absolute output path
    output_path = os.path.join(os.getcwd(), "output", selected_file)
    
    weight_folder = './weights'
    
    if not os.path.exists(weight_folder):
        st.error(f"Folder '{weight_folder}' not found.")
        return
    
    model_files = get_model_files(weight_folder)
    model_path = st.selectbox("Select a Model Path", model_files)
    
    index_file_path = st.text_input("Index File Path")
    inference_device = st.text_input("Inference Device", value="cuda:0")
    method = st.selectbox("Method", ["pm", "harvest", "crepe"])
    
    clone_button = st.button("Clone")
    
    if clone_button:
        terminal_command = [
            "python", 
            "modules/Retrieval-based-Voice-Conversion-WebUI/infer_cli.py",
            str(transpose_value),
            input_path,
            output_path,
            os.path.join(weight_folder, model_path),
            index_file_path,
            inference_device,
            method
        ]
        subprocess.run(terminal_command)
        st.success("Cloning process started. Please check the terminal for progress.")
        st.audio(output_path)
    
if __name__ == "__main__":
    main()
