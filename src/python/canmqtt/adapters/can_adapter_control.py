import os

from canmqtt.interface.can_source import CanFrameSource


class CanAdapter:
    def __init__(self, interface_name = "can0"):
        self.frame_source = CanFrameSource(interface_name)
        self.interface_name = interface_name
        self.bit_rate = 500000
        self.tx_queue_len = 65536

    def assert_parameters(self):
        # Check if the interface already exists
        try:
            if not self.frame_source.interface_exists:
                return
            os.system(f'ip link show {self.interface_name}')
            print(f"Interface {self.interface_name} exists.")
        except Exception as e:
            print(f"Error checking interface: {e}")
        return

        os.system(f'ip link set {self.interface_name} down')
        os.system(f'ip link set {self.interface_name} type can bitrate {self.bit_rate}')
        #os.system(f'ip link set {self.interface_name} txqueuelen {self.tx_queue_len}')
        os.system(f'ip link set {self.interface_name} up')

    def assert_up(self):
        # Bring the interface up
        os.system(f'ip link set {self.interface_name} up')

    def check_if_up(self):
        # Check if the interface is up
        try:
            status = self.frame_source.interface_status
            print(f"Interface {self.interface_name} is {status}.")
            return self.frame_source.is_interface_up
        except Exception as e:
            print(f"Error checking interface status: {e}")
            return False

