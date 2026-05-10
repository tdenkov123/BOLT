#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from config import BROKER_HOST, BROKER_PORT

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("pip install paho-mqtt")
    sys.exit(2)


def _mk_client(client_id: str) -> mqtt.Client:
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
    c = _mk_client("bolt-engine-watch")

    def on_connect(cli, _u, _f, rc) -> None:  # noqa: ANN001
        if rc != 0:
            print("[watch] connect rc=", rc)
            return
        cli.subscribe("$SYS/broker/clients/connected")
        cli.subscribe("ENGINE_DEGREES")
        cli.subscribe("ENGINE_STATUS")

    counts = {"deg": 0, "sts": 0, "sys": 0}

    def on_message(_cli, _u, msg: mqtt.MQTTMessage) -> None:
        t = msg.topic
        pl = msg.payload.decode("utf-8", errors="replace")
        if t == "ENGINE_DEGREES":
            counts["deg"] += 1
            print(f"[watch] ENGINE_DEGREES #{counts['deg']:<6} payload={pl!r}")
        elif t == "ENGINE_STATUS":
            counts["sts"] += 1
            print(f"[watch] ENGINE_STATUS #{counts['sts']:<6} payload={pl!r}")
        elif t.endswith("clients/connected"):
            counts["sys"] += 1
            print(f"[watch] $SYS broker clients_connected = {pl!r}")
        else:
            print("[watch]", t, "=", repr(pl))

    c.on_connect = on_connect
    c.on_message = on_message

    print(f"[watch] broker {host}:{port} — Ctrl+C stop")
    try:
        c.connect(host, port, keepalive=30)
    except OSError as e:
        print("[watch] connect failed:", e)
        return 1
    c.loop_start()
    try:
        last = time.monotonic()
        while True:
            time.sleep(2.5)
            if time.monotonic() - last >= 60:
                print(
                    f"[watch] stats ENGINE_DEGREES={counts['deg']} ENGINE_STATUS={counts['sts']}"
                )
                last = time.monotonic()
    except KeyboardInterrupt:
        print(
            "[watch] done:",
            counts,
            "(if sts=0 while deg>0, ESP is not acknowledging on ENGINE_STATUS)",
        )
    finally:
        c.loop_stop()
        c.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
