import time
import paho.mqtt.client as mqtt
from util.logger import logger as log

def check_if_port_open(host, port):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((host, port))
        return True
    except socket.error:
        return False
    finally:
        sock.close()

def poll_mqtt_version(outer_client: mqtt.Client, host, port, timeout=5):
    def on_connect(inner_client, userdata, flags, rc, properties=None):
        setattr(inner_client, 'mqtt_version', None)
        if properties:
            inner_client.mqtt_version = "5.0"
        else:
            inner_client.mqtt_version = "3.1"

    def on_disconnect(inner_client: mqtt.Client, userdata, rc, properties=None):
        inner_client.loop_stop()
        inner_client.on_connect = None
        inner_client.on_disconnect = None
        inner_client.on_error = None

    def on_error(inner_client: mqtt.Client, userdata, rc, properties=None, things=None):
        log.info(f"Connection failed: {rc}")
        inner_client.loop_stop()

    outer_client.on_connect = on_connect
    outer_client.on_disconnect = on_disconnect
    outer_client.on_disconnect = on_error

    try:
        # Attempt to connect to the server
        outer_client.connect(host, port, keepalive=timeout)
        outer_client.loop(100)
        if hasattr(outer_client, 'mqtt_version'):
            log.info(f"MQTT version: {outer_client.mqtt_version}")
            return outer_client.mqtt_version
    except Exception as e:
        log.info(f"Error connecting to {host}:{port}: {str(e)}")


class ManagedMQTTClient:
    def __init__(self, host, port, client_id = "managed_mqtt_client", timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client_id = client_id
        self.client = mqtt.Client()

    def poll_version(self):
        return poll_mqtt_version(self.client, self.host, self.port, self.timeout)

    def loop_until_ready(self):
        self.initialize()
        while not check_if_port_open(self.host, self.port):
            log.info(f"Waiting for MQTT broker at {self.host}:{self.port}...")
            time.sleep(5)
        log.info(f"MQTT broker at {self.host}:{self.port} is ready.")
        while not self.poll_version():
            log.info(f"Waiting for MQTT version response from {self.host}:{self.port}...")
            time.sleep(5)
        log.info(f"MQTT version response received from {self.host}:{self.port}.")
        return True

    def initialize(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=self.client_id)

    def connect(self):
        if self.loop_until_ready():
            log.info(f"Connecting to MQTT broker at {self.host}:{self.port}...")

        self.client.connect(self.host, self.port, keepalive=self.timeout)
        self.client.loop_start()
        log.info(f"Connected to MQTT broker at {self.host}:{self.port}")

    def publish(self, topic, payload):
        self.client.publish(topic, payload)
        log.info(f"Published to {topic}: {len(payload)}")





