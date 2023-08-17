#!/bin/bash
# Created by Francesco
# Define ANSI escape sequences for font styles and colors
RED=$(tput setaf 1)
BIG=$(tput bold; tput smso)
RESET=$(tput sgr0)

echo "${RED}${BIG}Install pip packages${RESET}"

# Install Python dependencies
pip install -r requirements.txt
pip install torch torchvision torchaudio ffmpeg-python --no-input

# Download aria
apt -y install -qq aria2

# Hurberto
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt -d ./ -o hubert_base.pt

# Clone the Git repository
mkdir modules
cd modules
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI

echo "${RED}${BIG}Pip the Cazooooo.txt${RESET}"
pip install -r requirements.txt

# Create api.py file in the ./temp folder
echo "${RED}${BIG}Create api.py file in the ./temp folder${RESET}"
echo "X_USER_ID = \"USER_ID\"" > ../temp/api.py
echo "AUTHORIZATION = \"AUTHORIZATION\"" >> ../temp/api.py

echo "${RED}${BIG}Installation done!${RESET}"