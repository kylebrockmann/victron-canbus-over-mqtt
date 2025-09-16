from canmqtt.interface.can_source import CanFrameSource
import time
from canmqtt.util.logger import logger as log

class CanInterfaceMonitor:
    def __init__(self, interface_name = "vcan0"):
        self.interface_name = interface_name
        self.can_source = CanFrameSource(interface_name)

    @property
    def interface_exists(self):
        return self.can_source.interface_exists

    def loop_until_ready(self):
        while not self.can_source.interface_exists:
            log.info(f"Waiting for CAN interface {self.interface_name} to exist...")
            time.sleep(5)
        while not self.can_source.is_interface_up:
            log.info(f"Waiting for CAN interface {self.interface_name} to be up...")
            time.sleep(5)
        log.info(f"CAN interface {self.interface_name} is up...")
        return True