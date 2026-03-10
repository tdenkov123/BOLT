import time
from umqtt.robust import MQTTClient


class BoltMQTTClient:
    def __init__(self, client_id, broker_host, broker_port=1883):
        self._broker_host = broker_host
        self._broker_port = broker_port
        self._callbacks = {}
        self._client = MQTTClient(
            client_id,
            broker_host,
            port=broker_port,
            keepalive=60,
        )
        self._client.set_callback(self._dispatch)
        self._connected = False

    def connect(self):
        print("[MQTT] Connecting to", self._broker_host, "port", self._broker_port, "...")
        self._client.connect()
        self._connected = True
        print("[MQTT] Connected")
        for topic in self._callbacks:
            print("[MQTT] Subscribing to", topic)
            self._client.subscribe(topic.encode())

    def subscribe(self, topic, callback):
        self._callbacks[topic] = callback
        if self._connected:
            print("[MQTT] Subscribing to", topic)
            self._client.subscribe(topic.encode())

    def publish(self, topic, value):
        if isinstance(value, str):
            value = value.encode("utf-8")
        try:
            self._client.publish(topic.encode(), value)
        except Exception:
            self._reconnect()
            self._client.publish(topic.encode(), value)

    def poll(self):
        try:
            self._client.check_msg()
        except Exception as e:
            print("[MQTT] poll error:", e, "— reconnecting ...")
            self._reconnect()

    def _dispatch(self, topic_bytes, payload_bytes):
        topic = topic_bytes.decode("utf-8")
        value = payload_bytes.decode("utf-8")
        print("[MQTT] Message on", topic, "=", value)
        cb = self._callbacks.get(topic)
        if cb is not None:
            cb(value)
        else:
            print("[MQTT] No callback registered for topic", topic)

    def _reconnect(self):
        self._connected = False
        while True:
            try:
                print("[MQTT] Reconnecting ...")
                self._client.reconnect()
                self._connected = True
                print("[MQTT] Reconnected")
                for topic in self._callbacks:
                    print("[MQTT] Re-subscribing to", topic)
                    self._client.subscribe(topic.encode())
                return
            except Exception as e:
                print("[MQTT] Reconnect failed:", e, "— retrying in 5 s")
                time.sleep(5)
