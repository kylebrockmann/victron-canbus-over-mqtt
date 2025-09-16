import logging
import os
import socket


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if os.environ.get("LOG_LEVEL") == "debug":
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

