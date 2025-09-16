from pathlib import Path

class CanFrameSource:
    def __init__(self, interface_name = "vcan0"):
        self.interface_name = interface_name
        self.interface_class = Path(self.interface_path)

    @property
    def interface_exists(self):
        if not self.interface_class.exists():
            return False
        return True

    @property
    def interface_path(self):
        return f"/sys/class/net/{self.interface_name}"

    @property
    def interface_status(self):
        state_path = f"{self.interface_path}/operstate"
        f = open(state_path, "r")
        state = f.readline().strip().lower()
        f.close()
        return state

    @property
    def is_interface_up(self):
        if self.interface_status == "unknown":
            return True
        if self.interface_status == "up":
            return True
        else:
            return False


    @property
    def device_path(self):
        return f"/dev/{self.interface_name}"
