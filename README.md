# BOLT — Block-Oriented Lightweight Tasker

BOLT is a lightweight IEC 61499-inspired runtime that executes **Function Blocks (FBs)** connected by event and data connections. It runs on a standard PC (Python 3) and communicates with embedded devices over MQTT.

The included example drives an ESP32 running MicroPython: the PC sends engine angle commands over MQTT and the ESP32 acknowledges them back.

---

## Repository structure

```
BOLT/
├── core/               # Runtime engine (device, resource, FB loader, MQTT client)
│   └── FBs/            # Built-in function blocks (START, E_CYCLE, MQTT_*, ...)
├── BOLT_mp/BOLT_mp/    # MicroPython firmware for the ESP32
├── docker/             # Mosquitto broker config
├── config.py           # Host-side configuration (broker host/port)
├── main.py             # Example application
├── requirements.txt    # Python dependencies
├── scripts/            # Operational helpers only
│   ├── setup_venv.sh       # Venv creation + dependency installation
│   ├── deploy_mp_script.sh # Upload MicroPython firmware to the ESP32
│   └── mp_debug_esp.sh     # Runs tests/mp_debug_esp_device.py via mpremote
├── tests/              # MQTT / ESP integration probes (run from repo root with venv)
│   ├── mqtt_roundtrip_smoke.py   # Broker smoke test without an ESP32
│   ├── mqtt_engine_watch.py      # Log ENGINE_* topics to the terminal
│   ├── esp32_mqtt_stability_probe.py  # Long-run PC↔ESP stability (BOLT FBs + real ESP ACKs)
│   └── mp_debug_esp_device.py    # MicroPython one-shot network/broker sanity (ESP only)
```

---

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (for the MQTT broker)
- An ESP32 flashed with MicroPython (for the embedded side)

---

## Host-side setup

### 1. Create the virtual environment and install dependencies

```bash
source ./scripts/setup_venv.sh
```

This creates `.venv/`, activates it, upgrades pip, and installs everything in `requirements.txt` (including `mpremote`).

Alternatively, do it manually:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure the broker

Edit `config.py` in the project root:

```python
BROKER_HOST = "localhost"   # or your broker's IP
BROKER_PORT = 1883
```

### 3. Start the MQTT broker with auto-discovery

To enable ESP32 devices to auto-discover the broker via mDNS on the local network, run:

```bash
./setup.sh
```

This script:
- Installs `avahi-daemon` if needed (required for mDNS on Linux)
- Registers the broker as a discoverable service (`mqtt.local`)
- Starts the Docker Compose broker

**Alternatively**, start manually without auto-discovery:

```bash
docker compose up -d
```

### 4. Run BOLT

```bash
python main.py
```

As the example, BOLT connects to the broker, starts the cyclic engine, and begins publishing `ENGINE_DEGREES` every 500 ms while listening for `ENGINE_STATUS` acknowledgements.

Lines printed as `[TX] ... published` only appear after `MQTT_PUBLISH` reports success for that send (QoS 0: accepted by the client library / handed to the TCP stack), so you should **not** see them if the broker is down and `INIT` never completed. To verify the broker path end-to-end without the ESP32: `.venv/bin/python tests/mqtt_roundtrip_smoke.py` (optional: `--broker-host HOST --broker-port 1883`; with `docker compose up -d`).

> **Performance tip:** BOLT uses one thread per event chain. For maximum throughput on CPython, disable the GIL (Python 3.13+ free-threaded build).

---

## ESP32 / MicroPython setup

### 1. Configure the device

Edit configurations in `BOLT_mp/BOLT_mp/config.py`:

```python
WIFI_SSID           = "your-wifi-ssid"
WIFI_PASSWORD       = "your-wifi-password"

# After Wi-Fi connects, run discovery once (fast IP probe + optional mDNS)
BROKER_DISCOVERY_ENABLED = True
# Keep False on ESP32-C6 unless you have verified _thread + lwIP + USB (avoids Guru Meditation / raw REPL issues).
BROKER_DISCOVERY_USE_THREAD = False
# Dangerous on ESP32 lwIP: socket.getaddrinfo("*.local") can block and break mpremote.
BROKER_MDNS_LOOKUP_ENABLED = False
BROKER_MDNS_NAME = "mqtt"          # only used when BROKER_MDNS_LOOKUP_ENABLED is True
BROKER_DISCOVERY_TIMEOUT_MS = 3000 # TCP probe timeout cap (and pacing hint)
BROKER_DISCOVERY_RETRIES = 3       # mDNS resolve rounds (only when mDNS lookup enabled)

# Broker LAN IP — used when discovery is off, as the fast path when it answers, and as fallback
BROKER_HOST         = "192.168.x.x"
BROKER_PORT         = 1883
CLIENT_ID           = "esp32-engine-01"

# `main.py` waits up to this many ms for async discovery (see `bolt_net.await_discovery`).
BROKER_DISCOVERY_WAIT_MS = 15000
```

