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
├── scripts/
│   ├── setup_venv.sh       # Venv creation + dependency installation script
│   └── deploy_mp_script.sh # Upload MicroPython firmware to the ESP32
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

> **Performance tip:** BOLT uses one thread per event chain. For maximum throughput on CPython, disable the GIL (Python 3.13+ free-threaded build).

---

## ESP32 / MicroPython setup

### 1. Configure the device

Edit configurations in `BOLT_mp/BOLT_mp/config.py`:

```python
WIFI_SSID           = "your-wifi-ssid"
WIFI_PASSWORD       = "your-wifi-password"

# Enable auto-discovery of the broker via mDNS
BROKER_DISCOVERY_ENABLED = True
BROKER_MDNS_NAME = "mqtt"          # resolves as mqtt.local via mDNS
BROKER_DISCOVERY_TIMEOUT_MS = 3000 # ms to wait for each mDNS query attempt
BROKER_DISCOVERY_RETRIES = 3       # attempts before falling back

# Fallback if discovery fails or is disabled
BROKER_HOST         = "192.168.x.x"   # fallback IP if discovery is disabled or fails
BROKER_PORT         = 1883
CLIENT_ID           = "esp32-engine-01"
```

**Auto-discovery notes:**
- The broker must be running on a machine with mDNS support (Linux with `avahi-daemon`)
- Use `./setup.sh` to start the broker with mDNS advertised
- If `BROKER_DISCOVERY_ENABLED = False`, the ESP32 will connect directly to `BROKER_HOST`
- If discovery fails, the device automatically falls back to the hardcoded `BROKER_HOST`

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

This copies `boot.py`, `main.py`, `mqtt_client.py`, and `config.py` to the device and resets it. The default port is `/dev/ttyACM0` — edit the `PORT` variable in the script if yours differs.

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