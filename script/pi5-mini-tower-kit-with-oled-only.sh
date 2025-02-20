#!/bin/bash

sudo apt update
sudo apt install -y raspi-config i2c-tools \
	python3-dev python3-pip python3-numpy libfreetype6-dev libjpeg-dev build-essential libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev \
	git vim

sudo groupadd spi 
sudo groupadd gpio
sudo usermod -a -G i2c,spi,gpio $USER
sudo raspi-config 
i2cdetect -y 1

cd /tmp
git clone https://github.com/rm-hull/luma.examples.git
cd /tmp/luma.examples
sudo -H pip3 install -e . --break-system-packages
cd /tmp/luma.examples/examples
sudo -H pip3 install psutil --break-system-packages

sudo mkdir -p /usr/local/minitower/
sudo rsync -avP /tmp/luma.examples/examples/ /usr/local/minitower/
sudo chmod -R 755 /usr/local/minitower/
sudo cp /usr/local/minitower/sys_info.py /usr/local/minitower/service.py

sudo sh -c "sudo cat <<EOF >  '/etc/systemd/system/minitower_oled.service'
[Unit]
Description=Minitower OLED Service
DefaultDependencies=no
StartLimitIntervalSec=60
StartLimitBurst=5

[Service]
Type=simple
ExecStart=sudo /bin/bash -c '/usr/bin/python3 /usr/local/minitower/service.py'
RemainAfterExit=yes
Restart=always

[Install]
WantedBy=multi-user.target

EOF"

sudo chown root:root /etc/systemd/system/minitower_oled.service
sudo chmod 644 /etc/systemd/system/minitower_oled.service
sudo systemctl daemon-reload
sudo systemctl enable minitower_oled.service
sudo systemctl start minitower_oled.service
sudo systemctl restart minitower_oled.service
