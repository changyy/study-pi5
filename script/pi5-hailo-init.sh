#!/bin/bash

sudo apt update && sudo apt upgrade -y  && sudo apt autoremove -y && sudo apt clean -y 
sudo apt install -y git vim curl tree cmake pkg-config linux-headers-$(uname -r) linux-headers-raspi build-essential

git clone https://github.com/hailo-ai/hailort-drivers.git
cd hailort-drivers
git log -1
cd ~/hailort-drivers/linux/pcie/
time make all
sudo make install
cd ~/hailort-drivers/
bash download_firmware.sh 
sudo mkdir -p /lib/firmware/hailo
sudo cp ./hailo8_fw.*.bin /lib/firmware/hailo/hailo8_fw.bin
sudo cp ~/hailort-drivers/linux/pcie/51-hailo-udev.rules /etc/udev/rules.d/

ls /dev/hailo*
sudo modprobe hailo_pci
ls /dev/hailo*

lspci
sudo dmesg | grep hailo

cd ~/
git clone https://github.com/hailo-ai/hailort
mkdir ~/hailort/build && cd ~/hailort/build
time cmake ..
time make -j2

./hailort/hailortcli/hailortcli fw-control identify
sudo make install
