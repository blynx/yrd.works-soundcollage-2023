#!/bin/bash

set -a
source audio_config.env
set +a

python3 "$(pwd)/collage.py"
