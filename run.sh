#!/bin/bash

# sleep 10

./run-set-soundcard.sh

# export AUDIO_BACK_FILE=other-audio-file.mp3
# export AUDIO_OVERLAY_FILE=another-audio-file.mp3

# needs to be set https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-mcp2221/linux
export BLINKA_MCP2221=1

python3 /home/boss/yrd.works-soundcollage-2023/collage.py
