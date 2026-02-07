from __future__ import annotations

from typing import Any, Dict

from core.FBContainer import FBContainer
from core.EventBroker import EventBroker


class BaseResource:
    def __init__(self, name: str) -> None:
        self._name = name
        self._container = FBContainer()
        self._broker = EventBroker(self._container)

    @property
    def name(self) -> str:
        return self._name

    @property
    def container(self) -> FBContainer:
        return self._container

    def add_fb(self, fb_instance) -> None:
        self._container.add_fb(fb_instance)
        fb_instance.set_emit_callback(self._emit_event_callback)

    async def _emit_event_callback(self, fb_name: str, event: str, payload: Dict[str, Any] | None) -> None:
        connections = self._broker._event_connections.get((fb_name, event), [])
        for dst_fb, dst_event in connections:
            await self._broker.enqueue(dst_fb, dst_event, payload or {})

    def connect_event(self, src_fb: str, src_event: str, dst_fb: str, dst_event: str = "REQ") -> None:
        self._broker.add_event_connection(src_fb, src_event, dst_fb, dst_event)

    def connect_data(self, src_fb: str, src_output: str, dst_fb: str, dst_input: str) -> None:
        self._broker.add_data_connection(src_fb, src_output, dst_fb, dst_input)

    def set_data(self, fb_name: str, input_name: str, value) -> None:
        fb = self._container.get_fb(fb_name)
        fb.set_input(input_name, value)

    async def enqueue_event(self, fb_name: str, payload: Dict[str, Any] | None = None, event: str = "REQ") -> None:
        payload_map = payload or {}
        await self._broker.enqueue(fb_name, event, payload_map)

    async def start(self) -> None:
        await self._broker.start()

    async def stop(self) -> None:
        await self._broker.stop()
