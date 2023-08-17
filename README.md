# TTSCloneEngine

## Overview

TTSCloneEngine is a Python program that combines text-to-speech (TTS) generation from an API (play.ht) with the Retrieval-based Voice Conversion (RVC) technique for cloning speech.


## Installation with the setup

1. Create a Python 3.10 environment using conda:
   ```bash
   conda create -n tce python=3.10
   conda activate tce

2. Run the setup script:
   ```bash
    chmod +x setup.sh
    ./setup.sh



## Manual installation

1. Install required Python packages and system dependencies:
   ```bash
    pip install -r requirements.txt
    pip install torch torchvision torchaudio ffmpeg-python --no-input
    sudo apt-get install build-essential nano p7zip-full -y
    sudo apt -y install -qq aria2

2. Download a pre-trained model and clone the RVC repository:
   ```bash
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt -d ./ -o hubert_base.pt
    cd modules
    git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
    cd Retrieval-based-Voice-Conversion-WebUI && pip install -r requirements.txt

3. Run the Streamlit application:
   ```bash
    streamlit run tts-clone-engine.py


## Configure API credentials by creating an api.py file in the ./temp folder:
    # api.py
    X_USER_ID = "USER_ID"
    AUTHORIZATION = "AUTHORIZATION"

## Conclusion
For contributions, improvements, or bug fixes, feel free to submit pull requests. TTSCloneEngine is released under the MIT License, granting users the freedom to use, modify, and distribute the software according to the license terms.