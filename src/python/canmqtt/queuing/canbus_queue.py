import sys
import signal
import json
import queue
import time
from queue import Queue
import can
from paho.mqtt.client import MQTTMessage
import threading
from canmqtt.util.logger import logger as log

class TerminateProtected:
    killed = False

    def _handler(self, signum, frame):
        log.info (f'Caught exit SIGNAL {signum}, this instance will now shutdown, goodbye... ')
        self.killed = True
        sys.exit(0)

    def __enter__(self):
        self.old_sigint = signal.signal(signal.SIGINT, self._handler)
        self.old_sigterm = signal.signal(signal.SIGTERM, self._handler)

    def __exit__(self, type, value, traceback):
        if self.killed:
            sys.exit(0)
        signal.signal(signal.SIGINT, self.old_sigint)
        signal.signal(signal.SIGTERM, self.old_sigterm)

class CANBusQueue:
    def __init__(self):
        self.incoming_queue = Queue()
        self.outgoing_queue = Queue()
        self.publish_thread = None
        self.receive_thread = None
        self.publish_target = None
        self.receive_target = None

    def send_can_message(self, can_frame: can.Message):
        msg_dict = {
            'id': can_frame.arbitration_id,
            'data': can_frame.data.hex(),
            'is_extended_id': can_frame.is_extended_id
        }
        msg_body=json.dumps(msg_dict)
        self.outgoing_queue.put(msg_body)

    def receive_can_message(self, mqtt_bytes: MQTTMessage):
        payload = json.loads(mqtt_bytes.payload.decode())
        can_msg = can.Message(
            arbitration_id=payload['id'],
            data=bytes.fromhex(payload['data']),
            is_extended_id=payload['is_extended_id']
        )
        self.incoming_queue.put(can_msg)

    def publish_loop(self, publish_queue: Queue, timeout: float):
        log.info("Started publish thread...")
        if self.publish_target is None:
            log.info("No publish invocation target specified...")
        while True:
            if self.publish_target is not None:
                try:
                    can_json_body = publish_queue.get(True,timeout)
                    if can_json_body:
                        self.publish_target(can_json_body)
                except queue.Empty:
                    log.info("Publish queue is empty...")
                    time.sleep(5)
                    pass
            else:
                time.sleep(30)

    def receive_loop(self, receive_queue: Queue, timeout: float):
        log.info("Started receive thread...")
        if self.receive_target is None:
            log.info("No receive invocation target specified...")
        while True:
            if self.receive_target is not None:
                try:
                    can_frame = receive_queue.get(True,timeout)
                    if can_frame:
                        self.receive_target(can_frame)
                except queue.Empty:
                    log.info("Receive queue is empty...")
                    time.sleep(5)
                    pass
            else:
                time.sleep(30)

    def start_message_loops(self):
        with TerminateProtected():
            publish_thread = threading.Thread(target=self.publish_loop,
                                              args=(self.outgoing_queue, 5.0))
            publish_thread.daemon = True
            publish_thread.start()

            receive_thread = threading.Thread(target=self.receive_loop,
                                              args=(self.incoming_queue, 5.0))
            receive_thread.daemon = True
            receive_thread.start()