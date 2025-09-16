import os

def create_virtual_can_interface(vcan_name="vcan0"):
    os.system(f'ip link add {vcan_name} type vcan')
    os.system(f'ip link set {vcan_name} down')
    os.system(f'ip link set {vcan_name} txqueuelen 65536')
    os.system(f'ip link set {vcan_name} up')

def start_listening():
    create_virtual_can_interface()
    os.system('socketcand -v -i vcan0 -p 5000 --listen eth0')


