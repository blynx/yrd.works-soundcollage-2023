#!/bin/bash

# Cheatsheets

# sed find/replace line
# sed 's/^.*\bpattern\b.*$/Substitution/' file

# cat > REPLACE_NEWFILE << EOF
# cat >> APPEND_FILE << EOF

# ---

# Auto login
# In /lib/systemd/system/getty@.service
# From: ExecStart=-/sbin/agetty -o '-p -- \\u' --noclear %I $TERM
# To: ExecStart=-/sbin/agetty --noissue --autologin boss %I $TERM Type=idle
LOGIN_FIND="^ExecStart=.*$"
LOGIN_REPLACE="ExecStart=-\/sbin\/agetty --noissue --autologin boss %I \$TERM Type=idle"
sudo sed -i "s/$LOGIN_FIND/$LOGIN_REPLACE/g" /lib/systemd/system/getty@.service



# Install python, board, dependencies, alsa & co
sudo apt-get -y install python3 python3-pip libusb-1.0 libudev-dev pulseaudio alsa-base alsa-utils moc
pip install pygame hidapi adafruit-blinka



# "wait for network start job" ignorieren
sed -i -e '/    enp1s0:/a\' -e '      optional: true' /etc/netplan/00-installer-config.yaml
sed -i -e '/    mlan0:/a\' -e '      optional: true' /etc/netplan/00-installer-config-wifi.yaml
sudo netplan apply



# disabled cloud-init
sudo touch /etc/cloud/cloud-init.disabled



# Board config wie in https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-mcp2221/linux
cat > /etc/udev/rules.d/99-mcp2221.rules << EOF
SUBSYSTEM=="usb", ATTRS{idVendor}=="04d8", ATTR{idProduct}=="00dd", MODE="0666"
EOF

sudo rmmod hid_mcp2221

cat >> /etc/modprobe.d/blacklist.conf << EOF

# blacklist native mcp2221 driver for adafruit driver
blacklist hid_mcp2221
EOF

sudo update-initramfs -u


# Autorun service erstellen:
# cat > /etc/systemd/system/yrd.works-soundcollage-start.service << EOF
# [Unit]
# Description=Autorun YRD.WORKS Soundcollage

# [Service]
# ExecStart=/bin/bash /home/boss/yrd.works-soundcollage-2023/run.sh
# User=boss

# [Install]
# WantedBy=default.target
# EOF

# sudo systemctl enable yrd.works-soundcollage-start.service

echo "Installation fertig!? 🥸 ... einmal neu starten bitte."