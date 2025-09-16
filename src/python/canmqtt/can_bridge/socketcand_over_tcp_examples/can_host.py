import os

def create_virtual_can_interface():
    os.system('ip link add vcan0 type vcan')
    os.system('ip link set vcan0 down')
    os.system('ip link set vcan0 txqueuelen 65536')
    os.system('ip link set vcan0 up')

def start_listening():
    create_virtual_can_interface()
    os.system('socketcand -v -i vcan0 -p 5000 --listen eth0')


