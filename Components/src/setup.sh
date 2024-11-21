#!/bin/bash

# Define the directory for the virtual environment
VENV_DIR="/greengrass/v2/GreenGrassV2HelloWorld_venv"
sudo -i
# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Upgrade pip and install required packages
pip install --upgrade pip
pip install awsgreengrasspubsubsdk numpy

# Deactivate the virtual environment
deactivate