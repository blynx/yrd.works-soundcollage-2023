##!/bin/bash

# list soundcards
# pacmd list-sinks | grep -e 'name:' -e 'index:'

soundcard=$(pacmd list-sinks | sed -En "s/.*<(alsa_output\.usb.*)>.*/\1/p")
echo "set soundcard to: $soundcard"
pacmd set-default-sink $soundcard

echo "set volume"
amixer set Speaker 90%

# needs to be set https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-mcp2221/linux
export BLINKA_MCP2221=1

python3 /home/stewo/scripts/yrd.works-soundcollage-2023/collage.py
