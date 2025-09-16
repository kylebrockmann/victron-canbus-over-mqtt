import time

import can
import os
import paho.mqtt.client as mqtt
import json
from threading import Thread
from paho.mqtt.enums import CallbackAPIVersion

# MQTT settings
# Change to your MQTT broker address
MQTT_BROKER = os.environ.get("MQTT_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "can/bridge")
MQTT_CLIENT_ID = os.environ.get("MQTT_CLIENT_ID", "can_receiver")

class CANToMQTTBridge:
    def __init__(self, source_channel, dest_topic):
        self.source_channel = source_channel
        self.dest_topic = dest_topic
        self.source_bus = None
        self.mqtt_client = None
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

    def initialize_mqtt(self):
        self.mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION1, userdata=MQTT_CLIENT_ID)
        self.running = False

    def next_message(self) -> can.Message:
        return self.source_bus.recv(timeout=1.0)

    def can_to_mqtt(self):
        """Read from CAN and publish to MQTT"""
        while self.running:
            try:
                message = self.next_message()
                if message is not None:
                    # Convert CAN message to JSON
                    msg_dict = {
                        'id': message.arbitration_id,
                        'data': message.data.hex(),
                        'is_extended_id': message.is_extended_id
                    }

                    # Publish to MQTT
                    self.mqtt_client.publish(
                        MQTT_TOPIC,
                        json.dumps(msg_dict)
                    )
                    print(f"Published from {self.source_channel}: ID={hex(message.arbitration_id)}, Data={message.data.hex()}")

            except Exception as e:
                print(f"Error in CAN to MQTT: {e}")

    def run(self):
        self.initialize_can()
        self.initialize_mqtt()
        self.start()

    def start(self):
        """Start the bridge"""
        self.running = True

        # Connect to MQTT broker
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        except Exception as e:
            print(f"Failed to connect to MQTT: {e}")

        # Start MQTT loop in a separate thread
        self.mqtt_client.loop_start()

        # Start CAN to MQTT forwarding in a thread
        can_thread = Thread(target=self.can_to_mqtt)
        can_thread.start()

        print("CAN-MQTT bridge started. Press Ctrl+C to stop.")

        try:
            can_thread.join()
        except KeyboardInterrupt:
            print("\nBridge stopped by user")
        finally:
            self.stop()

    def stop(self):
        """Stop the bridge and clean up"""
        self.running = False
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        self.source_bus.shutdown()
