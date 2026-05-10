import time
from mqtt_client import BoltMQTTClient

from config import CLIENT_ID
import bolt_net

bolt_net.init()
from bolt_net import RESOLVED_BROKER_HOST, RESOLVED_BROKER_PORT


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
    print("[ESP->BOLT] published ENGINE_STATUS", "ACK:" + str(angle))


client = BoltMQTTClient(CLIENT_ID, RESOLVED_BROKER_HOST, RESOLVED_BROKER_PORT)
client.connect()
client.subscribe("ENGINE_DEGREES", on_engine_degrees)

print(
    "[ESP] MQTT subscribed on",
    RESOLVED_BROKER_HOST,
    ":",
    RESOLVED_BROKER_PORT,
    "topics: ENGINE_DEGREES → ENGINE_STATUS ACK (client id",
    CLIENT_ID,
    ")",
)
print("[ESP] If BOLT sees no [RX], check this USB serial log — no lines here ⇒ ESP not receiving.")

_heartbeat = 0
while True:
    client.poll()
    _heartbeat += 1
    if _heartbeat >= 500:
        print("[MAIN] loop alive, waiting for messages ...")
        _heartbeat = 0
    time.sleep_ms(10)
