#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from config import BROKER_HOST, BROKER_PORT

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("Install paho-mqtt (e.g. pip install -r requirements.txt)")
    sys.exit(2)


def _client(client_id: str) -> mqtt.Client:
    try:
        return mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION1,
            client_id=client_id,
            clean_session=True,
        )
    except AttributeError:
        return mqtt.Client(client_id=client_id, clean_session=True)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--broker-host", default=None, help="default: config.BROKER_HOST")
    p.add_argument("--broker-port", type=int, default=None, help="default: config.BROKER_PORT")
    args = p.parse_args()
    host = str(args.broker_host if args.broker_host is not None else BROKER_HOST)
    port = int(args.broker_port if args.broker_port is not None else BROKER_PORT)
    got = []
    lock = threading.Lock()

    listener = _client("bolt-smoke-listener")

    def on_listener_msg(_c, _u, msg: mqtt.MQTTMessage) -> None:
        pl = msg.payload.decode("utf-8", errors="replace")
        print("[smoke] ENGINE_STATUS <-", repr(pl))
        with lock:
            got.append(pl)

    def on_listener_connect(cli, userdata, flags, rc) -> None:  # noqa: ARG001
        if rc == 0:
            cli.subscribe("ENGINE_STATUS")
        else:
            print("[smoke] listener on_connect rc=", rc)

    listener.on_connect = on_listener_connect
    listener.on_message = on_listener_msg
    try:
        listener.connect(host, port, keepalive=30)
    except OSError as exc:
        print(f"[smoke] connect failed {host}:{port} -> {exc}")
        return 1
    listener.loop_start()
    time.sleep(0.4)

    esp = _client("bolt-smoke-esp")

    def on_esp_degrees(_cli, _u, msg: mqtt.MQTTMessage) -> None:
        raw = msg.payload.decode("utf-8", errors="replace")
        print("[smoke] ENGINE_DEGREES <-", repr(raw))
        try:
            angle = int(raw)
        except ValueError:
            angle = -1
        esp.publish("ENGINE_STATUS", f"ACK:{angle}")

    def on_esp_connect(cli, userdata, flags, rc) -> None:  # noqa: ARG001
        if rc == 0:
            cli.subscribe("ENGINE_DEGREES")
        else:
            print("[smoke] esp on_connect rc=", rc)

    esp.on_connect = on_esp_connect
    esp.on_message = on_esp_degrees
    try:
        esp.connect(host, port, keepalive=30)
    except OSError as exc:
        print(f"[smoke] esp connect failed -> {exc}")
        listener.loop_stop()
        return 1
    esp.loop_start()
    time.sleep(0.4)

    producer = _client("bolt-smoke-producer")
    try:
        producer.connect(host, port, keepalive=30)
    except OSError as exc:
        print(f"[smoke] producer connect failed -> {exc}")
        esp.loop_stop()
        listener.loop_stop()
        return 1
    producer.loop_start()
    time.sleep(0.3)

    print("[smoke] publish ENGINE_DEGREES = 42")
    producer.publish("ENGINE_DEGREES", "42")

    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        time.sleep(0.05)
        with lock:
            if got and any(x.startswith("ACK:") for x in got):
                print("[smoke] PASS")
                producer.loop_stop()
                esp.loop_stop()
                listener.loop_stop()
                producer.disconnect()
                esp.disconnect()
                listener.disconnect()
                return 0

    print("[smoke] FAIL: no valid ENGINE_STATUS ACK (broker down or wrong host/port?)")
    producer.loop_stop()
    esp.loop_stop()
    listener.loop_stop()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
