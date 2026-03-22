import time
import network

from config import (
    BROKER_MDNS_NAME,
    BROKER_DISCOVERY_TIMEOUT_MS,
    BROKER_DISCOVERY_RETRIES,
    BROKER_HOST,
    BROKER_PORT,
)


def discover_broker():
    mdns = network.mDNS()
    mdns.start(BROKER_MDNS_NAME, "_mqtt._tcp")

    for attempt in range(1, BROKER_DISCOVERY_RETRIES + 1):
        print(
            "[mDNS] Discovery attempt",
            attempt,
            "/",
            BROKER_DISCOVERY_RETRIES,
            "...",
        )
        try:
            results = mdns.query(BROKER_DISCOVERY_TIMEOUT_MS, "_mqtt", "_tcp")
            if results:
                ip, port = _pick_best(results)
                print("[mDNS] Found broker at", ip, "port", port)
                mdns.stop()
                return ip, port
        except Exception as e:
            print("[mDNS] Query error:", e)

        time.sleep_ms(500)

    mdns.stop()
    print(
        "[mDNS] Discovery failed — falling back to",
        BROKER_HOST,
        "port",
        BROKER_PORT,
    )
    return BROKER_HOST, BROKER_PORT


def _pick_best(results):
    for r in results:
        addr = r.get("addr") or r.get("ip")
        port = r.get("port", BROKER_PORT)
        if addr:
            return addr, int(port)
    return BROKER_HOST, BROKER_PORT
