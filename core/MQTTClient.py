from __future__ import annotations

import logging
import threading
from typing import Callable

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

_managers: dict[tuple[str, int], MQTTClientManager] = {}
_managers_lock = threading.Lock()


def get_client(host: str, port: int) -> MQTTClientManager:
    key = (host, port)
    with _managers_lock:
        if key not in _managers:
            _managers[key] = MQTTClientManager(host, port)
        return _managers[key]


class MQTTClientManager:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._callbacks: dict[str, list[Callable[[str], None]]] = {}
        self._lock = threading.Lock()
        try:
            self._client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION1,
                client_id="",
                clean_session=True,
            )
        except AttributeError:
            self._client = mqtt.Client(client_id="", clean_session=True)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        self._client.connect(host, port, keepalive=60)
        self._client.loop_start()

    def subscribe(self, topic: str, callback: Callable[[str], None]) -> None:
        with self._lock:
            if topic not in self._callbacks:
                self._callbacks[topic] = []
                self._client.subscribe(topic)
            self._callbacks[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[str], None]) -> None:
        with self._lock:
            if topic not in self._callbacks:
                return
            try:
                self._callbacks[topic].remove(callback)
            except ValueError:
                pass
            if not self._callbacks[topic]:
                del self._callbacks[topic]
                self._client.unsubscribe(topic)

    def publish(self, topic: str, payload: str) -> None:
        self._client.publish(topic, payload.encode("utf-8"))

    def _on_connect(self, client, userdata, flags, rc) -> None:
        if rc == 0:
            logger.info("MQTT connected to %s:%d", self._host, self._port)
            with self._lock:
                for topic in self._callbacks:
                    self._client.subscribe(topic)
        else:
            logger.error(
                "MQTT connection to %s:%d failed (rc=%d)", self._host, self._port, rc
            )

    def _on_disconnect(self, client, userdata, rc) -> None:
        if rc != 0:
            logger.warning(
                "MQTT unexpected disconnect from %s:%d (rc=%d); paho will reconnect automatically",
                self._host,
                self._port,
                rc,
            )

    def _on_message(self, client, userdata, message) -> None:
        topic = message.topic
        payload = message.payload.decode("utf-8", errors="replace")
        with self._lock:
            callbacks = list(self._callbacks.get(topic, []))
        for cb in callbacks:
            try:
                cb(payload)
            except Exception:
                logger.exception(
                    "Exception in MQTT subscriber callback for topic '%s'", topic
                )
