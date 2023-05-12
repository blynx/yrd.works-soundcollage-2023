#!/bin/bash

# list soundcards
pacmd list-sinks | grep -e 'name:' -e 'index:'

soundcard=$(pacmd list-sinks | sed -En "s/.*<(alsa_output\.usb.*)>.*/\1/p")
echo "set soundcard to: $soundcard"
pacmd set-default-sink $soundcard

echo "set sink volume to 90%"
# amixer set Speaker 90% # alsa
pactl set-sink-volume 0 90% # pulseaudio
