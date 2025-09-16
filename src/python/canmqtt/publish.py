from canmqtt.can_bridge.can_to_mqtt import CANToMQTTBridge
from canmqtt.adapters.can_adapter_control import CanAdapter
from canmqtt.can_bridge.interfaces.can_message_source import CANMessageSource
from canmqtt.interface.can_monitor import CanInterfaceMonitor
from canmqtt.mqtt.managed_mqtt import ManagedMQTTClient
from canmqtt.mqtt.mqtt_message_destination import MQTTMessageDestination
from canmqtt.queuing.canbus_queue import CANBusQueue
from canmqtt.util.logger import logger

# This old message is kept for reference, but the new architecture uses
# a more modular approach with queues and separate components.
def old_method():
    print("Running MQTT bridge in publish mode...")
    adapter = CanAdapter("can0")
    adapter.assert_parameters()
    adapter.assert_up()
    if not adapter.check_if_up():
        raise RuntimeError("CAN interface is not up.")
    can_bridge = CANToMQTTBridge("can0", "can/bridge")
    can_bridge.run()
    pass

if __name__ == '__main__':
    managed_client = ManagedMQTTClient("terracotta.lan", 1883)
    if managed_client.loop_until_ready():
        logger.info("MQTT client is ready")
    queue = CANBusQueue()
    message_destination = MQTTMessageDestination("can/bridge",queue, managed_client)
    CanInterfaceMonitor("can0").loop_until_ready()
    can_source = CANMessageSource("can0", queue)
    queue.start_message_loops()
    can_source.run()
