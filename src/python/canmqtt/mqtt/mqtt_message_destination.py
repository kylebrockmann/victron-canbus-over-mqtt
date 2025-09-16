import can

from mqtt.managed_mqtt import ManagedMQTTClient
from util.logger import logger as log
from queuing.canbus_queue import CANBusQueue


class MQTTMessageDestination:
    def __init__(self, destination_topic : str, message_queue: CANBusQueue, mqtt_client : ManagedMQTTClient ):
        self.destination_topic = destination_topic
        self.message_queue = message_queue
        self.mqtt_client = mqtt_client
        self.initialize_mqtt()

    def publish(self, message: str):
        try:
            self.mqtt_client.publish(self.destination_topic, message)
        except Exception as e:
            log.error(f"Failed to publish message: {e}")

    def initialize_mqtt(self):
        try:
            self.message_queue.publish_target = self.publish
        except Exception as e:
            print(f"Failed to initialize MQTT target: {e}")
            raise


