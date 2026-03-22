import network
import time
from config import WIFI_SSID, WIFI_PASSWORD, BROKER_DISCOVERY_ENABLED

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    print("Connecting to Wi-Fi ...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(10):
        if wlan.isconnected():
            break
        time.sleep(1)

if wlan.isconnected():
    print("Wi-Fi connected:", wlan.ifconfig())
else:
    print("Wi-Fi connection FAILED — check SSID / password")

if wlan.isconnected() and BROKER_DISCOVERY_ENABLED:
    from mdns_discovery import discover_broker
    RESOLVED_BROKER_HOST, RESOLVED_BROKER_PORT = discover_broker()
else:
    from config import BROKER_HOST, BROKER_PORT
    RESOLVED_BROKER_HOST, RESOLVED_BROKER_PORT = BROKER_HOST, BROKER_PORT
