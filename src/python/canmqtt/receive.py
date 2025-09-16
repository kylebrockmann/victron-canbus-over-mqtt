from canmqtt.adapters.virtual.virtual_can_adapter import VirtualCanAdapter
from canmqtt.interface.can_monitor import CanInterfaceMonitor
from canmqtt.interface.virtual_socketcan.configure import create_virtual_can_interface
from canmqtt.mqtt.managed_mqtt import ManagedMQTTClient
from canmqtt.util.logger import logger

if __name__ == '__main__':
    print("Running MQTT bridge in receive mode...")
    managed_client = ManagedMQTTClient("terracotta.lan", 1883)
    if managed_client.loop_until_ready():
        logger.info("MQTT client is ready")
    can_monitor = CanInterfaceMonitor("vcan0")
    if not can_monitor.interface_exists:
        create_virtual_can_interface("vcan0")
    can_monitor.loop_until_ready()
    adapter = VirtualCanAdapter("vcan0")
    if not adapter.check_if_up():
        raise RuntimeError("Virtual CAN interface is not up.")
    can_bridge = MQTTToCANBridge("can/bridge", "vcan0")
    can_bridge.run()