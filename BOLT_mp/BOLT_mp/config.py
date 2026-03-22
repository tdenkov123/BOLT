WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

BROKER_DISCOVERY_ENABLED = True
BROKER_MDNS_NAME = "mqtt"          # resolves as mqtt.local via mDNS
BROKER_DISCOVERY_TIMEOUT_MS = 3000 # ms to wait for each mDNS query attempt
BROKER_DISCOVERY_RETRIES = 3       # attempts before falling back

BROKER_HOST = "192.168.1.19"       # fallback IP if discovery is disabled or fails
BROKER_PORT = 1883
CLIENT_ID = "esp32-engine-01"
