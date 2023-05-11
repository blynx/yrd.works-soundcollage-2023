#!/bin/bash

# cat > REPLACE_NEWFILE << EOF
# cat >> APPEND << EOF

# Install python, board, dependencies, alsa & co
# sudo apt-get --force-yes install python3 python3-pip libusb-1.0 libudev-dev pulseaudio alsa-base alsa-utils 
# pip install pygame hidapi adafruit-blinka

# TODO: "wait for network start job" Fehler :/ .. wegen wlan?

# TODO: Pulseaudio service direkt starten oder manueller Neustart?

# Board config wie in https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-mcp2221/linux
# TODO: test
# cat > /etc/udev/rules.d/99-mcp2221.rules << EOF
# SUBSYSTEM=="usb", ATTRS{idVendor}=="04d8", ATTR{idProduct}=="00dd", MODE="0666"
# EOF

# sudo rmmod hid_mcp2221
# TODO: "blacklist hid_mcp2221" in die datei: /etc/modprobe.d/blacklist.conf
# sudo update-initramfs -u

# Autorun service erstellen:
# TODO: pfad für yrd.works-soundcollage-start.service
cat > TEST2 << EOF
[Unit]
Description=Autorun YRD.WORKS Soundcollage

[Service]
ExecStart=/bin/bash /home/boss/yrd.works-soundcollage-2023/run.shit
User=boss

[Install]
WantedBy=default.target
EOF
# systemctl enable yrd.works-soundcollage-start.service


