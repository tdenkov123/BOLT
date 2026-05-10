"""Wi-Fi + MQTT broker resolution. Idempotent init(); discovery can run async (_thread) or deferred sync."""

import network
import time

from config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    BROKER_DISCOVERY_ENABLED,
    BROKER_DISCOVERY_USE_THREAD,
    BROKER_DISCOVERY_WAIT_MS,
    BROKER_HOST,
    BROKER_PORT,
)

RESOLVED_BROKER_HOST = str(BROKER_HOST)
RESOLVED_BROKER_PORT = int(BROKER_PORT)

_READY = False
_pending_async_discovery = False
_pending_sync_discovery = False
_discovery_result = None

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


def _discovery_worker():
    """Runs in helper thread when BROKER_DISCOVERY_USE_THREAD is True."""
    global _discovery_result
    try:
        from mdns_discovery import discover_broker

        h, p = discover_broker()
        _discovery_result = (str(h), int(p))
    except Exception as e:
        print("[bolt_net] discovery worker error:", e)
        _discovery_result = (str(BROKER_HOST), int(BROKER_PORT))


def init() -> None:
    """Wi-Fi setup; baseline broker = config. Optional background thread for discovery."""
    global RESOLVED_BROKER_HOST, RESOLVED_BROKER_PORT, _READY
    global _pending_async_discovery, _pending_sync_discovery, _discovery_result

    if _READY:
        return

    _pending_async_discovery = False
    _pending_sync_discovery = False
    _discovery_result = None

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

    RESOLVED_BROKER_HOST = str(BROKER_HOST)
    RESOLVED_BROKER_PORT = int(BROKER_PORT)

    if wlan.isconnected() and BROKER_DISCOVERY_ENABLED:
        use_bg_thread = False
        _thmod = None
        if bool(BROKER_DISCOVERY_USE_THREAD):
            try:
                import _thread as _thmod
            except ImportError:
                _thmod = None
            use_bg_thread = _thmod is not None

        if use_bg_thread and _thmod is not None:
            _discovery_result = None
            _pending_async_discovery = True
            _thmod.start_new_thread(_discovery_worker, ())
            print(
                "[bolt_net] MQTT discovery running in helper thread;",
                "main will await",
                int(BROKER_DISCOVERY_WAIT_MS),
                "ms then connect",
            )
        else:
            _pending_sync_discovery = True
            print(
                "[bolt_net] broker discovery deferred to await_discovery() "
                "(USE_THREAD=False; avoids _thread/lwIP instability on some ESP32 builds)",
            )

    else:
        print(
            "[bolt_net] MQTT target:",
            RESOLVED_BROKER_HOST,
            ":",
            RESOLVED_BROKER_PORT,
            "(discovery off or Wi-Fi down — use PC LAN IP — not localhost)",
        )

    _READY = True


def await_discovery(timeout_ms=None):
    """Call from main.py before MQTT.connect. Yields when using threaded discovery."""
    global RESOLVED_BROKER_HOST, RESOLVED_BROKER_PORT, _pending_async_discovery
    global _pending_sync_discovery

    if _pending_sync_discovery:
        from mdns_discovery import discover_broker

        print("[bolt_net] running discover_broker() on main task ...")
        try:
            h, p = discover_broker()
            RESOLVED_BROKER_HOST = str(h)
            RESOLVED_BROKER_PORT = int(p)
        except Exception as e:
            print("[bolt_net] discovery failed:", e)
        _pending_sync_discovery = False
        print(
            "[bolt_net] MQTT target:",
            RESOLVED_BROKER_HOST,
            ":",
            RESOLVED_BROKER_PORT,
            "(discovery complete)",
        )
        return

    if not _pending_async_discovery:
        return

    if timeout_ms is None:
        timeout_ms = int(BROKER_DISCOVERY_WAIT_MS)

    deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
    poll_ms = 40

    while _discovery_result is None:
        if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
            print(
                "[bolt_net] discovery wait exceeded",
                timeout_ms,
                "ms — using fallback",
                RESOLVED_BROKER_HOST + ":" + str(RESOLVED_BROKER_PORT),
            )
            _pending_async_discovery = False
            return
        time.sleep_ms(poll_ms)

    h, p = _discovery_result
    RESOLVED_BROKER_HOST, RESOLVED_BROKER_PORT = h, int(p)
    _pending_async_discovery = False

    print(
        "[bolt_net] MQTT target:",
        RESOLVED_BROKER_HOST,
        ":",
        RESOLVED_BROKER_PORT,
        "(discovery complete)",
    )
