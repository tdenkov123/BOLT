import time
from mqtt_client import BoltMQTTClient

from config import CLIENT_ID
from boot import RESOLVED_BROKER_HOST, RESOLVED_BROKER_PORT


def set_engine_angle(degrees):
    print("ENGINE ->", degrees, "degrees")


def on_engine_degrees(value):
    try:
        angle = int(value)
    except ValueError:
        print("Bad ENGINE_DEGREES value:", value)
        return

    set_engine_angle(angle)

    client.publish("ENGINE_STATUS", "ACK:" + str(angle))


client = BoltMQTTClient(CLIENT_ID, RESOLVED_BROKER_HOST, RESOLVED_BROKER_PORT)
client.connect()
client.subscribe("ENGINE_DEGREES", on_engine_degrees)

print("Connected to broker, listening for ENGINE_DEGREES ...")

_heartbeat = 0
while True:
    client.poll()
    _heartbeat += 1
    if _heartbeat >= 500:
        print("[MAIN] loop alive, waiting for messages ...")
        _heartbeat = 0
    time.sleep_ms(10)