**Broker resolution notes:**
- `boot.py` calls `bolt_net.init()`: Wi‑Fi, baseline `RESOLVED_*` = `BROKER_*`. When discovery is on, either **`BROKER_DISCOVERY_USE_THREAD`** starts **`discover_broker()`** in **`_thread`**, or (default) discovery is **deferred** to **`main.py`**’s **`bolt_net.await_discovery()`** on the **main** task.
- Threaded mode: **`await_discovery()`** polls with **`sleep_ms`** until the worker finishes or **`BROKER_DISCOVERY_WAIT_MS`** elapses.
- Default (no thread): **`await_discovery()`** runs **`discover_broker()`** once on the main task (still may block on long `getaddrinfo` if mDNS lookup is enabled).
- **`mdns_discovery`**: fast IP probe, optional `*.local` when `BROKER_MDNS_LOOKUP_ENABLED`, retries, fallback.
- If `BROKER_DISCOVERY_ENABLED = False`, the ESP uses `BROKER_HOST`/`BROKER_PORT` only.

**Finding the correct broker IP on your LAN**

The ESP talks to **`BROKER_HOST` over Wi‑Fi**, not to `localhost`. If Mosquitto runs in Docker on your laptop, **`BROKER_HOST` must be that laptop’s LAN address** (e.g. `192.168.1.x`), the same subnet as the ESP (check the ESP serial line: `wlan.ifconfig()` / `Wi-Fi connected: ('192.168.x.y', …)`).

1. **On the PC that runs Mosquitto / Docker:**  
   Linux: `ip -4 route get 1.1.1.1 | awk '{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}'` or `hostname -I` (pick the Wi‑Fi or Ethernet IPv4).  
   Windows / macOS: `ipconfig` / System Settings → network — IPv4 for the adapter on that LAN.
2. **Sanity check from any device on the same LAN:**  
   `nc -vz THAT_IP 1883` or `mqtt pub -h THAT_IP …` — must succeed when Docker maps `1883:1883` and `listener 1883 0.0.0.0` is set.
3. **If the PC’s LAN IP changes (DHCP):** use a DHCP reservation in the router, or keep discovery + a stable `BROKER_HOST` probe list, or enable mDNS only if your network resolves `mqtt.local` reliably.

And in `BOLT_mp/.micropythonrc`

```json
{
  "upload": {
    "port": "/dev/ttyACM0",
    "baud": 460800
  },
  "serial": {
    "port": "/dev/ttyACM0",
    "baud": 460800
  },
  "ignore": {
    "extensions": [
      ".micropythonrc"
    ],
    "directories": [
      ".vscode"
    ]
  },
  "tools": {
    "ampy": "/home/user/.local/bin/ampy",
    "rshell": "/home/user/.local/bin/rshell"
  }
}
```


### 2. Flash the firmware to the ESP32

Connect the ESP32 via USB, then run:

```bash
bash scripts/deploy_mp_script.sh
```

This copies `boot.py`, `main.py`, `mqtt_client.py`, `bolt_net.py`, `mdns_discovery.py`, and `config.py` to the device, removes a stale onboard `agent_debug_mp.py` if present, and resets. The default port is `/dev/ttyACM0` — override with `PORT=/dev/ttyUSB0 bash scripts/deploy_mp_script.sh` if needed.

---

## Built-in Function Blocks

| FB | Description |
|---|---|
| `START` | Fires a single `START` event on resource initialisation |
| `E_CYCLE` | Periodic timer — fires `EO` every `DT` milliseconds |
| `MQTT_PUBLISH` | Publishes a value to an MQTT topic |
| `MQTT_SUBSCRIBE` | Subscribes to an MQTT topic and fires `IND` on each message |
| `PRINT_CONSOLE` | Prints the `IN` data variable to stdout |
| `ADD_2` | Adds two integers |
| `INT2INT` | Integer passthrough / type cast |
| `STRING2STRING` | String passthrough |

---

## License

See [LICENSE](LICENSE).