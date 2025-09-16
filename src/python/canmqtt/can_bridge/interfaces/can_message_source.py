import can
from util.logger import logger as log
from threading import Thread
from queuing.canbus_queue import CANBusQueue


class CANMessageSource:
    def __init__(self, source_channel : str, message_queue: CANBusQueue):
        self.source_channel = source_channel
        self.source_bus = None
        self.message_queue = message_queue
        self.running = False

    def initialize_can(self):
        try:
            self.source_bus = can.interface.Bus(
                channel=self.source_channel,
                bustype='socketcan',
                bitrate=500000
            )
        except Exception as e:
            print(f"Failed to initialize CAN buses: {e}")
            raise

    def next_message(self) -> can.Message:
        return self.source_bus.recv(timeout=1.0)

    def can_to_mqtt(self):
        while self.running:
            try:
                message = self.next_message()
                if message is not None:
                    self.message_queue.send_can_message(message)
                    log.info(f"Published from {self.source_channel}: ID={hex(message.arbitration_id)}, Data={len(message.data)}")
            except Exception as e:
                log.error(f"Error in CAN to MQTT: {e}")

    def run(self):
        self.initialize_can()
        self.start()

    def start(self):
        self.running = True
        can_thread = Thread(target=self.can_to_mqtt)
        can_thread.start()
        print("CAN-MQTT bridge can message source started. Press Ctrl+C to stop.")
        try:
            can_thread.join()
        except KeyboardInterrupt:
            print("\nBridge stopped by user")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        self.source_bus.shutdown()
