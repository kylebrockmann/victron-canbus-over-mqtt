import time

import can
import paho.mqtt.client as mqtt
import json
from canmqtt.util.logger import logger

from paho.mqtt.enums import CallbackAPIVersion

# MQTT settings
MQTT_BROKER = "terracotta.lan"  # Change to your MQTT broker address
MQTT_PORT = 1883
MQTT_TOPIC = "can/bridge"
MQTT_CLIENT_ID = "can_receiver"


class MQTTToCANBridge:
    def __init__(self, source_topic, dest_channel):
        self.source_topic = source_topic
        self.dest_channel = dest_channel
        self.dest_bus = None
        self.mqtt_client = None
        self.running = False

    def initialize_can(self):
        try:
            # Initialize destination bus
            self.dest_bus = can.interface.Bus(
                channel=self.dest_channel,
                bustype='socketcan'
            )
        except Exception as e:
            logger.error(f"Failed to initialize CAN buses: {e}")
            raise

    def initialize_mqtt(self, publish=True):
        self.mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION1, userdata=MQTT_CLIENT_ID)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.running = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
            client.subscribe(MQTT_TOPIC)
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages and send to CAN"""
        try:
            # Parse the JSON message
            payload = json.loads(msg.payload.decode())
            # Reconstruct CAN message
            can_msg = can.Message(
                arbitration_id=payload['id'],
                data=bytes.fromhex(payload['data']),
                is_extended_id=payload['is_extended_id']
            )
            # Send to CAN interface
            self.dest_bus.send(can_msg)
            logger.info(f"Sent to {self.dest_channel}: ID={hex(can_msg.arbitration_id)}, Data={can_msg.data.hex()}")

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

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
            logger.error(f"Failed to connect to MQTT: {e}")

        # Start MQTT loop in a separate thread
        self.mqtt_client.loop_start()

        logger.info("CAN-MQTT bridge started. Press Ctrl+C to stop.")

        try:
            while self.running:
                time.sleep(5)  # Prevent busy-waiting
        except KeyboardInterrupt:
            logger.info("\nBridge stopped by user")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        self.dest_bus.shutdown()