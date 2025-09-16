import os

from can_bridge.mqtt_to_can import MQTToCANBridge
from adapters.virtual.virtual_can_adapter import VirtualCanAdapter
from interface.can_monitor import CanInterfaceMonitor
from interface.virtual_socketcan.configure import create_virtual_can_interface
from mqtt.managed_mqtt import ManagedMQTTClient
from util.logger import logger

if __name__ == '__main__':
    print("Running MQTT bridge in receive mode...")
    mqtt_host = os.environ.get("MQTT_HOST", "localhost")
    mqtt_port = int(os.environ.get("MQTT_PORT", 1883))
    managed_client = ManagedMQTTClient(mqtt_host, mqtt_port)
    if managed_client.loop_until_ready():
        logger.info("MQTT client is ready")
    can_monitor = CanInterfaceMonitor("vcan0")
    if not can_monitor.interface_exists:
        create_virtual_can_interface("vcan0")
    can_monitor.loop_until_ready()
    adapter = VirtualCanAdapter("vcan0")
    if not adapter.check_if_up():
        raise RuntimeError("Virtual CAN interface is not up.")
    can_bridge = MQTToCANBridge("can/bridge", "vcan0")
    can_bridge.run()