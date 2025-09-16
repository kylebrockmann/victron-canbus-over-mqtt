#!/bin/sh
opkg install gcc binutils socketcand libgpiod3 libgpiod3 libgpiod-dev libgpiod-tools python3-venv python3-ensurepip python3-tomllib
python -m ensurepip --upgrade
ln -s /usr/bin/pip3 /usr/bin/pip
pip3 install --upgrade pip
ln -s /data/canmqtt /service/canmqtt
ln -s /home/root/canmqtt /usr/share/canmqtt
cd /usr/share/canmqtt
python -m venv venv12
chmod +x /usr/share/canmqtt/venv12/bin/python3
chmod +x /usr/share/canmqtt/venv12/bin/pip3
chmod +x /usr/share/canmqtt/venv12/bin/pip
chmod +x /usr/share/canmqtt/venv12/bin/python
source /usr/share/canmqtt/venv12/bin/activate
/usr/share/canmqtt/venv12/bin/pip install -r ./requirements.txt