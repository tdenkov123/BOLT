import network
import time

from config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    BROKER_DISCOVERY_ENABLED,
    BROKER_HOST,
    BROKER_PORT,
)

RESOLVED_BROKER_HOST = str(BROKER_HOST)
RESOLVED_BROKER_PORT = int(BROKER_PORT)

_READY = False

_STA_CONNECTING = 1001


def _wait_wifi(wlan, max_s: float) -> None:
    deadline = time.ticks_ms() + int(max_s * 1000)
    while time.ticks_diff(deadline, time.ticks_ms()) > 0:
        if wlan.isconnected():
            return
        try:
            st = wlan.status()
        except Exception:
            st = -1
        if st in (201, 202, 203):
            return
        time.sleep_ms(250)


def init() -> None:
    global RESOLVED_BROKER_HOST, RESOLVED_BROKER_PORT, _READY
    if _READY:
        return

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print("Wi-Fi already connected:", wlan.ifconfig())
    else:
        try:
            st = wlan.status()
        except Exception:
            st = -1
        if st == _STA_CONNECTING:
            print("Wi-Fi: waiting for join in progress ...")
            _wait_wifi(wlan, 25.0)

        if wlan.isconnected():
            print("Wi-Fi connected:", wlan.ifconfig())
        else:
            print("Connecting to Wi-Fi ...")
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            _wait_wifi(wlan, 25.0)
            if wlan.isconnected():
                print("Wi-Fi connected:", wlan.ifconfig())
            else:
                print(
                    "Wi-Fi connection FAILED — check SSID / password; status=",
                    wlan.status(),
                )

    if wlan.isconnected() and BROKER_DISCOVERY_ENABLED:
        from mdns_discovery import discover_broker

        h, p = discover_broker()
        RESOLVED_BROKER_HOST = str(h)
        RESOLVED_BROKER_PORT = int(p)
    else:
        RESOLVED_BROKER_HOST = str(BROKER_HOST)
        RESOLVED_BROKER_PORT = int(BROKER_PORT)

    print(
        "[bolt_net] MQTT target:",
        RESOLVED_BROKER_HOST,
        ":",
        RESOLVED_BROKER_PORT,
        "(use PC LAN IP — not localhost)",
    )
    _READY = True
