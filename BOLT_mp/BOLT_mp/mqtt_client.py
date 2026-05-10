import time
from umqtt.robust import MQTTClient


class BoltMQTTClient:
    def __init__(self, client_id, broker_host, broker_port=1883):
        self._broker_host = str(broker_host)
        self._broker_port = int(broker_port)
        self._callbacks = {}
        self._client = MQTTClient(
            client_id,
            self._broker_host,
            port=self._broker_port,
            keepalive=60,
        )
        self._client.set_callback(self._dispatch)
        self._connected = False
        self._backoff_ms = 1000
        self._next_try_tick = 0

    def _now(self):
        return time.ticks_ms()

    def _can_try_reconnect(self):
        return time.ticks_diff(self._next_try_tick, self._now()) <= 0

    def _schedule_backoff(self):
        self._next_try_tick = time.ticks_add(self._now(), self._backoff_ms)
        self._backoff_ms = min(self._backoff_ms * 2, 30_000)

    def _resubscribe_all(self):
        for topic in self._callbacks:
            print("[MQTT] Subscribing to", topic)
            self._client.subscribe(topic.encode())

    def connect(self):
        print("[MQTT] Connecting to", self._broker_host, "port", self._broker_port, "...")
        self._client.connect()
        self._connected = True
        self._backoff_ms = 1000
        self._next_try_tick = 0
        print("[MQTT] Connected")
        self._resubscribe_all()

    def subscribe(self, topic, callback):
        self._callbacks[topic] = callback
        if self._connected:
            print("[MQTT] Subscribing to", topic)
            self._client.subscribe(topic.encode())

    def publish(self, topic, value):
        if isinstance(value, str):
            value = value.encode("utf-8")
        if not self._connected:
            print("[MQTT] publish skipped (not connected); will retry after reconnect")
            return
        try:
            self._client.publish(topic.encode(), value)
        except Exception as e:
            print("[MQTT] publish error:", e)
            self._connected = False
            self._schedule_backoff()

    def poll(self):
        if not self._connected:
            if not self._can_try_reconnect():
                return
            self._attempt_reconnect()
            return
        try:
            self._client.check_msg()
        except Exception as e:
            print("[MQTT] poll error:", e)
            self._connected = False
            self._schedule_backoff()

    def _attempt_reconnect(self):
        try:
            print("[MQTT] Reconnecting ...")
            self._client.reconnect()
            self._connected = True
            self._backoff_ms = 1000
            self._next_try_tick = 0
            print("[MQTT] Reconnected")
            self._resubscribe_all()
        except Exception as e:
            print("[MQTT] Reconnect failed:", e, "| next retry in", self._backoff_ms, "ms")
            self._schedule_backoff()

    def _dispatch(self, topic_bytes, payload_bytes):
        topic = topic_bytes.decode("utf-8")
        value = payload_bytes.decode("utf-8")
        print("[MQTT] Message on", topic, "=", value)
        cb = self._callbacks.get(topic)
        if cb is not None:
            cb(value)
        else:
            print("[MQTT] No callback registered for topic", topic)
