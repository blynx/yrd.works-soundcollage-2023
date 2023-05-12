#!/bin/bash

./run-set-soundcard.sh

# needs to be set https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-mcp2221/linux
export BLINKA_MCP2221=1

python3 /home/boss/yrd.works-soundcollage-2023/collage.py
