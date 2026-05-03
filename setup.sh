#!/bin/bash

echo "[*] MACFLIP - MAC Address Changer Setup"

if [ "$EUID" -ne 0 ]; then 
    echo "[!] Please run as root: sudo ./setup.sh"
    exit 1
fi

apt update
apt install python3 python3-pip -y
pip3 install --upgrade pip

mkdir -p backup

chmod +x macflip.py

echo "[+] Setup complete!"
echo "[*] Run: sudo python3 macflip.py"
