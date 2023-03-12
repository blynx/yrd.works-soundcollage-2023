#!/bin/bash

# list soundcards
# pacmd list-sinks | grep -e 'name:' -e 'index:'

soundcard=$(pacmd list-sinks | sed -En "s/.*<(alsa_output\.usb.*)>.*/\1/p")
echo "set soundcard to: $soundcard"
pacmd set-default-sink $soundcard

python3 ./collage.py
