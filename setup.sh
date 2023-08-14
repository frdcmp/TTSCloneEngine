#!/bin/bash
# Created by Francesco
# Define ANSI escape sequences for font styles and colors
RED=$(tput setaf 1)
BIG=$(tput bold; tput smso)
RESET=$(tput sgr0)

#echo "${RED}${BIG}Install Dependencies - Porca Zozza${RESET}"

# Update and upgrade the system
#apt-get update
#apt-get upgrade -y


# Install required packages
#apt-get install build-essential nano p7zip-full -y

echo "${RED}${BIG}Install pip packages${RESET}"

# Install Python dependencies
pip install -r requirements.txt
pip install torch torchvision torchaudio ffmpeg-python --no-input


# Clone the Git repository
mkdir modules
cd modules
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI

echo "${RED}${BIG}Download Modules Cazooooo${RESET}"

# Download aria
apt -y install -qq aria2

# Hurberto
aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt -d ./ -o hubert_base.pt

echo "${RED}${BIG}Pip the Cazooooo.txt${RESET}"

  pip install -r requirements.txt

# Launch the service
read -p "${RED}${BIG}Ciao Bastardo, the setup is complete. Would you like to start the RVC? (y/n)${RESET} " start_rvc

if [ "$start_rvc" == "y" ] || [ "$start_rvc" == "Y" ]; then
  # Launch the service
  
  python3 infer-web.py --colab --pycmd python3
else
  echo "${RED}${BIG}RVC launch terminated.${RESET}"
fi