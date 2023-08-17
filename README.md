# TTSCloneEngine

## Overview

TTSCloneEngine is a Python program that combines the power of text-to-speech (TTS) generation from an API (play.ht) with the Retrieval-based Voice Conversion (RVC) technique for cloning speech. This tool provides a comprehensive solution for creating and replicating speech content with advanced capabilities.

## Key Features

### TTS Generation and Cloning

TTSCloneEngine seamlessly integrates with the play.ht API to generate high-quality text-to-speech output. It then employs RVC to clone the generated speech, enabling the creation of diverse speech content.

### Environment Setup

The program simplifies the setup process by providing clear instructions for creating a Python 3.10 environment, installing dependencies, and downloading essential models.

### Streamlit Integration

TTSCloneEngine offers a streamlined user experience through Streamlit, allowing users to easily interact with the program and initiate TTS generation and speech cloning.

### API Configuration

Users can configure API credentials by creating an API file in the designated folder, enabling smooth interaction with the play.ht service.

### Versatile Settings

The program allows users to customize settings such as model weights and log placement, tailoring the experience to individual preferences.

## How to Use

1. Create a Python 3.10 environment using conda:
   ```bash
   conda create -n tce python=3.10
   conda activate tce

2. Run the setup script:
    chmod +x setup.sh
    ./setup.sh

3. Install required Python packages and system dependencies:
    pip install -r requirements.txt
    pip install torch torchvision torchaudio ffmpeg-python --no-input
    sudo apt-get install build-essential nano p7zip-full -y
    sudo apt -y install -qq aria2

4. Download a pre-trained model and clone the RVC repository:
    aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt -d ./ -o hubert_base.pt
    cd modules
    git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
    cd Retrieval-based-Voice-Conversion-WebUI && pip install -r requirements.txt

5. Run the Streamlit application:
    streamlit run tts-clone-engine.py


## Configure API credentials by creating an api.py file in the ./temp folder:
    # api.py
    X_USER_ID = "USER_ID"
    AUTHORIZATION = "AUTHORIZATION"

## Conclusion
TTSCloneEngine empowers users to effortlessly generate and clone speech content using TTS and RVC techniques. By following the outlined steps in this README, users can quickly set up and utilize the program's advanced features for their audio processing needs.

For contributions, improvements, or bug fixes, feel free to submit pull requests. TTSCloneEngine is released under the MIT License, granting users the freedom to use, modify, and distribute the software according to the license terms.